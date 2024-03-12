from PyQt5.QtCore import Qt, QSize, QSortFilterProxyModel, QRegularExpression
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QStyleFactory, QPushButton, QLineEdit, \
    QCompleter, QListWidget, QAbstractItemView, QListView, QStyledItemDelegate, QTextEdit, QGridLayout, QFileDialog, \
    QGroupBox

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

        self.file_name = QLineEdit()
        self.file_tags = QTextEdit()
        self.info_widget = QGroupBox()

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
        self.image_gallery.clicked.connect(self.display_info)
        # Action Box
        self.action_box = QGroupBox()
        self.action_box.setLayout(QHBoxLayout())
        self.action_box.setMaximumHeight(300)
        self.action_box.setContentsMargins(0, 0, 0, 0)

        # info_widget: This is where file information will go
        self.info_widget.setLayout(QVBoxLayout())
        self.file_name.setPlaceholderText("File Name")
        self.file_name.setReadOnly(True)
        self.file_tags.setPlaceholderText("Tags")
        self.file_tags.setReadOnly(True)
        self.info_widget.layout().addWidget(self.file_name)
        self.info_widget.layout().addWidget(self.file_tags)

        self.fms_widget = QGroupBox()
        self.fms_widget.setLayout(QGridLayout())

        self.search_wigdet = QGroupBox()
        self.search_wigdet.setLayout(QHBoxLayout())
        self.target_dir = QLineEdit()
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(lambda: self.browse_directory(self.target_dir))
        self.search_wigdet.layout().addWidget(self.target_dir)
        self.search_wigdet.layout().addWidget(self.browse_btn)

        self.button_box = QGroupBox()
        self.button_box.setLayout(QHBoxLayout())
        self.move_btn = QPushButton("Move Selected")
        self.slt_all = QPushButton("Select All")
        self.clr_all = QPushButton("Clear Selected")
        self.move_btn.clicked.connect(lambda: self.move_selected(self.image_gallery.selectedIndexes()))
        self.slt_all.clicked.connect(lambda: self.image_gallery.selectAll())
        self.clr_all.clicked.connect(lambda: self.image_gallery.clearSelection())
        update_btn = QPushButton("Import From Tagger")
        update_btn.clicked.connect(self.get_results)
        self.button_box.layout().addWidget(self.move_btn)
        self.button_box.layout().addWidget(self.slt_all)
        self.button_box.layout().addWidget(self.clr_all)
        self.button_box.layout().addWidget(update_btn)

        self.fms_widget.layout().addWidget(self.search_wigdet)
        self.fms_widget.layout().addWidget(self.button_box)

        self.action_box.layout().addWidget(self.info_widget)
        self.action_box.layout().addWidget(self.fms_widget)

        frame2.layout().addWidget(self.image_gallery)
        frame2.layout().addWidget(self.action_box)

    def browse_directory(self, line_edit):
        """
        looks for the target directory where images are to be tagged
        :parameter line_edit: QLineEdit where text will be displayed
        :return directory_path: abs path of the directory
        """

        directory_path = QFileDialog.getExistingDirectory(None, "Select Directory")
        if directory_path:
            line_edit.setText(directory_path)
            return directory_path

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

    def display_info(self, info):
        self.file_name.setText(info.data(FILE_PATH))
        self.file_tags.setText(info.data(TEXT))

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

    def move_selected(self, files):
        pass


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


class TagListItemDelegate(QStyledItemDelegate):
    """ Custom delegate for displaying larger item with larger text"""

    def sizeHint(self, option, index):
        # Customize the size of items
        return QSize(100, 25)  # Adjust the width and height as needed

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        # Customize the font size of the item text
        option.font.setPointSize(12)  # Adjust the font size as needed
