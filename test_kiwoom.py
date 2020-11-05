from pykiwoom.kiwoom import *
from pykiwoom.wrapper import *
import logging
import mylog
a=mylog.mylogging()


@a.logBuying
def hey(a,b):
    print(a,b)

if __name__ == '__main__':



    hey(1,2)