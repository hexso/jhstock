# coding: utf-8

import sys, time
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt, QTimer, QTime
from PyQt5 import uic
from pykiwoom.kiwoom import *
from pykiwoom.wrapper import *
import codecs
import pytrader


form_class = uic.loadUiType("find_stock_with_algorithm.ui")[0]
ALGORITHM = ["테마주 찾기","작전주"]

class MainWindow(QMainWindow, form_class):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        #UI 연결
        self.strategyList.addItems(ALGORITHM)
        self.startBtn.clicked.connect(self.start)
        self.stopBtn.clicked.connect(self.stop)
    def start(self):
        self.strategy = self.strategyList.currentText()
        self.showProcess.setText("찾는중")

    def stop(self):
        self.showProcess.setText("종료")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    test = MainWindow()
    test.show()
    app.exec_()



