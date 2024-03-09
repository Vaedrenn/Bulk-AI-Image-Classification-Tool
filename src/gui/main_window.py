import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget


from src.gui.dark_palette import create_dark_palette
from src.gui.image_tagger import ImageTagger
from src.gui.file_manager import FileManager

FILE_PATH = Qt.UserRole
RATING = Qt.UserRole + 1
CHARACTER_RESULTS = Qt.UserRole + 2
GENERAL_RESULTS = Qt.UserRole + 3
TEXT = Qt.UserRole + 4
TAG_STATE = Qt.UserRole + 5


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create a QTabWidget
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        self.setPalette(create_dark_palette())
        self.tab_widget.setPalette(create_dark_palette())
        # Create tabs (widgets)
        self.tab1 = ImageTagger()
        self.tab2 = FileManager(self.tab1)

        # Add tabs to the QTabWidget
        self.tab_widget.addTab(self.tab1, "Main")
        self.tab_widget.addTab(self.tab2, "File Manager")
