from pykiwoom.kiwoom import *
from pykiwoom.wrapper import *
import logging


class ab():
    def __init__(self,a,b):
        print(a)


def my_log(original_function):
    def inner_function():
        print("what?")
        return original_function()
    print("is in logging")
    return inner_function

if __name__ == '__main__':

    @my_log
    def hey():
        print("haha")

    hey()
    c=ab(1,2)