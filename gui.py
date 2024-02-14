import os
import sys
from collections import OrderedDict

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QGridLayout, \
    QTextEdit, QLineEdit, QSlider, QSpinBox, QFileDialog, QMessageBox, QSizePolicy
from PyQt5.QtCore import Qt, QEvent
from CheckListWidget import CheckListWidget
from TupleCheckListWidget import TupleCheckListWidget
from PyQt5.QtWidgets import QListWidgetItem

FILE_PATH = Qt.UserRole
RATING = Qt.UserRole + 1
CHARACTER_RESULTS = Qt.UserRole + 2
GENERAL_RESULTS = Qt.UserRole + 3
TEXT = Qt.UserRole + 4
TAG_STATE = Qt.UserRole + 5


class MyGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.image_label = None
        self.text_output = None
        self.general_tags = None
        self.character_tags = None
        self.rating_tags = None
        self.image_label_layout = None
        self.image_label_widget = None
        self.labels = []
        self.model = None
        self.action_box = None
        self.filelist = None
        self.initUI()

    def initUI(self):
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

        self.image_label = QLabel(self.image_label_widget)

        pixmap = QPixmap(450, 450)
        pixmap.fill(Qt.white)  # Fill the pixmap with a white color
        self.image_label.setPixmap(pixmap)

        self.image_label.setPixmap(pixmap)
        self.image_label_layout.addWidget(self.image_label)
        self.image_label.setAlignment(Qt.AlignCenter)

        self.action_box = self.action_box_widget()

        self.text_output = QTextEdit()
        self.text_output.setPlaceholderText("Text Output")
        self.text_output.setReadOnly(True)

        frame2.layout().addWidget(self.image_label_widget)
        frame2.layout().addWidget(self.action_box)
        frame2.layout().addWidget(self.text_output)

        # Frame 3
        self.rating_tags = TupleCheckListWidget()
        self.character_tags = TupleCheckListWidget()
        self.general_tags = TupleCheckListWidget()

        self.rating_tags.setMaximumHeight(100)
        self.character_tags.setMaximumHeight(100)

        button_box = QWidget()
        button_box.setLayout(QHBoxLayout())
        button_box.layout().setContentsMargins(0, 0, 0, 0)

        store_tags = QPushButton("Save Changes")
        b_select_all = QPushButton("Select All")
        b_clear = QPushButton("Clear")

        store_tags.clicked.connect(lambda value: self.update_tag_status())
        b_select_all.clicked.connect(lambda value: self.select_all_tags())
        b_clear.clicked.connect(lambda value: self.clear_tags())

        button_box.layout().addWidget(store_tags)
        button_box.layout().addWidget(b_select_all)
        button_box.layout().addWidget(b_clear)

        frame3.layout().addWidget(self.rating_tags)
        frame3.layout().addWidget(self.character_tags)
        frame3.layout().addWidget(self.general_tags)
        frame3.layout().addWidget(button_box)
        # self.setStyleSheet("border: 1px solid black;")

        # Set window properties
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowTitle('PyQt Horizontal Layout with Labels and Borders')
        self.show()

    def action_box_widget(self) -> QWidget:
        action_box = QWidget(self)
        action_layout = QVBoxLayout()
        action_box.setLayout(action_layout)

        selection_frame = QWidget()
        slider_frame = QWidget()
        button_frame = QWidget()
        output_frame = QWidget()

        selection_grid = QGridLayout()
        slider_grid = QGridLayout()
        button_grid = QHBoxLayout()
        output_grid = QGridLayout()

        selection_frame.setLayout(selection_grid)
        slider_frame.setLayout(slider_grid)
        button_frame.setLayout(button_grid)
        output_frame.setLayout(output_grid)

        action_layout.addWidget(selection_frame)
        action_layout.addWidget(slider_frame)
        action_layout.addWidget(button_frame)

        model_input = QLineEdit()
        model_input.setPlaceholderText("Select model directory...")
        dir_input = QLineEdit()
        dir_input.setPlaceholderText("Select directory...")
        model_button = QPushButton("Browse")
        dir_button = QPushButton("Browse")

        model_button.clicked.connect(lambda value: self.browse_model(model_input))
        dir_button.clicked.connect(lambda value: self.browse_directory(dir_input))

        selection_grid.addWidget(model_input, 0, 0)
        selection_grid.addWidget(model_button, 0, 1)
        selection_grid.addWidget(dir_input, 1, 0)
        selection_grid.addWidget(dir_button, 1, 1)

        general_tag = QLabel("General Tags Threshold")
        character_tag = QLabel("Character Tags Threshold")
        general_slider = QSlider(Qt.Horizontal)
        character_slider = QSlider(Qt.Horizontal)
        general_threshold = QSpinBox()
        character_threshold = QSpinBox()

        general_slider.setMinimum(0)
        general_slider.setMaximum(100)
        general_slider.setTickInterval(1)
        character_slider.setMinimum(0)
        character_slider.setMaximum(100)
        character_slider.setTickInterval(1)

        general_threshold.setMinimum(0)
        general_threshold.setMaximum(100)
        character_threshold.setMinimum(0)
        character_threshold.setMaximum(100)

        general_slider.valueChanged.connect(lambda value: general_threshold.setValue(value))
        character_slider.valueChanged.connect(lambda value: character_threshold.setValue(value))
        general_threshold.valueChanged.connect(lambda value: general_slider.setValue(value))
        character_threshold.valueChanged.connect(lambda value: character_slider.setValue(value))
        general_threshold.setValue(50)
        character_threshold.setValue(85)

        slider_grid.addWidget(general_tag, 0, 0)
        slider_grid.addWidget(general_threshold, 0, 2)
        slider_grid.addWidget(general_slider, 1, 0, 1, 3)
        slider_grid.addWidget(character_tag, 2, 0)
        slider_grid.addWidget(character_threshold, 2, 2)
        slider_grid.addWidget(character_slider, 3, 0, 1, 3)

        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(lambda value: self.submit(dir_input.text(), general_threshold.value()))

        one_image_button = QPushButton("Tag Current Image")
        selected_images_button = QPushButton("Tag Selected images")
        one_image_button.clicked.connect(lambda value: self.tag_image())
        selected_images_button.clicked.connect(lambda value: self.tag_selected_images())

        button_grid.addWidget(submit_button)
        button_grid.addWidget(one_image_button)
        button_grid.addWidget(selected_images_button)
        return action_box

    def browse_directory(self, line_edit):
        directory_path = QFileDialog.getExistingDirectory(None, "Select Directory")
        if directory_path:
            line_edit.setText(directory_path)
            return directory_path

    def browse_model(self, line_edit):
        directory_path = QFileDialog.getExistingDirectory(None, "Select Directory")
        if not directory_path:
            return
        else:
            print("importing actions")
            from actions import load_model, load_labels
            print("Finished importing actions")
            line_edit.setText(directory_path)
            self.model = load_model(directory_path)
            self.labels = load_labels(directory_path)
            return directory_path

    # Tags all images in the directory
    def submit(self, directory, general_threshold):
        if self.model is None or directory is None or directory == '':
            return
        if self.labels is None or []:
            # Warn user that model correctly loaded but no labels are found
            QMessageBox.warning(self, "Warning", "Model loaded successfully but no labels are found.")
            return

        from actions import predict_all

        score_threshold = general_threshold / 100

        # filename, [threshold_results, all_results, rating_results, text]
        results = predict_all(self.model, self.labels, directory, score_threshold)

        if len(results) == 0 or results is None:
            QMessageBox.information(self, " ", "No duplicate images were found.")
            return

        # Populate filelist
        self.filelist.clear()
        for image in results:
            file_path = image[0]
            threshold_results, _, rating_results, text = image[1]
            filename = os.path.basename(file_path)
            item = QListWidgetItem(filename)
            item.setData(FILE_PATH, file_path)
            item.setData(GENERAL_RESULTS, threshold_results)
            item.setData(RATING, rating_results)
            item.setData(TEXT, text)

            # Build initial tag states
            max_rating_key = max(rating_results, key=rating_results.get)
            tag_state = {}

            # Only check the content rating for threshold, check everything else
            for key in rating_results.keys():
                if key == max_rating_key:
                    tag_state[key] = True
                else:
                    tag_state[key] = False

            for key, value in threshold_results.items():
                tag_state[key] = True

            item.setData(TAG_STATE, tag_state)

            self.filelist.addItem(item)

    # Refreshes the contents of the page when a new image is selected
    def update_page(self):
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

    # Display image
    def update_image(self):
        try:
            image_path = self.filelist.currentItem().data(FILE_PATH)
            pixmap2 = QPixmap(image_path)
            # scale down image if larger than container
            self.image_label.setPixmap(pixmap2.scaled(
                self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

        except Exception as e:
            print(e)

    # Refreshes the tags in the given checklist
    def update_tags(self, checklist, tags, tag_state):
        checklist.clear()
        if tags is None:
            return
        for tag_name, value in tags.items():
            percentage = f"{value * 100:.2f}%"  # Format value as percentage
            checklist.addPair(tag_name, percentage, tag_state[tag_name])

    # Saves the tags of the current image
    def update_tag_status(self):
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
        self.filelist.check_all()

    def clear_all_files(self):
        self.filelist.uncheck_all()

    def select_all_tags(self):
        self.character_tags.check_all()
        self.general_tags.check_all()

    def clear_tags(self):
        self.character_tags.uncheck_all()
        self.general_tags.uncheck_all()

    # Writes the tags to exif
    def tag_image(self):
        if not self.model:
            return False
        if not self.labels:
            return False
        from actions import write_tags
        current_image = self.filelist.currentItem()
        info = current_image.data(TEXT)
        image_path = current_image.data(FILE_PATH)
        write_tags(image_path, info)

    # Writes tags to exif for all selected images
    def tag_selected_images(self):
        if not self.model:
            return False
        if not self.labels:
            return False
        from actions import write_tags
        selected_rows = self.filelist.getCheckedRows()
        for row in selected_rows:
            item = self.filelist.item(row)
            info = item.data(TEXT)
            image_path = item.data(FILE_PATH)
            write_tags(image_path, info)

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myGUI = MyGUI()
    import actions

    directory_path = r"models/deepdanbooru-v3-20211112-sgd-e28"
    directory = r"tests/images"
    myGUI.model = actions.load_model(directory_path)
    myGUI.labels = actions.load_labels(directory_path)
    myGUI.submit(directory, 50)

    sys.exit(app.exec_())
