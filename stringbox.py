from PyQt5.QtWidgets import QSpinBox
from music import TonoFactory

_tf = TonoFactory()


class StringBox(QSpinBox):
    def __init__(self, parent=None):
        super(StringBox, self).__init__(parent)
        strings = ['HEAD']
        for key in _tf.notas.keys():
            strings.append(key)
        strings.append('TAIL')
        self.setStrings(strings)
        self.setValue(1)

    def strings(self):
        return self._strings

    def setStrings(self, strings):
        strings = list(strings)
        self._strings = tuple(strings)
        self._values = dict(zip(strings, range(len(strings))))
        self.setRange(0, len(strings) - 1)

    def textFromValue(self, value):
        return self._strings[int(value)]

    def valueFromText(self, text):
        return self._values[text]

    def stepBy(self, step):
        if self.value() == 1 and step == 1:
            self.setValue(self.maximum())
        elif self.value() == self.maximum() - 1 and step == -1:
            self.setValue(0)
        QSpinBox.stepBy(self, step * -1)
