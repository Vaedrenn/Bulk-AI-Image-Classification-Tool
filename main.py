import multiprocessing
import sys

from PyQt5.QtWidgets import QApplication

from src.gui.image_tagger import ImageTagger

def main():
    app = QApplication(sys.argv)
    myGUI = ImageTagger()

    sys.exit(app.exec_())

if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
