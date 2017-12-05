from PyQt5 import uic, QtTest
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush, QPalette
from PyQt5.QtWidgets import \
    QApplication,\
    QListWidgetItem,\
    QTableWidgetItem,\
    QColorDialog,\
    QStyledItemDelegate,\
    QStyle
from music import start_mixer, play_note, TonoFactory

window = uic.loadUiType('stackedwidget.ui')


class custListWidgetItem(QListWidgetItem):
    def __lt__(self, other):
        tone_scale = {
            'C': 0,
            'C#/Db': 1,
            'D': 2,
            'D#/Eb': 3,
            'E': 2,
            'F': 3,
            'F#/Gb': 4,
            'G': 5,
            'G#/Ab': 5,
            'A': 6,
            'A#/Bb': 6,
            'B': 7,
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
        start_mixer()
        self.setupUi(self)
        self.tf = TonoFactory()

        # PAGE 1
        self.comboBox.addItems(note for note in self.tf.notas.keys())
        self.listWidget.setSortingEnabled(True)

        self.pushButton_2.clicked.connect(self.to_colors)
        self.toolButton.clicked.connect(self.add_to_right)
        self.toolButton_2.clicked.connect(self.add_to_left)

        # PAGE 2
        self.tableWidget.setHorizontalHeaderLabels(['Nota', 'Color'])
        self.tableWidget.horizontalHeader().show()
        self.tableWidget.cellDoubleClicked.connect(self.choose_color)

        self.pushButton_3.clicked.connect(lambda:
                                          self.setCurrentIndex(0))
        self.pushButton_4.clicked.connect(self.to_sounds)
        self.tableWidget.setItemDelegate(StyleDelegateForQTableWidget(self.tableWidget))

    # PAGE 1 Methods

    def add_to_right(self):
        nota = str(self.comboBox.currentText())
        octava = self.spinBox.value()
        tiempo = self.spinBox_2.value()
        if self.tf.new_tono(nota, octava, tiempo):
            self.listWidget.addItem(custListWidgetItem(str(self.tf.tonos[-1])))
            if octava == 10:
                combo_index = self.comboBox.currentIndex()
                self.label_3.setText('Nota(...)')
                if combo_index == self.comboBox.count() - 1:
                    self.comboBox.setCurrentIndex(0)
                else:
                    self.comboBox.setCurrentIndex(self.comboBox.currentIndex() + 1)
                QtTest.QTest.qWait(1000)
                self.label_3.setText('Nota')
                self.label_4.setText('Octava(...)')
                self.spinBox.setValue(1)
                QtTest.QTest.qWait(1000)
                self.label_4.setText('Octava')
            else:
                self.label_4.setText('Octava(...)')
                self.spinBox.setValue(self.spinBox.value() + 1)
                QtTest.QTest.qWait(1000)
                self.label_4.setText('Octava')
            self.spinBox_2.setValue(1)
        else:
            self.label_5.setText('No puedes agregar este tono!.')
            QtTest.QTest.qWait(2000)
            self.label_5.setText('')
        self.listWidget.sortItems()

    def add_to_left(self):
        print('called')
        row = self.listWidget.currentRow()
        if row == -1:
            row = self.listWidget.count() - 1

        self.listWidget.takeItem(row)
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
        self.setCurrentIndex(1)

    # Page 2 Methods
    def choose_color(self, row, column):
        if column == 1:
            color = QColorDialog.getColor()
            self.tf.notas[str(self.tableWidget.item(row, 0).text())].color = color
            self.tableWidget.item(row, column).setData(Qt.BackgroundRole, color)

    # Page 3 Methods
    def to_sounds(self):
        self.setCurrentIndex(2)
        for tono in self.tf.tonos:
            p = self.frame_5.palette()
            p.setColor(self.frame_5.backgroundRole(), tono.nota.color)
            self.frame_5.setPalette(p)
            play_note(tono.tiempo, tono.nota.nota, tono.octava)
            QtTest.QTest.qWait(tono.tiempo * 1000)

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
