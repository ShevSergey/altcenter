import re
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
import pexpect
import logging
from PyQt5.QtWidgets import (QWidget, QPushButton, QVBoxLayout,
                            QMessageBox, QLabel, QLineEdit, QHBoxLayout)
from PyQt5.QtGui import QStandardItem
from PyQt5.QtCore import Qt, QTimer
from plugins import Base

ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SuAuthDialog(Gtk.Dialog):
    def __init__(self):
        Gtk.Dialog.__init__(self, "Root Authentication", None, 0)
        self.set_default_size(250, 100)
        self.entry = Gtk.Entry(visibility=False, invisible_char='*')
        box = self.get_content_area()
        box.add(Gtk.Label(label="Root password:"))
        box.add(self.entry)
        self.add_buttons("Cancel", Gtk.ResponseType.CANCEL, "OK", Gtk.ResponseType.OK)
        self.show_all()

    def get_password(self):
        response = self.run()
        password = self.entry.get_text() if response == Gtk.ResponseType.OK else None
        self.destroy()
        return password

class PluginUsers(Base):
    def __init__(self):
        super().__init__("users", 70)
        self.root_session = None
        self.authenticated = False
        Gtk.init([])
        GLib.timeout_add(100, self.gtk_events_poll)

    def gtk_events_poll(self):
        while GLib.MainContext.default().iteration(False): pass
        return True

    def start(self, plist, pane):
        self.node = QStandardItem("Users")
        self.node.setData(self.getName())
        plist.appendRow([self.node])
        self.widget = QWidget()
        layout = QVBoxLayout()
        self.auth_btn = QPushButton("Authenticate")
        self.auth_status = QLabel("Status: Not authenticated", styleSheet="color: red; font-weight: bold;")
        self.username_input = QLineEdit(placeholderText="Username", enabled=False)
        btn_layout = QHBoxLayout()
        for btn in [QPushButton(t) for t in ["Create", "Delete"]]:
            btn.setEnabled(False)
            btn_layout.addWidget(btn)
        self.create_btn, self.delete_btn = btn_layout.itemAt(0).widget(), btn_layout.itemAt(1).widget()
        self.password_input = QLineEdit(placeholderText="Password (optional)")
        self.password_input.setEchoMode(QLineEdit.Password)

        layout.addWidget(self.auth_btn)
        layout.addWidget(self.auth_status)
        layout.addWidget(QLabel("\nUser Operations:"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_input)
        layout.addLayout(btn_layout)
        self.widget.setLayout(layout)
        pane.addWidget(self.widget)

        self.auth_btn.clicked.connect(self.authenticate)
        self.create_btn.clicked.connect(self.create_user)
        self.delete_btn.clicked.connect(self.delete_user)

    def authenticate(self):
        if self.authenticated: return
        dialog = SuAuthDialog()
        if (password := dialog.get_password()) is None: return
        try:
            self.root_session = pexpect.spawn('/bin/su - root', encoding='utf-8', timeout=5)
            self.root_session.expect('Password:')
            self.root_session.sendline(password)
            self.root_session.expect('#', timeout=3)
            self.root_session.sendline("PS1='SU_SESSION#'")
            self.root_session.expect('SU_SESSION#')
            self.authenticated = True
            self.update_ui()
            self.start_session_monitor()
            logger.debug("Authentication successful")
        except Exception as e:
            self.handle_error("Authentication failed: Wrong password!")

    def execute_command(self, command):
        try:
            if not self.authenticated or self.root_session.closed:
                raise Exception("Session expired")

            self.root_session.sendline(f"{command}; echo CMD_EXIT:$?")
            self.root_session.expect_exact('CMD_EXIT:', timeout=10)
            self.root_session.expect('SU_SESSION#', timeout=5)

            # Очистка вывода
            raw_output = self.root_session.before
            cleaned_output = ansi_escape.sub('', raw_output)

            # Парсинг кода возврата
            exit_code = 1
            if 'CMD_EXIT:' in cleaned_output:
                exit_part = cleaned_output.split('CMD_EXIT:')[-1].split('\n')[0].strip()
                exit_code = int(exit_part) if exit_part.isdigit() else 1

            # Извлечение вывода команды
            output = '\n'.join([
                line.strip()
                for line in cleaned_output.split('\n')
                if line.strip() and not line.startswith('SU_SESSION#')
            ][:-1])

            return output.strip(), exit_code

        except Exception as e:
            self.handle_error(f"Command execution error: {str(e)}")
            return None, -1

    def create_user(self):
        if not (username := self.validate_username()): return
        password = self.password_input.text().strip()

        try:
            exists = self.user_exists(username)
            if exists:
                self.handle_error(f"User '{username}' already exists")
                return

            output, code = self.execute_command(f"useradd -m {username}")
            if code != 0 or not self.user_exists(username):
                self.handle_error(f"Creation failed: {output}")
                return

            if password:
                password_escaped = password.replace('"', r'\"')
                cmd = f'echo "{username}:{password_escaped}" | chpasswd'
                pwd_output, pwd_code = self.execute_command(cmd)
                if pwd_code != 0:
                    self.handle_error(f"Password set failed: {pwd_output}")
                    return

            QMessageBox.information(self.widget, "Success", "User created successfully!")

        except Exception as e:
            self.handle_error(f"Error: {str(e)}")

    def delete_user(self):
        if not (username := self.validate_username()): return
        try:
            if not self.user_exists(username):
                self.handle_error(f"User '{username}' not found")
                return

            output, code = self.execute_command(f"userdel -r {username}")
            if code != 0 or self.user_exists(username):
                self.handle_error(f"Deletion failed: {output}")
            else:
                QMessageBox.information(self.widget, "Success", "User deleted!")
        except Exception as e:
            self.handle_error(f"Error: {str(e)}")

    def user_exists(self, username):
        try:
            output, code = self.execute_command(f"getent passwd {username}")
            return code == 0
        except:
            return False

    def validate_username(self):
        username = self.username_input.text().strip()
        if not username:
            self.handle_error("Enter username")
            return None
        if not re.match(r'^[a-z_][a-z0-9_-]*$', username):
            self.handle_error("Invalid username format")
            return None
        return username

    def start_session_monitor(self):
        def monitor():
            if self.authenticated:
                try:
                    self.root_session.sendline("")
                    self.root_session.expect('SU_SESSION#', timeout=1)
                    QTimer.singleShot(5000, monitor)
                except:
                    self.handle_error("Session lost")
        QTimer.singleShot(1000, monitor)

    def handle_error(self, message):
        # logger.error(message)
        QMessageBox.critical(self.widget, "Error", message)
        if self.authenticated and self.root_session and not self.root_session.closed:
            try:
                self.root_session.sendcontrol('c')
                self.root_session.expect('SU_SESSION#', timeout=1)
            except:
                self.root_session.close()
                self.authenticated = False
        self.update_ui()

    def update_ui(self):
        auth = self.authenticated
        self.auth_status.setText(f"Status: {'Authenticated' if auth else 'Not authenticated'}")
        self.auth_status.setStyleSheet(f"color: {'green' if auth else 'red'}; font-weight: bold;")
        self.username_input.setEnabled(auth)
        for btn in [self.create_btn, self.delete_btn]:
            btn.setEnabled(auth)

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication([])
    Gtk.init([])
    plist, pane = QStandardItem(), QWidget()
    PluginUsers().start(plist, pane)
    pane.show()
    QTimer().singleShot(100, lambda: None)
    app.exec_()
