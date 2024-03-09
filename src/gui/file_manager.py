import sys

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QStyleFactory, QPushButton, QLineEdit, \
    QCompleter, QListWidget, QListWidgetItem, QLabel

from src.gui.CheckListWidget import CheckListWidget
from src.gui.dark_palette import create_dark_palette

FILE_PATH = Qt.UserRole
RATING = Qt.UserRole + 1
CHARACTER_RESULTS = Qt.UserRole + 2
GENERAL_RESULTS = Qt.UserRole + 3
TEXT = Qt.UserRole + 4
TAG_STATE = Qt.UserRole + 5


class FileManager(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.tagger = parent

        self.item_menu = None
        self.action_box = None
        self.filelist = None

        self.initUI()

    def initUI(self):
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        dark_palette = create_dark_palette()
        self.setPalette(dark_palette)
        self.setAutoFillBackground(True)

        # Create labels
        frame1 = QWidget()
        frame2 = QWidget()
        # frame3 = QWidget()

        # Create layout
        main_layout = QHBoxLayout()

        main_layout.addWidget(frame1)
        main_layout.addWidget(frame2)
        # main_layout.addWidget(frame3)

        # Set main window layout
        self.setLayout(main_layout)
        frame1.setLayout(QVBoxLayout())
        frame2.setLayout(QVBoxLayout())
        # frame3.setLayout(QVBoxLayout())

        # Frame 1
        search_box = QWidget()
        search_box.setLayout(QHBoxLayout())
        search_box.layout().setContentsMargins(0, 0, 0, 0)

        self.s_lineedit = QLineEdit()
        self.s_lineedit.setPlaceholderText("  Search Tags")
        t_button = QPushButton("Search")

        self.s_completer = QCompleter(self.tagger.labels)
        self.s_lineedit.setCompleter(self.s_completer)
        self.s_lineedit.returnPressed.connect(lambda: self.add_tags(self.s_lineedit.text()))
        t_button.clicked.connect(lambda: self.add_tags(self.s_lineedit.text()))

        search_box.layout().addWidget(self.s_lineedit)
        search_box.layout().addWidget(t_button)

        self.tag_list = CheckListWidget()
        deselect_all = QPushButton("Deselect All")
        self.tag_list.itemClicked.connect(self.update_page)  # on click filter

        deselect_all.clicked.connect(self.clear_all_files)

        frame1.layout().addWidget(search_box)
        frame1.layout().addWidget(self.tag_list)
        frame1.layout().addWidget(deselect_all)

        # Frame 2
        self.item_menu = QListWidget()
        self.item_menu.setViewMode(QListWidget.IconMode)
        self.item_menu.setIconSize(QSize(200,200))
        self.item_menu.setBatchSize(50)

        self.action_box = QWidget()
        self.action_box.setLayout(QVBoxLayout())
        update_btn = QPushButton("Import From Tagger")
        update_btn.clicked.connect(self.get_results)
        self.action_box.layout().addWidget(update_btn)
        frame2.layout().addWidget(self.item_menu)
        frame2.layout().addWidget(self.action_box)

    # used to populate file manager
    def get_results(self):
        list_widget = self.tagger.filelist
        if list_widget.count() == 0:
            return
        # populate tag list
        self.tag_list.clear()
        tag_count = self.tagger.tag_count
        sorted_dict = dict(sorted(tag_count.items(), key=lambda item: item[1], reverse=True))
        for i in sorted_dict:
            val = '(' + str(sorted_dict[i]) + ')   ' + str(i)
            self.tag_list.addItem(val)

        # load "thumbnails"
        # for i in range(list_widget.count()):
        #     item = list_widget.item(i)
        #     if item is not None:  # Ensure the item is not None
        #         list_item = QListWidgetItem(item.data(FILE_PATH))
        #         self.item_menu.addItem(list_item)
        self.load_images()

        return

    def update_page(self):
        pass

    def clear_all_files(self):
        self.tag_list.uncheck_all()

    def load_images(self):
        model = self.tagger.results  # get the model in tagger
        for row in range(model.rowCount()):
            index = model.index(row, 0)  # Create index for each row and column 0
            img_path = model.data(index, Qt.UserRole)  # Get the data associated with the index

            pixmap = QPixmap(img_path).scaledToWidth(200, Qt.FastTransformation)
            icon = QIcon(pixmap)

            item = QListWidgetItem(icon, "")
            self.item_menu.addItem(item)

    def filter_images(self):
        selected_tags = [
            item.text().split("   ", 1)[1].strip()
            for item in self.tag_list.selectedItems()
        ]

        if not selected_tags:
            self.scroll_widget.show()
        else:
            for i in reversed(range(self.thumbnail_layout.count())):
                self.thumbnail_layout.itemAt(i).widget().setParent(None)
            for img_info in self.images:
                if all(tag in img_info["tags"] for tag in selected_tags):
                    pixmap = QPixmap(img_info["path"])
                    label = QLabel()
                    label.setPixmap(pixmap.scaledToWidth(200))
                    self.thumbnail_layout.addWidget(label)
