from PyQt5.QtCore import Qt, QSize, QSortFilterProxyModel, QRegularExpression
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QStyleFactory, QPushButton, QLineEdit, \
    QCompleter, QListWidget, QAbstractItemView, QListView, QStyledItemDelegate

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
        self.search_completer = MultiCompleter()

        self.image_gallery = None
        self.action_box = None
        self.filelist = None

        self.initUI()

    def initUI(self):
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        dark_palette = create_dark_palette()
        self.setPalette(dark_palette)
        self.setAutoFillBackground(True)

        # Create Widgets
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

        # Frame 1, Tag list and search
        frame1.setMaximumWidth(400)
        search_box = QWidget()
        search_box.setLayout(QHBoxLayout())
        search_box.layout().setContentsMargins(0, 0, 0, 0)

        self.searchbar.setPlaceholderText("  Search Tags")
        self.searchbar.returnPressed.connect(lambda: self.search_tags(self.searchbar.text()))
        tag_button = QPushButton("Search")
        search_box.layout().addWidget(self.searchbar)
        search_box.layout().addWidget(tag_button)
        tag_button.clicked.connect(lambda: self.search_tags(self.searchbar.text()))

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
        self.image_gallery = QListView()
        delegate = ThumbnailDelegate()
        self.image_gallery.setItemDelegate(delegate)
        self.image_gallery.setModel(self.proxy_model)  # set proxy model for filtering
        self.image_gallery.setViewMode(QListWidget.IconMode)
        self.image_gallery.setAcceptDrops(False)
        self.image_gallery.setSelectionMode(QAbstractItemView.ExtendedSelection)  # ctrl and shift click selection
        self.image_gallery.setIconSize(QSize(400, 200))
        self.image_gallery.setResizeMode(QListWidget.Adjust)  # Reorganize thumbnails on resize

        self.action_box = QWidget()
        self.action_box.setLayout(QVBoxLayout())
        update_btn = QPushButton("Import From Tagger")
        update_btn.clicked.connect(self.get_results)
        self.action_box.layout().addWidget(update_btn)
        frame2.layout().addWidget(self.image_gallery)
        frame2.layout().addWidget(self.action_box)

    def get_results(self):
        """Used to populate file manager, loads tags from tagger and sets the model for displaying images"""

        list_widget = self.tagger.filelist
        if list_widget.count() == 0:
            return

        # Populate tag list
        self.tag_list.clear()
        tag_count = self.tagger.tag_count

        # We want to place rating information at the top of tag list
        ratings = {"rating:safe": 0, "rating:questionable": 0, "rating:explicit": 0}

        # Sort and add excluded items
        for key, value in ratings.items():
            if key in tag_count:
                count = tag_count.pop(key)
                val = f"({count})   {key}"
                self.tag_list.addItem(val)

        # Sort and add remaining items
        for key, value in sorted(tag_count.items(), key=lambda item: item[1], reverse=True):
            if key in tag_count:
                val = f"({value})   {key}"
                self.tag_list.addItem(val)

        # Add ratings back in for the completer
        tag_count.update(ratings)
        self.load_tagger_info()

    def load_tagger_info(self):
        """ Reloads changes from tagger, loads images and tags."""

        self.proxy_model.setSourceModel(self.tagger.results)
        self.search_completer = MultiCompleter(self.tagger.tag_count.keys())
        self.searchbar.setCompleter(self.search_completer)

    def search_tags(self, text: str):
        """
        Alternative to clicking tags, Searches for tags based on text.
        Filtering is based on the text output section of the tagger.
        This is accessed by the TEXT user role ie: item.data(TEXT)
        :parameter text: string of tags to filter by
        """

        if text == "":
            return
        tags = [tag.strip() for tag in text.split(',')]
        regex_pattern = "(?=.*{})".format(")(?=.*".join(tags))  # Regex for selecting things with all tags
        # Create QRegularExpression object
        regex = QRegularExpression(regex_pattern, QRegularExpression.CaseInsensitiveOption)

        self.proxy_model.setFilterRole(TEXT)  # Filter by TEXT role, each item comes with a string of all checked tags
        self.proxy_model.setFilterRegularExpression(regex)  # Apply filter

    def filter_images(self):
        """
        Display images with the following tags.
        Filtering is based on the text output section of the tagger.
        This is accessed by the TEXT user role ie: item.data(TEXT)
        """

        # get all tags and remove (number)
        selected_tags = [
            item.text().split("   ", 1)[1].strip()
            for item in self.tag_list.selectedItems()
        ]
        regex_pattern = "(?=.*{})".format(")(?=.*".join(selected_tags))  # Regex for selecting things with all tags

        # Create QRegularExpression object
        regex = QRegularExpression(regex_pattern, QRegularExpression.CaseInsensitiveOption)

        self.proxy_model.setFilterRole(TEXT)  # Filter by TEXT role, each item comes with a string of all checked tags
        self.proxy_model.setFilterRegularExpression(regex)  # Apply filter


class MultiCompleter(QCompleter):
    """ Multi Tag completer, allows for comma separated tag searching"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaxVisibleItems(5)

    def pathFromIndex(self, index):
        path = super().pathFromIndex(index)

        lst = str(self.widget().text()).split(', ')
        if len(lst) > 1:
            path = ', '.join(lst[:-1]) + ', ' + path

        return path

    def splitPath(self, path):
        return [path.split(',')[-1].strip()]


class ThumbnailDelegate(QStyledItemDelegate):
    """ Custom delegate for displaying images, removes check box and names for better formatting"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.displayRoleEnabled = False

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        # remove checkbox and name area
        if not self.displayRoleEnabled:
            option.features &= ~option.HasDisplay
            option.features &= ~option.HasCheckIndicator


# Custom delegate for displaying larger item with larger text
class TagListItemDelegate(QStyledItemDelegate):
    def sizeHint(self, option, index):
        # Customize the size of items
        return QSize(100, 25)  # Adjust the width and height as needed

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        # Customize the font size of the item text
        option.font.setPointSize(12)  # Adjust the font size as needed
