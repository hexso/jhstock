# coding: utf-8

from PyQt5 import uic
from pykiwoom.wrapper import *
import pytrader
import find_stock_with_algorithm


form_class = uic.loadUiType("main.ui")[0]

class MainWindow(QMainWindow, form_class):

    fps = find_stock_with_algorithm.MainWindow()
    auto = pytrader.MyWindow()
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.show()

        #버튼 설정
        self.find_patterned_stock_btn.clicked.connect(self.call_find_patterned_stock)
        self.auto_trade_btn.clicked.connect(self.auto_trade)


    def call_find_patterned_stock(self):
        self.fps.show()
        self.close()
    def auto_trade(self):
        self.auto.show()
        #self.auto.start()
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    test = MainWindow()
    test.show()
    app.exec_()



