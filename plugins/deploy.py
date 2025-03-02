import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
import pexpect
from PyQt5.QtWidgets import (QWidget, QVBoxLayout,
                            QPushButton, QLabel, QMessageBox)
from PyQt5.QtGui import QStandardItem
from PyQt5.QtCore import QTimer
import plugins

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

class PluginDeployAuth(plugins.Base):
    def __init__(self):
        super().__init__("deploy", 15)
        self.node = None
        self.root_session = None
        self.authenticated = False
        Gtk.init([])
        GLib.timeout_add(100, self.gtk_events_poll)

    def gtk_events_poll(self):
        while GLib.MainContext.default().iteration(False): pass
        return True

    def start(self, plist, pane):
        self.node = QStandardItem(self.tr("Deploy"))
        self.node.setData(self.getName())
        plist.appendRow([self.node])

        container = QWidget()
        layout = QVBoxLayout(container)

        self.auth_btn = QPushButton("Authenticate as Root")
        self.auth_status = QLabel("Status: Not authenticated")

        layout.addWidget(self.auth_btn)
        layout.addWidget(self.auth_status)

        container.setLayout(layout)
        pane.addWidget(container)

        self.auth_btn.clicked.connect(self.authenticate)
        self.update_ui()

    def authenticate(self):
        if self.authenticated:
            return

        dialog = SuAuthDialog()
        if (password := dialog.get_password()) is None:
            return

        try:
            self.root_session = pexpect.spawn('/bin/su - root', encoding='utf-8')
            self.root_session.expect('Password:')
            self.root_session.sendline(password)
            self.root_session.expect('#')
            self.root_session.sendline("PS1='SU_SESSION#'")
            self.root_session.expect('SU_SESSION#')
            self.authenticated = True
            self.update_ui()
            self.start_session_monitor()
        except:
            self.handle_error("Authentication failed: Wrong password!")

    def handle_error(self, message):
        QMessageBox.critical(None, "Error", message)
        if self.authenticated and self.root_session and not self.root_session.closed:
            try:
                self.root_session.sendcontrol('c')
                self.root_session.expect('SU_SESSION#')
            except:
                self.root_session.close()
                self.authenticated = False
        self.update_ui()

    def start_session_monitor(self):
        def monitor():
            if self.authenticated:
                try:
                    self.root_session.sendline("")
                    self.root_session.expect('SU_SESSION#')
                    QTimer.singleShot(1000, monitor)
                except:
                    self.handle_error("Session lost")
        monitor()

    def update_ui(self):
        auth = self.authenticated
        self.auth_status.setText(f"Status: {'Authenticated' if auth else 'Not authenticated'}")

    def stop(self):
        if self.root_session and not self.root_session.closed:
            self.root_session.close()
        self.authenticated = False
        self.update_ui()
