import sys

from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QGroupBox
import CheckListWidget


class MyGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # Create labels
        filelist = CheckListWidget.CheckListWidget()
        frame2 = QWidget()
        frame3 = QWidget()

        # Create layout
        main_layout = QHBoxLayout()

        main_layout.addWidget(filelist)
        main_layout.addWidget(frame2)
        main_layout.addWidget(frame3)

        # Set main window layout
        self.setLayout(main_layout)
        frame2.setLayout(QVBoxLayout())
        frame3.setLayout(QVBoxLayout())

        # Frame 2
        image_display = QLabel("image")

        action_box = QGroupBox()
        action_box_layout = QHBoxLayout()
        action_box.setLayout(action_box_layout)

        button1 = QPushButton("Button 1")
        action_box.layout().addWidget(button1)

        text_output = QLabel("text output")

        frame2.layout().addWidget(image_display)
        frame2.layout().addWidget(action_box)
        frame2.layout().addWidget(text_output)

        # Frame 3
        rating_tags = CheckListWidget.CheckListWidget()
        character_tags = CheckListWidget.CheckListWidget()
        general_tags = CheckListWidget.CheckListWidget()

        frame3.layout().addWidget(rating_tags)
        frame3.layout().addWidget(character_tags)
        frame3.layout().addWidget(general_tags)


        # Set window properties
        self.setGeometry(100, 100, 400, 200)
        self.setWindowTitle('PyQt Horizontal Layout with Labels and Borders')
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myGUI = MyGUI()
    sys.exit(app.exec_())
