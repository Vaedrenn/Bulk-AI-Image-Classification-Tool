import os
import sys

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QGridLayout, \
    QTextEdit, QLineEdit, QSlider, QSpinBox, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, QEvent
import CheckListWidget

from PyQt5.QtWidgets import QListWidgetItem

FILE_PATH = Qt.UserRole
GENERAL_RESULTS = Qt.UserRole + 1
RATING = Qt.UserRole + 2
TEXT = Qt.UserRole + 3


class MyGUI(QWidget):
    def __init__(self):
        super().__init__()
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
        self.filelist = CheckListWidget.CheckListWidget()
        select_all = QPushButton("Select All")
        deselect_all = QPushButton("Deselect All")
        self.filelist.itemClicked.connect(self.update_image)  # on click change image

        frame1.layout().addWidget(self.filelist, 0, 0, 1, 2)
        frame1.layout().addWidget(select_all, 1, 0)
        frame1.layout().addWidget(deselect_all, 1, 1)

        # Frame 2
        self.image_label_widget = QWidget()
        self.image_label_layout = QVBoxLayout(self.image_label_widget)
        image_label = QLabel(self.image_label_widget)

        pixmap = QPixmap(450, 400)
        pixmap.fill(Qt.white)  # Fill the pixmap with a white color
        image_label.setPixmap(pixmap)

        image_label.setPixmap(pixmap)
        self.image_label_layout.addWidget(image_label)
        image_label.setAlignment(Qt.AlignCenter)

        self.action_box = self.action_box_widget()

        text_output = QTextEdit()
        text_output.setPlaceholderText("Text Output")
        text_output.setReadOnly(True)

        frame2.layout().addWidget(self.image_label_widget)
        frame2.layout().addWidget(self.action_box)
        frame2.layout().addWidget(text_output)

        # Frame 3
        rating_tags = CheckListWidget.CheckListWidget()
        character_tags = CheckListWidget.CheckListWidget()
        general_tags = CheckListWidget.CheckListWidget()

        rating_tags.setMaximumHeight(100)
        character_tags.setMaximumHeight(100)

        frame3.layout().addWidget(rating_tags)
        frame3.layout().addWidget(character_tags)
        frame3.layout().addWidget(general_tags)

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
        button_grid = QGridLayout()
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
        reset_button = QPushButton("Reset")
        submit_button.clicked.connect(lambda value: self.submit(dir_input.text(), general_threshold.value()))

        one_image_button = QPushButton("Tag Current Image")
        all_images_button = QPushButton("Tag Selected images")

        button_grid.addWidget(submit_button, 0, 0)
        button_grid.addWidget(reset_button, 0, 1)
        button_grid.addWidget(one_image_button, 3, 0)
        button_grid.addWidget(all_images_button, 3, 1)

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

    def submit(self, directory, general_threshold):
        if self.model is None:
            return
        if self.labels is None or []:
            # Warn user that model correctly loaded but no labels are found
            return
        if directory is None:
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

            self.filelist.addItem(item)

    def update_image(self):
        try:
            image_path = self.filelist.currentItem().data(FILE_PATH)
            pixmap = QPixmap(image_path)  # open image as pixmap

            # remove any previous image labels and add new QLabel current image, This prevents stacking of image labels
            while self.image_label_layout.count() > 0:
                self.image_label_layout.takeAt(0).widget().deleteLater()

            image_label = QLabel(self.image_label_widget)
            image_label.setAlignment(Qt.AlignCenter)

            width = self.image_label_widget.width()
            height = self.image_label_widget.height()

            # scale down image if it's bigger than the container
            if pixmap.width() > width or pixmap.height() > height:
                image_label.setPixmap(pixmap.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio))
            else:
                image_label.setPixmap(pixmap)
            self.image_label_layout.addWidget(image_label)

        except Exception as e:
            print(e)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    myGUI = MyGUI()
    sys.exit(app.exec_())
