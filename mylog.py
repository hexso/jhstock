import logging

from datetime import datetime

class mylogging():
    def __init__(self):
        self.mylogger = logging.getLogger("my")
        self.mylogger.setLevel(logging.INFO)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        self.stream_hander = logging.StreamHandler()
        self.stream_hander.setFormatter(self.formatter)
        self.mylogger.addHandler(self.stream_hander)

        self.today_date = datetime.today().strftime("%Y%m%d")

        self.file_handler = logging.FileHandler(self.today_date)
        self.mylogger.addHandler(self.file_handler)

    def logBuying(self, call_function):
        def wrapper(*args,**kwargs):
            func=list(args)
            print(func[0])
            self.mylogger.info("hey" + str(func[0]) + str(func[1]))
            return call_function(*args,**kwargs)
        return wrapper
