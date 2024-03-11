from PyQt5.QtCore import Qt, QEvent, QSize
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QGridLayout, \
    QTextEdit, QSizePolicy, QStyleFactory, QCompleter, QLineEdit

from src.gui.CheckListWidget import CheckListWidget
from src.gui.TupleCheckListWidget import TupleCheckListWidget
from src.gui.action_box import ActionBox
from src.gui.dark_palette import create_dark_palette

FILE_PATH = Qt.UserRole
RATING = Qt.UserRole + 1
CHARACTER_RESULTS = Qt.UserRole + 2
GENERAL_RESULTS = Qt.UserRole + 3
TEXT = Qt.UserRole + 4
TAG_STATE = Qt.UserRole + 5


class ImageTagger(QWidget):
    def __init__(self):
        super().__init__()
        self.labels = []
        self.char_labels = []
        self.model = None
        self.results = None
        self.tag_count = {}

        # QWigdets
        self.image_label = None
        self.text_output = None
        self.general_tags = None
        self.character_tags = None
        self.rating_tags = None
        self.image_label_layout = None
        self.image_label_widget = None
        self.action_box = None
        self.filelist = None
        self.t_completer = None
        self.t_lineedit = None

        self.initUI()

    def initUI(self):
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        dark_palette = create_dark_palette()
        self.setPalette(dark_palette)
        self.setAutoFillBackground(True)

        # Create labels
        frame1 = QWidget()
        frame2 = QWidget()
        frame3 = QWidget()

        # Create layout
        main_layout = QHBoxLayout()

        main_layout.addWidget(frame1)
        main_layout.addWidget(frame2)
        main_layout.addWidget(frame3)

        # Set main window layout
        self.setLayout(main_layout)
        frame1.setLayout(QGridLayout())
        frame2.setLayout(QVBoxLayout())
        frame3.setLayout(QVBoxLayout())

        # Frame 1
        self.filelist = CheckListWidget()
        self.filelist.setIconSize(QSize(0, 0))
        select_all = QPushButton("Select All")
        deselect_all = QPushButton("Deselect All")
        self.filelist.itemClicked.connect(self.update_page)  # on click change image

        select_all.clicked.connect(self.select_all_files)
        deselect_all.clicked.connect(self.clear_all_files)

        frame1.layout().addWidget(self.filelist, 0, 0, 1, 2)
        frame1.layout().addWidget(select_all, 1, 0)
        frame1.layout().addWidget(deselect_all, 1, 1)

        # Frame 2
        self.image_label_widget = QWidget()
        self.image_label_layout = QVBoxLayout(self.image_label_widget)
        self.image_label_layout.setContentsMargins(0, 0, 0, 0)
        self.image_label_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.image_label = QLabel(self.image_label_widget)

        pixmap = QPixmap(450, 450)
        pixmap.fill(Qt.lightGray)  # Fill the pixmap with a white color
        self.image_label.setPixmap(pixmap)

        self.image_label.setPixmap(pixmap)
        self.image_label_layout.addWidget(self.image_label)
        self.image_label.setAlignment(Qt.AlignCenter)

        self.action_box = ActionBox(self, frame2)

        self.text_output = QTextEdit()
        self.text_output.setPlaceholderText("Text Output")
        self.text_output.setReadOnly(True)
        self.text_output.setMaximumHeight(200)

        frame2.layout().addWidget(self.image_label_widget)
        frame2.layout().addWidget(self.action_box)
        frame2.layout().addWidget(self.text_output)

        # Frame 3
        self.rating_tags = TupleCheckListWidget()
        self.character_tags = TupleCheckListWidget()
        self.general_tags = TupleCheckListWidget()

        self.rating_tags.setMaximumHeight(100)
        self.character_tags.setMaximumHeight(100)

        tag_box = QWidget()
        tag_box.setLayout(QHBoxLayout())
        tag_box.layout().setContentsMargins(0, 0, 0, 10)

        self.t_lineedit = QLineEdit()
        self.t_lineedit.setPlaceholderText("  Add a tag here and hit enter")
        t_button = QPushButton("Add Tag")

        self.t_completer = QCompleter(self.labels)
        self.t_lineedit.setCompleter(self.t_completer)
        # self.t_completer.activated.connect(self.add_tags)
        self.t_lineedit.returnPressed.connect(lambda: self.add_tags(self.t_lineedit.text()))
        t_button.clicked.connect(lambda: self.add_tags(self.t_lineedit.text()))

        tag_box.layout().addWidget(self.t_lineedit)
        tag_box.layout().addWidget(t_button)

        button_box = QWidget()
        button_box.setLayout(QHBoxLayout())
        button_box.layout().setContentsMargins(0, 0, 0, 0)

        store_tags = QPushButton("Save Changes")
        b_select_all = QPushButton("Select All")
        b_clear = QPushButton("Clear")

        store_tags.clicked.connect(lambda: self.update_tag_status())
        b_select_all.clicked.connect(lambda: self.select_all_tags())
        b_clear.clicked.connect(lambda: self.clear_tags())

        button_box.layout().addWidget(store_tags)
        button_box.layout().addWidget(b_select_all)
        button_box.layout().addWidget(b_clear)

        rating_label = QLabel("Content Rating")
        font = QFont()
        font.setPointSize(10)
        rating_label.setFont(font)
        rating_label.setContentsMargins(5, 5, 5, 5)

        character_label = QLabel("Character Tags")
        font = QFont()
        font.setPointSize(10)
        character_label.setFont(font)
        character_label.setContentsMargins(5, 5, 5, 5)

        general_label = QLabel("General Tags")
        font = QFont()
        font.setPointSize(10)
        general_label.setFont(font)
        general_label.setContentsMargins(5, 5, 5, 5)

        frame3.layout().addWidget(rating_label)
        frame3.layout().addWidget(self.rating_tags)
        frame3.layout().addWidget(character_label)
        frame3.layout().addWidget(self.character_tags)
        frame3.layout().addWidget(general_label)
        frame3.layout().addWidget(self.general_tags)
        frame3.layout().addWidget(tag_box)
        frame3.layout().addWidget(button_box)
        # self.setStyleSheet("border: 1px solid black;")

        # # Set window properties
        # self.setGeometry(100, 100, 1200, 800)
        # self.setWindowTitle('Bulk AI Image Classification Tool')
        # self.show()

    def update_page(self):
        """ Refreshes the contents of the page when a new image is selected """
        current_item = self.filelist.currentItem()
        rating = current_item.data(RATING)
        character_tags = current_item.data(CHARACTER_RESULTS)
        general_tags = current_item.data(GENERAL_RESULTS)
        tag_state = current_item.data(TAG_STATE)
        text = current_item.data(TEXT)

        self.update_image()
        self.update_tags(self.rating_tags, rating, tag_state)
        self.update_tags(self.character_tags, character_tags, tag_state)
        self.update_tags(self.general_tags, general_tags, tag_state)
        self.text_output.setText(text)

    def update_image(self):
        """ Changes the display image"""
        try:
            image_path = self.filelist.currentItem().data(FILE_PATH)
            pixmap = QPixmap(image_path)
            width = self.image_label_widget.width()
            height = self.image_label_widget.height()

            # scale down image if it's bigger than the container
            if pixmap.width() > width or pixmap.height() > height:
                self.image_label.setPixmap(
                    pixmap.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio, Qt.FastTransformation))
            else:
                self.image_label.setPixmap(pixmap)
            self.image_label_layout.addWidget(self.image_label)
        except Exception as e:
            print(e)

    def update_tags(self, checklist, tags, tag_state):
        """ Refreshes the tags in the given checklist"""
        checklist.clear()
        if tags is None:
            return
        for tag_name, value in tags.items():
            percentage = f"{value * 100:.2f}%"  # Format value as percentage
            checklist.addPair(tag_name, percentage, tag_state[tag_name])

    def update_tag_status(self):
        """ Saves the check states of the current image"""
        if self.filelist.currentItem() is None:
            return

        # get the current checks states of the tags
        checked_ratings = self.rating_tags.get_check_states()
        checked_characters = self.character_tags.get_check_states()
        checked_general = self.general_tags.get_check_states()
        data = self.filelist.currentItem().data(TAG_STATE)
        data.update(checked_general)
        data.update(checked_ratings)
        data.update(checked_characters)
        text = ', '.join(tag_name for tag_name, value in data.items() if value)

        # update associated tags
        current_item = self.filelist.currentItem()
        current_item.setData(TAG_STATE, data)
        current_item.setData(TEXT, text)

    def select_all_files(self):
        """ Checks all files in the filelist """
        self.filelist.check_all()

    def clear_all_files(self):
        """ Unchecks all files in the filelist """
        self.filelist.uncheck_all()

    def add_tags(self, text):
        """
        Adds user tags to tag list, if the tag is found in the char labels add it there if not goes into general
        You can add any tag you want here it does not have to be in labels.
        Adding a tag here will not add it to labels, you would have to add it manually to the txt
        """
        if self.filelist.currentItem() is None:
            return
        current = self.filelist.currentItem()
        if text in self.char_labels:
            data = current.data(CHARACTER_RESULTS)
            data[text] = 10  # 1000 denotes custom user tag
            current.setData(CHARACTER_RESULTS, data)

        else:
            data = current.data(GENERAL_RESULTS)
            data[text] = 10  # 1000 denotes custom user tag
            current.setData(GENERAL_RESULTS, data)
        tag_state = current.data(TAG_STATE)
        tag_state[text] = True
        current.setData(TAG_STATE, tag_state)

        self.update_tag_status()
        self.update_page()

    def select_all_tags(self):
        """ Checks all tags in general and character tags"""
        self.character_tags.check_all()
        self.general_tags.check_all()

    def clear_tags(self):
        """ Unchecks all tags in general and character tags"""
        self.character_tags.uncheck_all()
        self.general_tags.uncheck_all()

    def eventFilter(self, obj, event):
        # arrow key navigation
        if obj == self.filelist and event.type() == QEvent.KeyPress:
            key = event.key()

            if key == Qt.Key_Up:
                current_row = self.filelist.currentRow()
                if current_row > 0:
                    self.filelist.setCurrentRow(current_row - 1)
                    self.update_page()
                return True
            elif key == Qt.Key_Down:
                current_row = self.filelist.currentRow()
                if current_row < self.filelist.count() - 1:
                    self.filelist.setCurrentRow(current_row + 1)
                    self.update_page()
                return True

        return super().eventFilter(obj, event)

    def showEvent(self, event):
        self.filelist.installEventFilter(self)

    def hideEvent(self, event):
        self.filelist.removeEventFilter(self)
