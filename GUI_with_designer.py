import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi("python/Perso/testUI.ui", self)


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
print(dir(window.gra))
window.testField.setText('test2')
window.show()
app.exec_()
