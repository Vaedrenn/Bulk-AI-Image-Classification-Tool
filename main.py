import multiprocessing
import sys

from PyQt5.QtWidgets import QApplication

from src.gui.main_widget import MainWidget

def main():
    app = QApplication(sys.argv)
    myGUI = MainWidget()

    sys.exit(app.exec_())

if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
