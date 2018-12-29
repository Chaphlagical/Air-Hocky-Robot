# -*- coding : utf-8 -*-
from time import *
from threading import *
from serial import *
from serial.tools.list_ports import *
from module.gui_module import *
from module.main_gui import *
import platform

# 全局变量,球对象和桌子对象
ball = Ball()
desk = Desk()
paddle = Paddle()








if __name__=="__main__":
    gui=main_gui(ball,desk,paddle)
    gui.init()
    gui.tk.mainloop()
    while True:
        pass


