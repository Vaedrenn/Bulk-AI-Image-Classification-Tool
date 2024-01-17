import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout,QVBoxLayout, QLabel, QFrame
import CheckListWidget


class MyGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # Create labels
        filelist = CheckListWidget.CheckListWidget()
        frame2 = QFrame()
        frame3 = QFrame()

        # Create layout
        main_layout = QHBoxLayout()

        main_layout.addWidget(filelist)
        main_layout.addWidget(frame2)
        main_layout.addWidget(frame3)

        # Set main window layout
        self.setLayout(main_layout)
        frame2.setLayout(QHBoxLayout())

        # Set window properties
        self.setGeometry(100, 100, 400, 200)
        self.setWindowTitle('PyQt Horizontal Layout with Labels and Borders')
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myGUI = MyGUI()
    sys.exit(app.exec_())
