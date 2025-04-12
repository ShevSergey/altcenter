#!/usr/bin/python3

import plugins
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton,
                            QScrollArea, QTextBrowser, QInputDialog,
                            QMessageBox, QLineEdit, QApplication, QLabel, QHBoxLayout)
from PyQt5.QtGui import QStandardItem
from PyQt5.QtCore import QObject, Qt
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
import subprocess
import webbrowser

import my_utils


class GetSystemInfo(QObject):
    def __init__(self):
        super().__init__()

    def get_system_info(self) -> str:

        # Получаем информацию о системе через inxi -F
        try:
            system_info = subprocess.check_output(
                "inxi -F -c -y -1",
                shell=True,
                text=True
            )
            # Очищаем от специальных символов
            # system_info = re.sub(r'', '', system_info)
            # system_info = re.sub(r'12', '', system_info)

            # Расширенный список терминов для разделителей
            separators = [
                'System:',
                'Machine:',
                'Battery:',
                'CPU:',
                'Graphics:',
                'Audio:',
                'Network:',
                'Bluetooth:',
                'Drives:',
                'Partition:',
                'Swap:',
                'Sensors:',
                'Info:',
            ]

            info = system_info.split('\n')

            # Добавляем белую разделительную линию
            for separator in separators:
                sep_len = len(separator)
                for key, value in enumerate(info):
                    # print(key, "    ", value)
                    if value[0:sep_len] == separator:
                        s = '<hr style="border: 1px solid #000000; margin: 10px 0;">' + separator
                        info.insert(key, s)
                        # print(value)
                        info[key+1] = ' ' * sep_len + value[sep_len:]
                        # print(info[key])
                        break


            # Словари переводов для разных языков
            translations = {
                # Special terms
                'System Temperatures:': self.tr('<b>System Temperatures:</b>'),
                'Fan Speeds (rpm):': self.tr('<b>Fan Speeds (rpm):</b>'),
                'N/A': self.tr('N/A'),

                # Headers with HTML formatting
                'System:': self.tr('<b>System:</b>'),
                'Kernel:': self.tr('<b>Kernel:</b>'),
                'Desktop:': self.tr('<b>Desktop:</b>'),
                'CPU:': self.tr('<b>CPU:</b>'),
                'GPU:': self.tr('<b>GPU:</b>'),
                'Memory:': self.tr('<b>Memory:</b>'),
                'Drives:': self.tr('<b>Drives:</b>'),
                'Network:': self.tr('<b>Network:</b>'),
                'Info:': self.tr('<b>Info:</b>'),
                'Machine:': self.tr('<b>Machine:</b>'),
                'Battery:': self.tr('<b>Battery:</b>'),
                'Processes:': self.tr('<b>Processes:</b>'),
                'Audio:': self.tr('<b>Audio:</b>'),
                'Sensors:': self.tr('<b>Sensors:</b>'),
                'Graphics:': self.tr('<b>Graphics:</b>'),
                'Display:': self.tr('<b>Display:</b>'),
                'Bluetooth:': self.tr('<b>Bluetooth:</b>'),

                # Common terms with colon and formatting
                'speed:': self.tr('<b>speed:</b>'),
                'type:': self.tr('<b>type:</b>'),
                'size:': self.tr('<b>size:</b>'),
                'used:': self.tr('<b>Used:</b>'),
                'serial:': self.tr('<b>serial:</b>'),
                'driver:': self.tr('<b>driver:</b>'),
                'drivers:': self.tr('<b>drivers:</b>'),
                'version:': self.tr('<b>version:</b>'),
                'model:': self.tr('<b>model:</b>'),
                'device:': self.tr('<b>device:</b>'),
                'vendor:': self.tr('<b>vendor:</b>'),
                'partition:': self.tr('<b>Partition:</b>'),
                'swap:': self.tr('<b>Swap File:</b>'),

                # The same terms with capital letters
                'Type:': self.tr('<b>Type:</b>'),
                # 'Size:': self.tr('<b>Size:</b>'),
                'Used:': self.tr('<b>Used:</b>'),
                # 'Serial:': self.tr('<b>Serial Number:</b>'),
                'Version:': self.tr('<b>Version:</b>'),
                'Model:': self.tr('<b>Model:</b>'),
                'Device:': self.tr('<b>Device:</b>'),
                'Vendor:': self.tr('<b>Vendor:</b>'),
                'Partition:': self.tr('<b>Partition:</b>'),
                'Swap:': self.tr('<b>Swap:</b>'),

                # Common terms without formatting
                'menu': self.tr('Hardware'),
                'title': self.tr('Hardware Information'),
                'System': self.tr('System'),
                'Kernel': self.tr('Kernel'),
                'Desktop': self.tr('Desktop'),
                'Laptop': self.tr('Laptop'),
                'type': self.tr('Type'),
                'model': self.tr('Model'),
                # 'serial': self.tr('Serial Number'),
                'product:': self.tr('<b>product:</b>'),
                'charge:': self.tr('<b>charge:</b>'),
                'condition:': self.tr('<b>condition:</b>'),
                'core:': self.tr('<b>Core:</b>'),
                'cores:': self.tr('<b>Cores:</b>'),
                'cache': self.tr('Cache'),
                'avg:': self.tr('<b>Average:</b>'),
                'server:': self.tr('<b>server:</b>'),
                ' loaded:': self.tr('<b> Loaded:</b>'),
                'unloaded:': self.tr('<b>Unloaded</b>'),
                'resolution:': self.tr('<b>resolution:</b>'),
                'platforms:': self.tr('<b>platforms:</b>'),
                'renderer': self.tr('<b>renderer:</b>'),
                'surfaces': self.tr('<b>surfaces:</b>'),
                'state:': self.tr('<b>state:</b>'),
                'status:': self.tr('<b>status:</b>'),
                'active': self.tr('Active'),
                'with': self.tr('With'),
                'compositor': self.tr('Compositor'),
                'arch:': self.tr('<b>Architecture:</b>'),
                'bits:': self.tr('<b>Bits:</b>'),
                'Report:': self.tr('<b>Report:</b>'),
                'address:': self.tr('<b>address:</b>'),
                'bt-v:': self.tr('<b>bt-v:</b>'),
                'cpu:': self.tr('<b>cpu:</b>'),
                'mobo:': self.tr('<b>mobo:</b>'),

                ' ID:': ' <b>ID:</b>',
                'ID-1:': '<b>ID-1:</b>',
                'ID-2:': '<b>ID-2:</b>',
                'ID-3:': '<b>ID-3:</b>',
                'ID-4:': '<b>ID-4:</b>',
                'ID-5:': '<b>ID-5:</b>',
                'ID-6:': '<b>ID-6:</b>',
                'ID-7:': '<b>ID-7:</b>',
                'ID-8:': '<b>ID-8:</b>',

                'Device-1': '<b>Device-1</b>',
                'Device-2': '<b>Device-2</b>',
                'Device-3': '<b>Device-3</b>',
                'Device-4': '<b>Device-4</b>',

                'Server-1': '<b>Server-1</b>',
                'Server-2': '<b>Server-2</b>',
                'Server-3': '<b>Server-3</b>',
                'Server-4': '<b>Server-4</b>',

                'fan-1:': '<b>fan-1:</b>',
                'fan-2:': '<b>fan-2:</b>',
                'fan-3:': '<b>fan-3:</b>',
                'fan-4:': '<b>fan-4:</b>',
                'fan-5:': '<b>fan-5:</b>',
                'fan-6:': '<b>fan-6:</b>',

                ' v:': self.tr(' <b>v:</b>'),
                'compat-v:': self.tr('<b>compat-v:</b>'),
                'Distro:': self.tr('<b>Distro:</b>'),
                'Alert:': self.tr('<b>Alert:</b>'),
                'Mobo:': self.tr('<b>Mobo:</b>'),
                'date:': self.tr('<b>date:</b>'),
                'dri:': '<b>dri:</b>',
                'gpu:': '<b>gpu:</b>',
                'Speed (MHz):': self.tr('<b>Speed (MHz):</b>'),
                'min/max:': self.tr('<b>min/max:</b>'),
                'Local Storage:': self.tr('<b>Local Storage:</b>'),
                'total:': self.tr('<b>total:</b>'),
                'note:': self.tr('<b>note:</b>'),
                ' est.': self.tr(' est.'),
                'available:': self.tr('<b>available:</b>'),
                'fs:': self.tr('<b>fs:</b>'),
                'dev:': self.tr('<b>dev:</b>'),
                'Uptime:': self.tr('<b>Uptime:</b>'),
                'Client:': self.tr('<b>Client:</b>'),
                'Tools:': self.tr('<b>Tools:</b>'),
                'api:': '<b>api:</b>',
                'de:': '<b>de:</b>',
                'x11:': '<b>x11:</b>',

                'Host:': '<b>Host:</b>',
                'BIOS:': '<b>BIOS:</b>',
                'UEFI:': '<b>UEFI:</b>',
                'API:': '<b>API:</b>',
                'IF:': '<b>IF:</b>',
                'mac:': '<b>mac:</b>',
                'Shell:': '<b>Shell:</b>',
                'inxi:': '<b>inxi:</b>',

                # Units of measurement
                'KiB': self.tr('KiB'),
                'GiB': self.tr('GiB'),
                'MiB': self.tr('MiB'),
                'MHz': self.tr('MHz'),
                'Wh': self.tr('Wh'),

                'min': self.tr('Min'),
                'max': self.tr('Max'),
                ' up ': self.tr(' up '),
                ' down ': self.tr(' down '),

                'No swap data was found': self.tr('No swap data was found'),
            }

            # core numbers
            for i in range(1,33):
                key = f' {i}: '
                value = f' <b>{i}:</b> '
                # print(f'{key=}', '  ', f'{value=}')
                translations[key] = value


            # Заменяем термины на переведенные версии
            for key, value in enumerate(info):
                # print(key, "    ", value)
                # print(value)
                # if value in separators:
                #     info[key] = '<hr style="border: 1px solid #000000; margin: 10px 0;">' + value
                #     print(info[key])
                for eng, translated in translations.items():
                    value = value.replace(eng, translated)
                info[key] = value
                # print(info[key])

            # Форматируем вывод для HTML
            system_info = "<h3>" + self.tr("Hardware Information") + "</h3>"
            system_info = system_info + "<p>" + "</p><p>".join(info) + "</p>"

        except Exception as e:
            s = self.tr('Error getting system information')
            system_info = f"<p>{s}: {e}</p>"

        return system_info


# class QtPasswordDialog(QDialog):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.setWindowTitle("Sudo Authentication")
#         self.setModal(True)
#
#         layout = QVBoxLayout(self)
#
#         self.label = QLabel("Enter sudo password:")
#         self.entry = QLineEdit()
#         self.entry.setEchoMode(QLineEdit.Password)
#
#         self.buttons = QDialogButtonBox(
#             QDialogButtonBox.Ok | QDialogButtonBox.Cancel
#         )
#         self.buttons.accepted.connect(self.accept)
#         self.buttons.rejected.connect(self.reject)
#
#         layout.addWidget(self.label)
#         layout.addWidget(self.entry)
#         layout.addWidget(self.buttons)
#
#     def get_password(self):
#         if self.exec_() == QDialog.Accepted:
#             return self.entry.text()
#         return None


class BrowserThread(QThread):
    # Сигнал для запуска браузера
    open_browser_signal = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        # Ожидаем сигнал для открытия браузера
        webbrowser.open(self.url)


class HardwareWindow(QWidget):
    def __init__(self, palette = None):
        super().__init__()

        if palette != None:
            self.setPalette(palette)
            pass

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)


        if self.is_enabled_hw_probe():
            top_panel = QWidget()
            top_layout = QHBoxLayout(top_panel)
            top_layout.setContentsMargins(15, 10, 15, 10)

            btn = QPushButton(self.tr("Upload Hardware Probe"))
            btn.setStyleSheet("""
                QPushButton {
                    padding: 5px 15px;  /* Отступы сверху/снизу и слева/справа */
                }
            """)
            btn.clicked.connect(self.authenticate)
            top_layout.addWidget(btn, 0, Qt.AlignLeft)

            self.link_label = QLabel()
            self.link_label.setAlignment(Qt.AlignRight)
            self.link_label.setTextFormat(Qt.RichText)
            self.link_label.setOpenExternalLinks(True)
            # self.link_label.setText('https://www.basealt.ru/dhsuhgfuseuiuighwuiheiuhwuighuihu')
            self.link_label.setStyleSheet('color: blue; text-decoration: underline; padding: 5px 10px;')
            top_layout.addWidget(self.link_label)
            self.link_label.mousePressEvent = self.on_label_click

            layout.addWidget(top_panel)


        # Основной текст
        self.text_browser = QTextBrowser()
        gsi = GetSystemInfo()
        self.text_browser.setHtml(gsi.get_system_info())

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.text_browser)
        layout.addWidget(scroll)

        self.setLayout(layout)
        # self.setMinimumSize(600,800)

        self.browser_thread = None


    def on_label_click(self, event):
        # if self.browser_thread is None or not self.browser_thread.isRunning():
        if self.link_label.text().startswith('http'):
            self.browser_thread = BrowserThread(self.link_label.text())
            # self.browser_thread.open_browser_signal.connect(self.open_browser)
            self.browser_thread.start()


    # def open_browser(self, url):
    #     webbrowser.open(url)


    def is_enabled_hw_probe(self) -> bool:
        return my_utils.check_polkit_enabled()  and  my_utils.check_package_installed('hw-probe')
        # return True
        # return False


    # @pyqtSlot()
    # def authenticate1(self):
    #     print("Метод authenticate вызван!")


    @pyqtSlot()
    def authenticate(self):
        # password, ok = QInputDialog.getText(None, 'Sudo Authentication', 'Enter sudo password:', QLineEdit.Password)
        #
        # if not ok or password == '':
        #     return

        # print(f"Пользователь ввёл пароль: {password}")

        try:
            # Проверка наличия пакета
            # check_installed = subprocess.run(
            #     ['rpm', '-q', 'hw-probe'],
            #     capture_output=True,
            #     text=True
            # )

            # Если пакет не установлен - устанавливаем
            # if check_installed.returncode != 0:
            #     subprocess.run(
            #         ['sudo', '-S', 'apt-get', 'install', '-y', 'hw-probe'],
            #         input=f"{password}\n",
            #         capture_output=True,
            #         text=True,
            #         check=True
            #     )

            # Запуск проверки оборудования
            # result = subprocess.run(
            #     # 'sudo -E hw-probe -all',
            #     ['sudo', '-S', '-k', 'hw-probe', '-all', '-upload'],
            #     input=f"{password}\n",
            #     capture_output=True,
            #     text=True,
            #     check=True
            # )

            # Запуск hw-probe с правами root через pkexec
            result = subprocess.run(
                ['pkexec', 'hw-probe', '-all', '-upload'],
                check=True,
                text=True,
                capture_output=True
            )
            # print(result.stdout)

            # Получение ссылки
            if 'Probe URL:' in result.stdout:
                url = result.stdout.split('Probe URL:')[1].strip()
                new_link = f'<a href="{url}">{url}</a>'
                self.link_label.setText(new_link)
            else:
                QMessageBox.critical(
                    None,
                    self.tr("Error"),
                    self.tr("Failed to get probe link\nPlease try again later")
                )

        except Exception as e:
            error_msg = self.tr("Unknown error")
            if isinstance(e, subprocess.CalledProcessError):
                error_msg = e.stderr.strip() or error_msg

            QMessageBox.critical(
                None,
                self.tr("Error"),
                f"{self.tr('Error occurred')}:\n{error_msg}"
            )


class PluginHardware(plugins.Base, QWidget):
    def __init__(self):
        super().__init__("hardware", 30)
        # os.environ["QT_XKB_CONFIG_ROOT"] = "/usr/share/X11/xkb"

        # Инициализируем QApplication с нужными параметрами
        # self.app = QApplication.instance() or QApplication([])
        self.node = None
        self.link_label = None
        self.text_browser = None


    def start(self, plist, pane):
        self.node = QStandardItem(self.tr("Hardware"))
        self.node.setData(self.getName())
        plist.appendRow([self.node])

        main_palette = pane.window().palette()
        main_widget = HardwareWindow(main_palette)

        pane.addWidget(main_widget)

    # @pyqtSlot()
    # def authenticate(self):
    #     print("call authenticate()")

    # def authenticate1(self):
    #     dialog = QtPasswordDialog()
    #     password = dialog.get_password()
    #
    #     if not password:
    #         return
    #
    #     try:
    #         # Проверка наличия пакета
    #         check_installed = subprocess.run(
    #             ['rpm', '-q', 'hw-probe'],
    #             capture_output=True,
    #             text=True
    #         )
    #
    #         # Если пакет не установлен - устанавливаем
    #         if check_installed.returncode != 0:
    #             subprocess.run(
    #                 ['sudo', '-S', 'apt-get', 'install', '-y', 'hw-probe'],
    #                 input=f"{password}\n",
    #                 capture_output=True,
    #                 text=True,
    #                 check=True
    #             )
    #
    #         # Запуск проверки оборудования
    #         result = subprocess.run(
    #             ['sudo', '-E', 'hw-probe', '-all', '-upload'],
    #             input=f"{password}\n",
    #             capture_output=True,
    #             text=True,
    #             check=True
    #         )
    #
    #         # Получение ссылки
    #         if 'Probe URL:' in result.stdout:
    #             url = result.stdout.split('Probe URL:')[1].strip()
    #             new_link = f'<a href="{url}">{url}</a><br>'
    #             current_text = self.link_label.text()
    #             self.link_label.setText(new_link + current_text)
    #         else:
    #             QMessageBox.critical(
    #                 None,
    #                 self.tr("Error"),
    #                 self.tr("Failed to get probe link\nPlease try again later")
    #             )
    #
    #     except Exception as e:
    #         error_msg = self.tr("Unknown error")
    #         # if isinstance(e, subprocess.CalledProcessError):
    #         #     error_msg = e.stderr.strip() or error_msg
    #
    #         QMessageBox.critical(
    #             None,
    #             self.tr("Error"),
    #             f"{self.tr('Error occurred')}:\n{error_msg}"
    #         )



if __name__ == '__main__':
    app = QApplication([])
    window = HardwareWindow()
    window.show()
    app.exec_()
