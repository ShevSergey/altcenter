# Application for configure and maintain ALT operating system
# (c) 2024 Andrey Cherepanov <cas@altlinux.org>

# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 3 of the License, or (at your option) any later
# version.

# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.

# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place - Suite 330, Boston, MA  02111-1307, USA.

from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QTranslator
# from PyQt5 import uic
from PyQt5.QtGui import QStandardItemModel

import locale
import os
import sys
from pathlib import Path

current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)
os.chdir(current_dir)

from ui_mainwindow import Ui_MainWindow
from plugins import Base
import my_utils

data_dir = "/usr/share/altcenter"
data_dir = "."

app_name = 'altcenter'

plugin_path = os.path.join(data_dir, "plugins")

class MainWindow(QWidget, Ui_MainWindow):
    """Main window"""

    def __init__(self):
        #super(MainWindow, self).__init__() # Call the inherited classes __init__ method
        super().__init__()
        self.setupUi(self)

        # Load UI from file
        # uic.loadUi("ui_mainwindow.ui", self) # Load the .ui file

        self.splitter.setStretchFactor(0,0)
        self.splitter.setStretchFactor(1,1)

        self.runOnSessionStart.setChecked(not my_utils.is_in_autostart(app_name))
        self.runOnSessionStart.toggled.connect(self.on_checkbox_toggled)

        # Получаем размеры экрана
        screen_geometry = QApplication.desktop().screenGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # Задаем размеры окна
        new_width = screen_width // 3
        new_height = screen_height // 2

        if new_width > self.width()  or  new_height > self.height():
            if new_width < self.width():
                new_width = self.width()

            if new_height < self.height():
                new_height = self.height()

            self.resize(new_width, new_height)


        # Центрируем окно на экране
        self.setGeometry(
            (screen_width - self.width()) // 2,
            (screen_height - self.height()) // 2,
            self.width(), self.height()
        )



    def on_checkbox_toggled(self, checked):
        if checked:
            print("Флажок установлен")
            my_utils.remove_from_autostart(app_name)
        else:
            print("Флажок не установлен")
            my_utils.add_to_autostart(app_name, Path(current_dir) / app_name)


    def onSelectionChange(self, index):
        """Slot for change selection"""
        self.stack.setCurrentIndex(index.row() + 1)


# Run application
app = QApplication(sys.argv) # Create an instance of QtWidgets.QApplication


# Load current locale translation
current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)

translator = QTranslator(app)
tr_file = os.path.join(current_dir, "altcenter_" + locale.getlocale()[0].split( '_' )[0])
# print( "Load translation from %s.qm" % ( tr_file ) )
if translator.load( tr_file ):
    app.installTranslator(translator)


# Initialize UI
window = MainWindow() # Create an instance of our class

# Set module list model
window.list_module = QStandardItemModel()
window.moduleList.setModel(window.list_module)
window.moduleList.selectionModel().currentChanged.connect(window.onSelectionChange)

# Load plugins
for p in Base.plugins:
    inst = p()
    inst.start(window.list_module, window.stack)


window.splitter.setStretchFactor(0,0)
window.splitter.setStretchFactor(1,1)

# Show window
window.show()

# Start the application
sys.exit(app.exec_())
