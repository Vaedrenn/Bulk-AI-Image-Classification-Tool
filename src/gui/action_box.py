import os
from collections import OrderedDict

import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QThread, QStringListModel
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QListWidgetItem, QProgressDialog, QGroupBox
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QGridLayout, \
    QLineEdit, QSlider, QSpinBox, QFileDialog, QMessageBox

import tensorflow as tf

from src.commands.predict_all import process_images_from_directory, predict
from src.commands.exif_actions import write_tags
from src.commands.load_actions import load_model, load_labels, load_char_labels

FILE_PATH = Qt.UserRole
RATING = Qt.UserRole + 1
CHARACTER_RESULTS = Qt.UserRole + 2
GENERAL_RESULTS = Qt.UserRole + 3
TEXT = Qt.UserRole + 4
TAG_STATE = Qt.UserRole + 5


class ActionBox(QGroupBox):
    def __init__(self, main_widget, parent):
        super().__init__(parent)
        self.dir_input = None
        self.model_input = None
        self.main_widget = main_widget
        self.model_button = QPushButton("Browse")
        self.dir_button = QPushButton("Browse")

        self.images = []
        self.initUI()

    def initUI(self):
        action_layout = QVBoxLayout()
        self.setLayout(action_layout)

        selection_frame = QGroupBox()
        slider_frame = QGroupBox()
        button_frame = QGroupBox()
        output_frame = QGroupBox()

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

        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("Select model directory...")
        self.dir_input = QLineEdit()
        self.dir_input.setPlaceholderText("Select directory...")
        self.model_button = QPushButton("Browse")
        self.dir_button = QPushButton("Browse")

        self.model_button.clicked.connect(lambda: self.browse_model(self.model_input))
        self.dir_button.clicked.connect(lambda: self.browse_directory(self.dir_input))

        selection_grid.addWidget(self.model_input, 0, 0)
        selection_grid.addWidget(self.model_button, 0, 1)
        selection_grid.addWidget(self.dir_input, 1, 0)
        selection_grid.addWidget(self.dir_button, 1, 1)

        general_tag = QLabel("General Tags Threshold")
        character_tag = QLabel("Character Tags Threshold")
        general_slider = QSlider(Qt.Horizontal)
        character_slider = QSlider(Qt.Horizontal)
        general_threshold = QSpinBox()
        character_threshold = QSpinBox()

        general_slider.setMinimum(1)  # Anything lower than 1 will result in long load times when updating page
        general_slider.setMaximum(100)
        general_slider.setTickInterval(1)
        character_slider.setMinimum(1)
        character_slider.setMaximum(100)
        character_slider.setTickInterval(1)

        general_threshold.setMinimum(1)
        general_threshold.setMaximum(100)
        character_threshold.setMinimum(1)
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
        submit_button.clicked.connect(
            lambda: self.submit(self.dir_input.text(), general_threshold.value(), character_threshold.value()))

        one_image_button = QPushButton("Tag Current Image")
        selected_images_button = QPushButton("Tag Selected images")
        one_image_button.clicked.connect(lambda: self.tag_image())
        selected_images_button.clicked.connect(lambda: self.tag_selected_images())

        button_grid.addWidget(submit_button)
        button_grid.addWidget(one_image_button)
        button_grid.addWidget(selected_images_button)

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

    def browse_model(self, line_edit) -> None:
        """
        Load model from directory for gui. Operation creates a new thread.
        refer to ModelWorker for more info.
        :parameter line_edit: QLineEdit where text will be displayed
        """
        directory_path = QFileDialog.getExistingDirectory(None, "Select Model")
        if not directory_path:
            return
        else:
            line_edit.setText(directory_path)
            self.load_models(directory_path)

    def load_models(self, directory_path):

            self.pd = QProgressDialog("Loading Model...", None, 0, 0, self.main_widget)
            # Prevents the user from interacting with the gui until finished
            self.pd.setWindowModality(QtCore.Qt.WindowModal)
            self.pd.setCancelButton(None)
            self.pd.setWindowTitle("Please wait")
            self.pd.setLabelText("Loading Model...")
            self.pd.setFixedSize(250, 100)
            self.pd.show()
            # self.pd.forceShow()  # use instead of above incase it does not show

            self.thread = QThread(self.main_widget)
            self.worker = ModelWorker(directory_path)

            self.worker.moveToThread(self.thread)

            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self._load_results)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.pd.close)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)

            self.thread.start()

    def _load_results(self, results) -> None:
        """
        Helper function for loading models and tags. ALso sets the model for completer
        :parameter results: model, labels, and character labels to be loaded
        """
        model, labels, char_labels = results
        self.main_widget.model = model
        self.main_widget.labels = labels
        self.main_widget.char_labels = char_labels
        self.main_widget.t_completer.setModel(QStringListModel(self.main_widget.labels))  # update tag completer

    def submit(self, directory: str, general_threshold: int, char_threshold: int) -> None:
        """
        Predicts tags for all images in the directory. Does not go into subdirectories.

        :param char_threshold: limit to what to tag if prob > threshold then write that tag
        :param general_threshold: limit to what to tag if prob > threshold then write that tag
        :param directory: directory to target
        """
        if self.main_widget.model is None or directory is None or directory == '':
            print("No model found")
            return
        if self.main_widget.labels is None or []:
            # Warn user that model correctly loaded but no labels are found
            QMessageBox.warning(self, "Warning", "Model loaded successfully but no labels are found.")
            return

        score_threshold = general_threshold / 100
        char_threshold = char_threshold / 100
        self.pd = QProgressDialog("Preprocessing Images...", None, 0, 100, self)
        self.pd.setWindowModality(QtCore.Qt.WindowModal)
        self.pd.setCancelButton(None)
        self.pd.setWindowTitle("Please wait")
        self.pd.setLabelText("Preprocessing Images...")
        self.pd.setFixedSize(250, 150)
        self.pd.show()
        # self.pd.forceShow()  # use instead of above incase it does not show

        # process images before predicting
        self.thread = QThread(self.main_widget)
        self.worker = PredictWorker(self.main_widget.model,
                                    directory,
                                    self.main_widget.labels,
                                    self.main_widget.char_labels,
                                    score_threshold,
                                    char_threshold)

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.max.connect(self._set_max)
        self.worker.progress.connect(self._update_progress)
        self.worker.results.connect(self.process_results)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.pd.close)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # assign images to results

        self.thread.start()

    def _set_max(self, maximum) -> None:
        """
        Helper function for setting the bar for progress dialog
        @param maximum: how many steps to take
        """
        self.pd.setLabelText("Predicting Tags")
        self.pd.setMaximum(maximum)

    def _update_progress(self, val) -> None:
        """
        Helper function for setting the bar for progress dialog
        @param val: increment progress bar by this
        """
        self.pd.setValue(self.pd.value() + val)

    def process_results(self, result_count):
        """
        Processes results into the GUI and refreshes the page
        :param result_count: results of predictions, and count of tags
        """
        results, count = result_count
        if len(results) == 0 or None:
            QMessageBox.information(self, "No results", "No results within threshold")

        self.main_widget.filelist.clear()
        # Populate filelist
        for image in results:
            file_path = image[0]
            threshold_results, _, rating_results, char_results, text = image[1]
            filename = os.path.basename(file_path)
            pixmap = QPixmap(file_path).scaledToHeight(200, Qt.FastTransformation)
            icon = QIcon(pixmap)
            item = QListWidgetItem(icon, filename)
            item.setData(FILE_PATH, file_path)
            item.setData(GENERAL_RESULTS, threshold_results)
            item.setData(CHARACTER_RESULTS, char_results)
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

            for key, value in char_results.items():
                tag_state[key] = True

            for key, value in threshold_results.items():
                tag_state[key] = True

            item.setData(TAG_STATE, tag_state)
            self.main_widget.filelist.addItem(item)
        self.main_widget.results = self.main_widget.filelist.model()  # set a pointer to listwidget's model
        self.main_widget.tag_count = count
        self.main_widget.filelist.setCurrentRow(0)
        self.main_widget.update_page()

    def tag_image(self):
        """
        Write tags to image's exif
        :return: True if successful, False if labels or model is missing
        """
        if not self.main_widget.model:
            return False
        if not self.main_widget.labels:
            return False

        current_image = self.main_widget.filelist.currentItem()
        info = current_image.data(TEXT)
        image_path = current_image.data(FILE_PATH)
        write_tags(image_path, info)

        return True

    def tag_selected_images(self):
        """
        Write tags to image's exif for all selected images
        :return: True if successful, False if labels or model is missing
        """
        if not self.main_widget.model:
            return False
        if not self.main_widget.labels:
            return False

        selected_rows = self.main_widget.filelist.getCheckedRows()
        for row in selected_rows:
            item = self.filelist.item(row)
            info = item.data(TEXT)
            image_path = item.data(FILE_PATH)
            write_tags(image_path, info)


class ModelWorker(QObject):
    """
     Worker Object for qthreading, loads models and tags from directory
    """
    finished = pyqtSignal(tuple)

    def __init__(self, directory_path):
        super().__init__()
        self.directory_path = directory_path

    def run(self):
        model = load_model(self.directory_path)
        labels = load_labels(self.directory_path)
        char_labels = load_char_labels(self.directory_path)
        self.finished.emit((model, labels, char_labels))


class ImageWorker(QObject):
    """
    Worker Object for qthreading, calls predicts all
    """
    finished = pyqtSignal()
    cancelled = pyqtSignal(bool)
    max = pyqtSignal(int)
    results = pyqtSignal(list)
    progress = pyqtSignal(int)

    def __init__(self, model, directory, labels, char_labels, score, char):
        super().__init__()
        self.model = model
        self.directory = directory
        self.labels = labels
        self.char_labels = char_labels
        self.score_threshold = score
        self.char_threshold = char
        self.processed_images = []

    def run(self):
        images = process_images_from_directory(self.model, self.directory)
        val = len(images)
        self.max.emit(val * 2)
        self.progress.emit(val)

        for image in images:
            result = predict(self.model, self.labels, self.char_labels, image[1], self.score_threshold,
                             self.char_threshold)
            if result is not None:
                self.processed_images.append((image[0], result))
            self.progress.emit(1)
        if len(self.processed_images) > 0:
            self.results.emit(self.processed_images)
        self.finished.emit()


class PredictWorker(QObject):
    """
    Worker Object for qthreading, calls predicts all.
    Faster implementation of ImageWorker, uses significantly more computing power
    Tensorflow: GPU not supported on Windows unless used with WSL
    """
    finished = pyqtSignal()
    max = pyqtSignal(int)
    results = pyqtSignal(tuple)
    progress = pyqtSignal(int)

    def __init__(self, model, directory, labels, char_labels, score, char):
        super().__init__()
        self.model = model
        self.directory = directory
        self.labels = labels
        self.char_labels = char_labels
        self.score_threshold = score
        self.char_threshold = char
        self.processed_images = []

    def run(self):
        images = process_images_from_directory(self.model, self.directory)
        val = len(images)
        self.max.emit(val * 3)
        self.progress.emit(val)

        filenames, arrays = zip(*images)
        arrays = np.array(arrays)

        # Stop TF from hogging all the VRAM, GPU not supported on windows
        gpus = tf.config.experimental.list_physical_devices("GPU")
        if gpus:
            try:
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
            except RuntimeError as e:
                print(e)

        probs = self.model.predict(arrays, batch_size=20, use_multiprocessing=True)
        probs = probs.astype(float)
        self.progress.emit(val)
        tag_count = {"rating:safe": 0, "rating:questionable": 0, "rating:explicit": 0}

        # Match labels with predictions
        for filename, probs in zip(filenames, probs):
            # Extract the last three tags as ratings
            rating_labels = ["rating:safe", "rating:questionable", "rating:explicit"]
            rating_probs = probs[-3:]
            probs = probs[:-3]
            # get the highest rating
            result_rating = OrderedDict(zip(rating_labels, rating_probs))
            max_index = max(result_rating, key=result_rating.get)
            tag_count[max_index] = tag_count[max_index] + 1

            # Get the indices of labels sorted by probability in descending order
            indices = np.argsort(probs)[::-1]

            result_all = OrderedDict()
            result_all[max_index] = result_rating[max_index]
            result_threshold = OrderedDict()
            result_char = OrderedDict()

            # Iterate over the sorted indices
            for index in indices:
                label = self.labels[index]
                prob = probs[index]

                # Store result for all labels
                result_all[label] = prob
                tag_count[label] = tag_count.get(label, 0) + 1

                # If probability is below the threshold, stop adding to threshold results, cannot assume char > general
                if prob < self.score_threshold and prob < self.char_threshold:
                    break

                # Store result for labels above the threshold
                if prob > self.score_threshold and label not in self.char_labels:
                    result_threshold[label] = prob
                if prob > self.char_threshold and label in self.char_labels:
                    result_char[label] = prob

            result_text = ', '.join(result_all.keys())
            self.progress.emit(val)
            if len(result_threshold) > 0 or len(result_char) > 0:
                self.processed_images.append(
                    (filename, (result_threshold, result_all, result_rating, result_char, result_text)))

        self.results.emit((self.processed_images, tag_count))
        self.finished.emit()
