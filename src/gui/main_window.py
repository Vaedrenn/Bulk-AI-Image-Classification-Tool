import sys

from PyQt5.QtCore import Qt

from src.gui.dark_palette import create_dark_palette
from src.gui.main_widget import MainWidget
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QAction


FILE_PATH = Qt.UserRole
RATING = Qt.UserRole + 1
CHARACTER_RESULTS = Qt.UserRole + 2
GENERAL_RESULTS = Qt.UserRole + 3
TEXT = Qt.UserRole + 4
TAG_STATE = Qt.UserRole + 5


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create a QTabWidget
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        self.setPalette(create_dark_palette())
        self.tab_widget.setPalette(create_dark_palette())
        # Create tabs (widgets)
        self.tab1 = MainWidget()
        self.tab2 = QWidget()

        # Add tabs to the QTabWidget
        self.tab_widget.addTab(self.tab1, "Main")
        self.tab_widget.addTab(self.tab2, "File Manager")



if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MyWindow()
    window.setGeometry(100, 100, 1200, 800)
    window.setWindowTitle("Bulk AI Image Classification Tool")
    window.show()
    sys.exit(app.exec_())
