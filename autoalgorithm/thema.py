
class auto_thema() :

    #algorithm용 변수
    high_peak = 0
    low_peak = 0
    average_price = 0

    def __init__(self, pyTrader):
        self.pyTrader = pyTrader

    def buying(self):
        self.pyTrader.send_order(0)

    def find_proper_stock(self):
        pass

    def start(self):
        pass

    def algorithm(self):
        """
        참조변수 : 주식코드, 주식수량, 주식평단가, 주식 high peak, 주식 low peak, 주식 평균
        :return: amount=주식수량, price=매수가격, sell=매매(1) or 매도(0)
        """
        