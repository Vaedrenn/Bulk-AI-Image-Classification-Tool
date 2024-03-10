from PyQt5.QtCore import Qt, QSize, QSortFilterProxyModel, QRegularExpression
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QStyleFactory, QPushButton, QLineEdit, \
    QCompleter, QListWidget, QLabel, QAbstractItemView, QListView, QStyledItemDelegate

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

        self.searchbar = QLineEdit()
        self.tag_list = QListWidget()
        self.proxy_model = QSortFilterProxyModel()
        self.search_completer = QCompleter()

        self.item_menu = None
        self.action_box = None
        self.filelist = None

        self.images = []

        self.initUI()

    def initUI(self):
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        dark_palette = create_dark_palette()
        self.setPalette(dark_palette)
        self.setAutoFillBackground(True)

        # Create labels
        frame1 = QWidget()
        frame2 = QWidget()

        # Create layout
        main_layout = QHBoxLayout()

        main_layout.addWidget(frame1)
        main_layout.addWidget(frame2)

        # Set main window layout
        self.setLayout(main_layout)
        frame1.setLayout(QVBoxLayout())
        frame2.setLayout(QVBoxLayout())

        # Frame 1
        frame1.setMaximumWidth(400)
        search_box = QWidget()
        search_box.setLayout(QHBoxLayout())
        search_box.layout().setContentsMargins(0, 0, 0, 0)

        self.searchbar.setPlaceholderText("  Search Tags")
        tag_button = QPushButton("Search")
        search_box.layout().addWidget(self.searchbar)
        search_box.layout().addWidget(tag_button)

        self.tag_list.setSelectionMode(QListWidget.MultiSelection)  # Toggle style selection
        self.tag_list.itemClicked.connect(self.filter_images)  # on click filter
        self.tag_list.setAcceptDrops(False)
        tl_delegate = TagListItemDelegate()
        self.tag_list.setItemDelegate(tl_delegate)

        deselect_all = QPushButton("Deselect All")
        deselect_all.clicked.connect(self.tag_list.clearSelection)

        frame1.layout().addWidget(search_box)
        frame1.layout().addWidget(self.tag_list)
        frame1.layout().addWidget(deselect_all)

        # Frame 2

        self.item_menu = QListView()
        delegate = ThumbnailDelegate()
        self.item_menu.setItemDelegate(delegate)
        self.item_menu.setModel(self.proxy_model)
        self.item_menu.setViewMode(QListWidget.IconMode)
        self.item_menu.setAcceptDrops(False)
        self.item_menu.setSelectionMode(QAbstractItemView.ExtendedSelection)  # Allows ctrl and  shift click selection
        self.item_menu.setIconSize(QSize(400, 200))
        self.item_menu.setResizeMode(QListWidget.Adjust)  # Reorganize thumbnails on resize

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

        excluded_items = {"rating:safe": 0, "rating:questionable": 0, "rating:explicit": 0}
        for i in excluded_items:
            if i in tag_count.keys():
                count = tag_count.pop(i)
                val = '(' + str(count) + ')   ' + str(i)
                self.tag_list.addItem(val)

        sorted_items = sorted(tag_count.items(), key=lambda item: item[1], reverse=True)
        for key, value in sorted_items:
            val = '(' + str(value) + ')   ' + str(key)
            self.tag_list.addItem(val)

        self.load_tagger_info()

        return

    # Reloads changes from tagger, loads images and tags.
    def load_tagger_info(self):
        self.proxy_model.setSourceModel(self.tagger.results)
        self.search_completer = QCompleter(self.tagger.labels)
        self.searchbar.setCompleter(self.search_completer)

    def search_tags(self, text):

        pass

    # Display images with the following tags.
    def filter_images(self):
        # get all tags and remove (number)
        selected_tags = [
            item.text().split("   ", 1)[1].strip()
            for item in self.tag_list.selectedItems()
        ]
        regex_pattern = "(?=.*{})".format(")(?=.*".join(selected_tags))  # Regex for selecting things with all tags

        # Create QRegularExpression object
        regex = QRegularExpression(regex_pattern, QRegularExpression.CaseInsensitiveOption)

        self.proxy_model.setFilterRole(TEXT)
        self.proxy_model.setFilterRegularExpression(regex)


class ThumbnailDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.displayRoleEnabled = False

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        if not self.displayRoleEnabled:
            option.features &= ~option.HasDisplay
            option.features &= ~option.HasCheckIndicator


class TagListItemDelegate(QStyledItemDelegate):
    def sizeHint(self, option, index):
        # Customize the size of items
        return QSize(100, 25)  # Adjust the width and height as needed

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        # Customize the font size of the item text
        option.font.setPointSize(12)  # Adjust the font size as needed
