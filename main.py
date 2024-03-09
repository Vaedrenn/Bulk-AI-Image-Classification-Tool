import multiprocessing
import sys

from PyQt5.QtWidgets import QApplication

from src.gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
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


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()

