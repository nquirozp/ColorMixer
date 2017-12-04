from PyQt5 import uic
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QLabel, QFileDialog, QComboBox, QMessageBox, QShortcut
from music import s

window = uic.loadUiType('stackedwidget.ui')


class MainWindow(window[0], window[1]):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # PAGE 1
        self.pushButton_2.clicked.connect(lambda:
                                          self.setCurrentIndex(1))
        # PAGE 2
        self.pushButton_3.clicked.connect(lambda:
                                          self.setCurrentIndex(0))
        self.pushButton_4.clicked.connect(lambda:
                                          self.setCurrentIndex(2))


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
