from PyQt5 import uic
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush, QPalette
from PyQt5.QtWidgets import \
    QApplication,\
    QListWidgetItem,\
    QTableWidgetItem,\
    QColorDialog,\
    QTableWidget,\
    QStyledItemDelegate,\
    QStyle
from music import start_mixer, play_note, get_notes

window = uic.loadUiType('stackedwidget.ui')


class custListWidgetItem(QListWidgetItem):
    def __lt__(self, other):
        tone_scale = {
            'C': 0,
            'C#': 1,
            'Db': 2,
            'D': 3,
            'D#': 4,
            'Eb': 5,
            'E': 6,
            'F': 7,
            'F#': 8,
            'Gb': 9,
            'G': 10,
            'G#': 11,
            'Ab': 12,
            'A': 13,
            'A#': 14,
            'Bb': 15,
            'B': 16,
        }
        self_data = self.data(Qt.EditRole).split(',')
        self_tone = self_data[0]
        self_octave = self_data[1]

        other_data = other.data(Qt.EditRole).split(',')
        other_tone = other_data[0]
        other_octave = other_data[1]

        return tone_scale[self_tone] < tone_scale[other_tone] or int(self_octave) < int(other_octave)


class StyleDelegateForQTableWidget(QStyledItemDelegate):
    color_default = QColor("#aaedff")

    def paint(self, painter, option, index):
        if option.state & QStyle.State_Selected:
            option.palette.setColor(QPalette.HighlightedText, Qt.black)
            color = self.combineColors(self.color_default, self.background(option, index))
            option.palette.setColor(QPalette.Highlight, color)
        QStyledItemDelegate.paint(self, painter, option, index)

    def background(self, option, index):
        item = self.parent().itemFromIndex(index)
        if item:
            if item.background() != QBrush():
                return item.background().color()
        if self.parent().alternatingRowColors():
            if index.row() % 2 == 1:
                return option.palette.color(QPalette.AlternateBase)
        return option.palette.color(QPalette.Base)

    @staticmethod
    def combineColors(c1, c2):
        c3 = QColor()
        c3.setRed((c1.red() + c2.red()) / 2)
        c3.setGreen((c1.green() + c2.green()) / 2)
        c3.setBlue((c1.blue() + c2.blue()) / 2)

        return c3


class MainWindow(window[0], window[1]):
    def __init__(self):
        super().__init__()
        start_mixer()
        self.setupUi(self)

        # PAGE 1
        for note in get_notes():
            self.listWidget_2.addItem(custListWidgetItem(note))
        self.listWidget_2.setSortingEnabled(True)
        self.listWidget.setSortingEnabled(True)

        self.pushButton_2.clicked.connect(self.to_colors)
        self.toolButton.clicked.connect(self.add_to_right)

        # PAGE 2
        self.tableWidget.setHorizontalHeaderLabels(['Nota', 'Color'])
        self.tableWidget.horizontalHeader().show()
        self.tableWidget.cellDoubleClicked.connect(self.choose_color)

        self.pushButton_3.clicked.connect(lambda:
                                          self.setCurrentIndex(0))
        self.pushButton_4.clicked.connect(lambda:
                                          self.setCurrentIndex(2))
        self.tableWidget.setItemDelegate(StyleDelegateForQTableWidget(self.tableWidget))

    # PAGE 1 Methods

    def add_to_right(self):
        item = self.listWidget_2.takeItem(self.listWidget_2.currentRow())
        self.listWidget.addItem(item)
        self.listWidget.sortItems()

    def add_to_left(self):
        item = self.listWidget.takeItem(self.listWidget_2.currentRow())
        self.listWidget_2.addItem(item)
        self.listWidget_2.sortItems()

    def to_colors(self):
        items = [self.listWidget.item(i).data(Qt.EditRole) for i in range(self.listWidget.count())]
        self.tableWidget.setRowCount(len(items))
        for row, item in enumerate(items):
            tone_item = QTableWidgetItem(item)
            tone_item.setFlags(tone_item.flags() ^ Qt.ItemIsEditable)

            color_item = QTableWidgetItem()
            color_item.setFlags(color_item.flags() ^ Qt.ItemIsEditable)
            self.tableWidget.setItem(row, 0, tone_item)
            self.tableWidget.setItem(row, 1, color_item)
        self.setCurrentIndex(1)

    # Page 2 Methods
    def choose_color(self, row, column):
        if column == 1:
            color = QColorDialog.getColor()
            self.tableWidget.item(row, column).setData(Qt.BackgroundRole, color)


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
