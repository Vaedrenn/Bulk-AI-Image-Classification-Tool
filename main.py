import multiprocessing
import sys

from PyQt5.QtWidgets import QApplication

from src.gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setGeometry(100, 100, 1200, 800)
    window.setWindowTitle("Bulk AI Image Classification Tool")
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()

