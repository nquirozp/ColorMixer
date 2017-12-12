from PyQt5 import uic, QtTest
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush, QPalette
from PyQt5.QtWidgets import \
    QApplication, \
    QListWidgetItem, \
    QTableWidgetItem, \
    QColorDialog, \
    QStyledItemDelegate, \
    QStyle
from music import start_mixer, play_note, TonoFactory, stop_mixer
from threading import Thread, Event

window = uic.loadUiType('mainwindow.ui')


class custListWidgetItem(QListWidgetItem):
    def __lt__(self, other):
        tone_scale = {
            'C': 0,
            'C#/Db': 1,
            'D': 2,
            'D#/Eb': 3,
            'E': 4,
            'F': 5,
            'F#/Gb': 6,
            'G': 7,
            'G#/Ab': 8,
            'A': 9,
            'A#/Bb': 10,
            'B': 11,
        }
        self_data = self.data(Qt.EditRole).split(',')
        self_tone = self_data[0][7:]
        self_octave = self_data[1][10:]

        other_data = other.data(Qt.EditRole).split(',')
        other_tone = other_data[0][7:]
        other_octave = other_data[1][10:]
        if tone_scale[self_tone] == tone_scale[other_tone]:
            return int(self_octave) < int(other_octave)
        elif int(self_octave) == int(other_octave):
            return tone_scale[self_tone] < tone_scale[other_tone]
        else:
            return int(self_octave) < int(other_octave)


class StyleDelegateForQTableWidget(QStyledItemDelegate):
    color_default = QColor(255, 255, 255, 0)

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
        self.setupUi(self)
        self.tf = TonoFactory()
        self.stackedWidget.setCurrentIndex(0)
        p = self.colorFrame.palette()
        self.frame_color = p.color(self.colorFrame.backgroundRole())
        # PAGE 1
        self.notesList.setSortingEnabled(True)

        self.next1.clicked.connect(self.to_colors)
        self.addToRight.clicked.connect(self.add_to_right)
        self.addToLeft.clicked.connect(self.add_to_left)

        # PAGE 2
        self.tableWidget.setHorizontalHeaderLabels(['Nota', 'Color'])
        self.tableWidget.horizontalHeader().show()
        self.tableWidget.cellDoubleClicked.connect(self.choose_color)

        self.previous2.clicked.connect(lambda:
                                       self.stackedWidget.setCurrentIndex(0))
        self.next2.clicked.connect(self.to_sounds)
        self.tableWidget.setItemDelegate(StyleDelegateForQTableWidget(self.tableWidget))

        # PAGE 3
        self.stop_event = Event()


    # PAGE 1 Methods

    def add_to_right(self):
        nota = str(self.noteStringBox.textFromValue(self.noteStringBox.value()))
        octava = self.octaveSpin.value()
        tiempo = self.durationSpin.value()
        if self.tf.new_tono(nota, octava, tiempo):
            self.notesList.addItem(custListWidgetItem(str(self.tf.tonos[-1])))
            self.tf.tonos[-1].nota.color = self.frame_color
            self.durationSpin.setValue(1)
        else:
            self.warningLabel.setText('No puedes agregar este tono!.')
            QtTest.QTest.qWait(2000)
            self.warningLabel.setText('')
        self.notesList.sortItems()

    def add_to_left(self):
        row = self.notesList.currentRow()
        if row == -1:
            row = self.notesList.count() - 1

        self.notesList.takeItem(row)
        self.tf.remove_tono(row)

    def to_colors(self):
        notas = []
        for tono in self.tf.tonos:
            t_nota = tono.nota.nota
            if t_nota not in notas:
                notas.append(t_nota)
        self.tableWidget.setRowCount(len(notas))
        for row, nota in enumerate(notas):
            tone_item = QTableWidgetItem(nota)
            tone_item.setFlags(tone_item.flags() ^ Qt.ItemIsEditable)

            color_item = QTableWidgetItem()
            color_item.setFlags(color_item.flags() ^ Qt.ItemIsEditable)
            self.tableWidget.setItem(row, 0, tone_item)
            self.tableWidget.setItem(row, 1, color_item)
        self.stackedWidget.setCurrentIndex(1)

    # Page 2 Methods
    def choose_color(self, row, column):
        if column == 1:
            color = QColorDialog.getColor()
            self.tf.notas[str(self.tableWidget.item(row, 0).text())].color = color
            self.tableWidget.item(row, column).setData(Qt.BackgroundRole, color)

    # Page 3 Methods
    def to_sounds(self):
        self.stackedWidget.setCurrentIndex(2)
        start_mixer()
        for tono in self.tf.tonos:
            p = self.colorFrame.palette()
            p.setColor(self.colorFrame.backgroundRole(), tono.nota.color)
            self.colorFrame.setPalette(p)
            play_note(tono.tiempo, tono.nota.nota, tono.octava)
            if tono is self.tf.tonos[-1]:
                QtTest.QTest.qWait(tono.tiempo * 900)
                return
            QtTest.QTest.qWait(tono.tiempo * 1000)
        stop_mixer()
    def stop_sounds(self):
        pass



if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
