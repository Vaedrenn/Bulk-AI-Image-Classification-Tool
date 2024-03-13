from PyQt5 import QtCore
from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QFileDialog, QApplication
import tensorflow as tf

from src.gui.main_window import MainWindow


def test_load_model(qtbot):
    """Test if the main window is initialized correctly."""
    # Create the main window, not to be confused with QMainWindow
    main_window = MainWindow()
    directory_path = r"models/deepdanbooru-v3-20211112-sgd-e28"

    main_window.tab1.action_box.load_models(directory_path)

    qtbot.wait(10000)

    assert isinstance(main_window.tab1.model, tf.keras.Model)
    assert len(main_window.tab1.labels) > 0
    assert len(main_window.tab1.char_labels) > 0


def test_submit(qtbot):
    main_window = MainWindow()
    model_path = r"models/deepdanbooru-v3-20211112-sgd-e28"
    directory = r"tests/images"

    main_window.tab1.action_box.load_models(model_path)

    qtbot.wait(10000)

    main_window.tab1.action_box.submit(directory, 50, 85)

    qtbot.wait(10000)

    assert main_window.tab1.image_label
    assert main_window.tab1.filelist.count() == 3
    assert len(main_window.tab1.text_output.toPlainText()) > 10
    assert main_window.tab1.general_tags.count() > 3
    assert main_window.tab1.character_tags.count() == 0
    assert main_window.tab1.rating_tags.count() == 3

