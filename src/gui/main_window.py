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


class MyWindow(QMainWindow):
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



if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MyWindow()
    window.setGeometry(100, 100, 1200, 800)
    window.setWindowTitle("Bulk AI Image Classification Tool")
    window.show()
    directory_path = r"models/deepdanbooru-v3-20211112-sgd-e28"
    directory = r"tests/images"
    from src.commands import load_actions
    window.tab1.model = load_actions.load_model(directory_path)
    window.tab1.labels = load_actions.load_labels(directory_path)
    window.tab1.char_labels = load_actions.load_char_labels(directory_path)
    while window.tab1.model is None:
        pass
    window.tab1.action_box.submit(directory, 50, 85)
    sys.exit(app.exec_())
