from pykiwoom.kiwoom import *
from pykiwoom.wrapper import *
import logging

import mylog
a=mylog.mylogging()


@a.logBuying
def hey(a,b):
    print(a,b)

if __name__ == '__main__':
    '''
    aa = logging.getLogger("asd")
    aa.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(formatter)
    aa.addHandler(stream_hander)

    aa.info("%d",1)
    '''

    hoga_type_table = {'지정가': "00", '시장가': "03", '최유리지정가': "06", '최우선지정가': "07"}
    print(hoga_type_table['지정가'])