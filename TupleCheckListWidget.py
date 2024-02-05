from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QAbstractItemView, QWidget, QHBoxLayout, QLabel, QCheckBox


class CustomListItem(QWidget):
    def __init__(self, text1, text2, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)  # Remove padding
        self.checkbox = QCheckBox()
        self.checkbox.setCheckState(Qt.Checked)
        layout.addWidget(self.checkbox)
        layout.addWidget(QLabel(text1))
        layout.addStretch(1)
        layout.addWidget(QLabel(text2))

    def get_checkbox(self):
        return self.checkbox


class TupleCheckListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)  # Allows ctrl and  shift click selection

    def addItem(self, item1, item2):
        item = CustomListItem(item1, item2)
        list_item = QListWidgetItem(self)
        list_item.setSizeHint(item.sizeHint())
        QListWidget.addItem(self, list_item)
        self.setItemWidget(list_item, item)


    def getCheckedRows(self):
        return self.__getRows(Qt.Checked)

    def getUncheckedRows(self):
        return self.__getRows(Qt.Unchecked)

    def __getRows(self, status: Qt.CheckState):
        ret_list = []
        for i in range(self.count()):
            item_checkbox = self.itemWidget(self.item(i)).get_checkbox()
            if item_checkbox.checkState() == status:
                ret_list.append(i)

        return ret_list

    def removeCheckedRows(self):
        status = Qt.Checked
        checked_rows = self.__getRows(status)
        offset = 0  # Offset to adjust for removed items

        for i in checked_rows:
            self.takeItem(i - offset)
            offset += 1

    def clear_selection(self):
        selected_items = self.selectedItems()
        for i in selected_items:
            item_checkbox = self.itemWidget(i).get_checkbox()
            item_checkbox.setCheckState(Qt.Unchecked)

    def keyPressEvent(self, event):
        # on space key press swap states
        if event.key() == Qt.Key_Space:
            selected_items = self.selectedItems()
            for item in selected_items:
                item_checkbox = self.itemWidget(item).get_checkbox()
                current_state = item_checkbox.checkState()
                if current_state == Qt.Checked:
                    item_checkbox.setCheckState(Qt.Unchecked)
                else:
                    item_checkbox.setCheckState(Qt.Checked)

        # Uncheck all selected items with CTRL + D
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_D:
            self.clear_selection()
        # do default action
        else:
            super().keyPressEvent(event)
