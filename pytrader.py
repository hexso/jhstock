"""
QtDesigner로 만든 UI와 해당 UI의 위젯에서 발생하는 이벤트를 컨트롤하는 클래스

author: Jongyeol Yang
last edit: 2017. 02. 23
"""


from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt, QTimer, QTime
from PyQt5 import uic
from pykiwoom.kiwoom import *
from pykiwoom.wrapper import *
from mylog import mylogging

AUTO_TRADE_TIME = 2100 # 자동매매시간 21초
AUTO_VIEW_MYACCOUNT = 1000 # 일정 시간마다 내 잔고 조회
LOGINID = '0'
PASSWORD = '0000'
CERTIFICATE_PASSWORD = '0000'
STRATEGY_LIST = ["테마주매매"]

form_class = uic.loadUiType("pytrader.ui")[0]

class MyWindow(QMainWindow, form_class):
    my_log = mylogging()

    def __init__(self):
        super().__init__()
        self.setupUi(self)

    #account.xt 파일에 ID,PASSWORD, 공인인증서 비밀번호를 적는다.
        with open("account.txt", 'r') as f:
            info= f.readlines()
        global LOGINID
        global PASSWORD
        global CERTIFICATE_PASSWORD
        LOGINID = info[0]
        PASSWORD = info[1]
        CERTIFICATE_PASSWORD = info[2]



        self.login_btn.clicked.connect(self.kiwoom_login)
        self.strategyComboBox.addItems(STRATEGY_LIST)

    def kiwoom_login(self):
        self.kiwoom = Kiwoom()
        self.kiwoom.comm_connect()
        self.wrapper = KiwoomWrapper(self.kiwoom)
        if self.kiwoom.get_login_info("GetServerGubun"):
            self.server_gubun = "실제운영"
        else:
            self.server_gubun = "모의투자"

        #self.code_list = self.kiwoom.get_code_list("005940")
        self.setAccountComboBox()  # 계좌번호 조회에서 GUI에 셋팅

    def start(self):
        # 메인 타이머
        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.timeout)

        # 자동 주문
        self.timer_stock = QTimer(self)
        self.timer_stock.start(AUTO_TRADE_TIME)  ## 21초마다 자동주문
        self.timer_stock.timeout.connect(self.timeout)

        # 잔고 및 보유종목 조회 타이머
        self.inquiryTimer = QTimer(self)
        self.inquiryTimer.start(AUTO_VIEW_MYACCOUNT)
        self.inquiryTimer.timeout.connect(self.timeout)

        self.inquiryBtn.clicked.connect(self.inquiry_balance)

        self.in_processing = False

        # 자동 선정 종목 리스트 테이블 설정
        #self.set_automated_stocks()
        #self.inquiry_balance()

    def setAccountComboBox(self):
        """ accountComboBox에 계좌번호를 설정한다. """
        try:
            cnt = int(self.kiwoom.get_login_info("ACCOUNT_CNT"))
            accountList = self.kiwoom.get_login_info("ACCNO").split(';')
            self.accountComboBox.addItems(accountList[0:cnt])
        except (KiwoomConnectError, ParameterTypeError, ParameterValueError) as e:
            self.show_dialog('Critical', e)


################수정해야함
    @my_log.logBuying
    def send_order(self, code, qty, price, order_type = 1, hoga_type = "03"):
        """ 키움서버로 주문정보를 전송한다. """
        order_type_table = {'신규매수': 1, '신규매도': 2, '매수취소': 3, '매도취소': 4}
        hoga_type_table = {'지정가': "00", '시장가': "03"}

        account = self.accountComboBox.currentText()

        try:
            self.kiwoom.send_order("수동주문", "0101", account, order_type, code, qty, price, hoga_type, "")
        except (ParameterTypeError, KiwoomProcessingError) as e:
            self.show_dialog('Critical', e)

    def inquiry_balance(self):
        """ 예수금상세현황과 계좌평가잔고내역을 요청후 테이블에 출력한다. """
        self.in_processing = True
        #self.inquiryTimer.stop()
        #self.timer_stock.stop()

        try:
            # 예수금상세현황요청
            self.kiwoom.set_input_value("계좌번호", self.accountComboBox.currentText())
            self.kiwoom.set_input_value("비밀번호", "0000")
            self.kiwoom.comm_rq_data("예수금상세현황요청", "opw00001", 0, "2000")

            # 계좌평가잔고내역요청 - opw00018 은 한번에 20개의 종목정보를 반환
            self.kiwoom.set_input_value("계좌번호", self.accountComboBox.currentText())
            self.kiwoom.set_input_value("비밀번호", "0000")
            self.kiwoom.comm_rq_data("계좌평가잔고내역요청", "opw00018", 0, "2000")
            while self.kiwoom.inquiry == '2':
                time.sleep(0.2)
                self.kiwoom.set_input_value("계좌번호", self.accountComboBox.currentText())
                self.kiwoom.set_input_value("비밀번호", "0000")
                self.kiwoom.comm_rq_data("계좌평가잔고내역요청", "opw00018", 2, "2")
        except (ParameterTypeError, ParameterValueError, KiwoomProcessingError) as e:
            self.show_dialog('Critical', e)

        # accountEvaluationTable 테이블에 정보 출력

        item = QTableWidgetItem(self.kiwoom.data_opw00001)
        item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
        self.accountEvaluationTable.setItem(0, 0, item)

        for i in range(1, 6):
            item = QTableWidgetItem(self.kiwoom.data_opw00018['account_evaluation'][i-1])
            item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            self.accountEvaluationTable.setItem(0, i, item)

        self.accountEvaluationTable.resizeRowsToContents()

        # Item list
        item_count = len(self.kiwoom.data_opw00018['stocks'])
        self.stocksTable.setRowCount(item_count)

        with open('../data/stocks_in_account.txt', 'wt', encoding='utf-8') as f_stock:
            f_stock.write('%d\n'%self.kiwoom.data_opw00001)
            for i in range(item_count):
                row = self.kiwoom.data_opw00018['stocks'][i]
                for j in range(len(row)-1):
                    f_stock.write('%s,'%row[j].replace(',', ''))
                    if j == len(row)-2:
                        f_stock.write('%s,'%row[-1])
                    item = QTableWidgetItem(row[j])
                    item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
                    self.stocksTable.setItem(i, j, item)
                f_stock.write('\n')

        self.stocksTable.resizeRowsToContents()

        # 데이터 초기화
        self.kiwoom.opw_data_reset()

        self.in_processing = False
        # inquiryTimer 재시작
        #self.inquiryTimer.start(1000*10)
        #self.timer_stock.start(1000*100)


    # 경고창
    def show_dialog(self, grade, error):
        grade_table = {'Information': 1, 'Warning': 2, 'Critical': 3, 'Question': 4}

        dialog = QMessageBox()
        dialog.setIcon(grade_table[grade])
        dialog.setText(error.msg)
        dialog.setWindowTitle(grade)
        dialog.setStandardButtons(QMessageBox.Ok)
        dialog.exec_()

    def set_automated_stocks(self):
        file_list = ["../data/sell_list.txt", "../data/buy_list.txt"]
        automated_stocks = []

        try:
            for file in file_list:
                # utf-8로 작성된 파일을
                # cp949 환경에서 읽기위해서 encoding 지정
                with open(file, 'rt', encoding='utf-8') as f:
                    stocks_list = f.readlines()
                    automated_stocks += stocks_list
        except Exception as e:
            print(e)
            e.msg = "set_automated_stocks() 에러"
            self.show_dialog('Critical', e)
            return

        # 테이블 행수 설정
        cnt = len(automated_stocks)
        self.automatedStocksTable.setRowCount(cnt)

        # 테이블에 출력
        for i in range(cnt):
            stocks = automated_stocks[i].split(';')
            for j in range(len(stocks)):
                if j == 1:
                    name = self.kiwoom.get_master_code_name(stocks[j].rstrip())
                    item = QTableWidgetItem(name)
                else:
                    item = QTableWidgetItem(stocks[j].rstrip())
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)
                self.automatedStocksTable.setItem(i, j, item)
        self.automatedStocksTable.resizeRowsToContents()

    def automatic_order(self):
        file_list = ["../data/sell_list.txt", "../data/buy_list.txt"]
        hoga_type_table = {'지정가': "00", '시장가': "03"}
        account = self.accountComboBox.currentText()
        automated_stocks = []
        self.in_processing = True
        # 파일읽기
        try:
            for file in file_list:
                # utf-8로 작성된 파일을
                # cp949 환경에서 읽기위해서 encoding 지정
                with open(file, 'rt', encoding='utf-8') as f:
                    stocks_list = f.readlines()
                    automated_stocks += stocks_list
        except Exception as e:
            print(e)
            #e.msg = "automatic_order() 에러"
            #self.show_dialog('Critical', e)
            return

        cnt = len(automated_stocks)

        # 주문하기
        buy_result = []
        sell_result = []

        for i in range(cnt):
            time.sleep(0.3)
            stocks = automated_stocks[i].split(';')

            code = stocks[1]
            hoga = stocks[2]
            qty = stocks[3]
            price = stocks[4]

            try:
                if stocks[5].rstrip() == '매수전':
                    self.kiwoom.send_order("자동매수주문", "0101", account, 1, code, int(qty), int(price), hoga_type_table[hoga], "")
                    print("order_no: ", self.kiwoom.order_no)

                    # 주문 접수시
                    if self.kiwoom.order_no:
                        buy_result += automated_stocks[i].replace("매수전", "매수완료")
                        self.kiwoom.order_no = ""
                    # 주문 미접수시
                    else:
                        buy_result += automated_stocks[i]

                # 참고: 해당 종목을 현재도 보유하고 있다고 가정함.
                elif stocks[5].rstrip() == '매도전':
                    self.kiwoom.send_order("자동매도주문", "0101", account, 2, code, int(qty), 0, hoga_type_table[hoga], "")
                    print("order_no: ", self.kiwoom.order_no)

                    # 주문 접수시
                    if self.kiwoom.order_no:
                        sell_result += automated_stocks[i].replace("매도전", "매도완료")
                        self.kiwoom.order_no = ""
                    # 주문 미접수시
                    else:
                        sell_result += automated_stocks[i]
                elif stocks[5].rstrip() == '매수완료':
                    buy_result += automated_stocks[i]
                elif stocks[5].rstrip() == '매도완료':
                    sell_result += automated_stocks[i]

            except (ParameterTypeError, KiwoomProcessingError) as e:
                #self.show_dialog('Critical', e)
                print(e)

        # 잔고및 보유종목 디스플레이 갱신
        self.inquiry_balance()

        # 결과저장하기
        for file, result in zip(file_list, [sell_result, buy_result]):
            with open(file, 'wt', encoding='utf-8') as f:
                for data in result:
                    f.write(data)
        self.in_processing = False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
