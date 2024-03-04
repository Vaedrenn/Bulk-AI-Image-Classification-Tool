import sys

from PyQt5.QtWidgets import QApplication

from src.gui.main_widget import MainWidget

if __name__ == '__main__':
    app = QApplication(sys.argv)
    myGUI = MainWidget()
    sys.exit(app.exec_())
