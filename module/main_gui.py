from time import *
from threading import *
from serial import *
from serial.tools.list_ports import *
from module.gui_module import *
from module.func import *
import platform
import tkinter.ttk as ttk

class main_gui(MySerial):
    def __init__(self,ball,desk,paddle):
        super().__init__()
        # GUI初始化
        self.tk = Tk()
        self.ball=ball
        self.desk=desk
        self.paddle=paddle

    def init(self):

        self.Port = StringVar()
        self.Baudrate = StringVar()  # 用来盛放从下拉栏中选择的字符串值
        self.Bytesize = StringVar()
        self.Stopbits = StringVar()
        self.Parity = StringVar()
        self.Switch_mode = StringVar()


        self.tk.title("冰球机器人控制台  ——XYZ小组")
        self.tk.maxsize(450, 380)  # （宽度，高度）
        self.tk.minsize(450, 380)
        self.tk.resizable(width=False, height=False)
        Center(self.tk, 450, 380)
        if 'Linux' not in platform.platform():
            self.tk.iconbitmap("./Matrial/Photo/launcher.ico")
        self.canvas = Canvas(self.tk, width=450, height=380, bg='whitesmoke')
        self.canvas.pack()

        # 先定义frame，避免覆盖
        self.label00 = LabelFrame(self.tk, height=150, width=130, text="串口设置", labelanchor='n', bg="whitesmoke")
        self.id00 = self.canvas.create_window(80, 140, window=self.label00)  # 坐标是正中
        self.label01 = LabelFrame(self.tk, height=60, width=420, text="总开关", labelanchor='n', bg="whitesmoke")
        self.id01 = self.canvas.create_window(225, 30, window=self.label01)  # 坐标是正中

        # 串口信息选择框

        self.port = ttk.Combobox(self.tk, width=7, textvariable=self.Port, state='readonly')
        self.baudrate = ttk.Combobox(self.tk, width=7, textvariable=self.Baudrate, state='readonly')
        self.stopbits = ttk.Combobox(self.tk, width=7, textvariable=self.Stopbits, state='readonly')
        self.bytesize = ttk.Combobox(self.tk, width=7, textvariable=self.Bytesize, state='readonly')
        self.parity = ttk.Combobox(self.tk, width=7, textvariable=self.Parity, state='readonly')

        self.port['value'] = ('无串口')
        self.port.current(0)

        self.baudrate['values'] = ("9600", "14500")  # 下拉栏的显示内容
        self.baudrate.current(0)

        self.bytesize['value'] = ("8", "7", "6", "5")
        self.bytesize.current(0)

        self.stopbits['value'] = ("1", "1.5", "2")
        self.stopbits.current(0)

        self.parity['value'] = ("No", "Odd", "Even", "Mark", "Space")
        self.parity.current(0)

        self.id11 = self.canvas.create_window(100, 95, window=self.port)
        self.id12 = self.canvas.create_window(100, 120, window=self.baudrate)
        self.id13 = self.canvas.create_window(100, 145, window=self.bytesize)
        self.id14 = self.canvas.create_window(100, 170, window=self.stopbits)
        self.id15 = self.canvas.create_window(100, 195, window=self.parity)

        # 串口信息的标签
        # 要先定义，不然会覆盖，也可以用子配件、父配件来解决self.label10 = LabelFrame(tk,height=150,width=130,text="串口设置",labelanchor='n',bg="whitesmoke")#labelanchor属性解决定位问题（n:北，nw:西北，center:正中，其余类推）
        self.label11 = Label(self.tk, text="串口号", bg="whitesmoke")
        self.label12 = Label(self.tk, text="波特率", bg="whitesmoke")
        self.label13 = Label(self.tk, text="数据位", bg="whitesmoke")
        self.label14 = Label(self.tk, text="停止位", bg="whitesmoke")
        self.label15 = Label(self.tk, text="奇偶位", bg="whitesmoke")

        self.id21 = self.canvas.create_window(40, 95, window=self.label11)  # 一个字符大概20*20，标签自动把中点定位到指定的那个坐标
        self.id22 = self.canvas.create_window(40, 120, window=self.label12)  # 由于一个标签也有高度，所以不能让标签们靠得太近，否则新加的会覆盖之前的（只要二者有一点点重合）
        self.id23 = self.canvas.create_window(40, 145, window=self.label13)
        self.id24 = self.canvas.create_window(40, 170, window=self.label14)
        self.id25 = self.canvas.create_window(40, 195, window=self.label15)

        self.camera_image = PhotoImage(file='./Matrial/Photo/camera.png')
        self.label30 = LabelFrame(self.tk, height=150, width=120, text="点击进入监控模式", labelanchor='n',
                             bg="whitesmoke")  # self.labelanchor属性解决定位问题（n:北，nw:西北，center:正中，其余类推）
        self.button31 = Button(self.tk, image=self.camera_image, width=100, height=120, command=lambda: Image_Processing(self.desk,self.paddle,self))
        self.button32 = Button(self.tk, text='摄像头设置', width=15, height=1, command=lambda: Cam_Setting(self.desk, self.ball, self.paddle))
        self.id30 = self.canvas.create_window(215, 140, window=self.label30)
        self.id31 = self.canvas.create_window(215, 145, window=self.button31)
        self.id32 = self.canvas.create_window(360, 203, window=self.button32)
        # self.id31.pack()


        # 电机状态
        self.Motor1_direction = StringVar()
        self.Motor1_speed = StringVar()
        self.Motor2_direction = StringVar()
        self.Motor2_speed = StringVar()
        self.Motor1_direction.set('左')
        self.Motor1_speed.set('0')
        self.Motor2_direction.set('左')
        self.Motor2_speed.set('0')

        self.label50 = LabelFrame(self.tk, height=120, width=150, text="电机状态", labelanchor='n',
                             bg="whitesmoke")  # self.labelanchor属性解决定位问题（n:北，nw:西北，center:正中，其余类推）
        self.label51 = Label(self.tk, text="电机1方向:", bg="whitesmoke")
        self.label52 = Label(self.tk, text="电机1档位:", bg="whitesmoke")
        self.label53 = Label(self.tk, text="电机2方向:", bg="whitesmoke")
        self.label54 = Label(self.tk, text="电机2档位:", bg="whitesmoke")
        self.label55 = Label(self.tk, textvariable=self.Motor1_direction, width=3, bg="white")
        self.label56 = Label(self.tk, textvariable=self.Motor1_speed,     width=3, bg="white")
        self.label57 = Label(self.tk, textvariable=self.Motor1_direction, width=3, bg="white")
        self.label58 = Label(self.tk, textvariable=self.Motor1_speed,     width=3, bg="white")

        self.id50 = self.canvas.create_window(360, 125, window=self.label50)  # self.label坐标是正中央的坐标
        self.id51 = self.canvas.create_window(330, 95,  window=self.label51)
        self.id52 = self.canvas.create_window(330, 120, window=self.label52)
        self.id53 = self.canvas.create_window(330, 145, window=self.label53)
        self.id54 = self.canvas.create_window(330, 170, window=self.label54)
        self.id55 = self.canvas.create_window(400, 95,  window=self.label55)
        self.id56 = self.canvas.create_window(400, 120, window=self.label56)
        self.id57 = self.canvas.create_window(400, 145, window=self.label57)
        self.id58 = self.canvas.create_window(400, 170, window=self.label58)

        # 总开关

        self.Switch_mode.set("开始串口通信")



        self.button41 = Button(self.tk, textvariable=self.Switch_mode, width=25,command=self.Start_serial_launcher)  # button启动的函数不能接受参数，此时使用lambda，先计算函数结果，然后把结果强制重组为一个匿名简单函数
        self.id41 = self.canvas.create_window(325, 35, window=self.button41)

        # 搜索串口
        self.searching_status = StringVar()
        self.searching_status.set('搜索串口')

        self.button61 = Button(self.tk, textvariable=self.searching_status, width=25,command=self.Searching_port_launcher)  # button启动的函数不能接受参数，此时使用lambda，先计算函数结果，然后把结果强制重组为一个匿名简单函数
        self.id61 = self.canvas.create_window(120, 35, window=self.button61)

        # 插图
        if 'Linux' in platform.platform():
            self.label71 = Label(self.tk, text="Le vent se lève", font=("Kunstler Script", 30), bg='whitesmoke')
            self.id71 = self.canvas.create_window(150, 260, window=self.label71)
            self.label72 = Label(self.tk, text="il faut tenter de vivre", font=("Kunstler Script", 30), bg='whitesmoke')
            self.id72 = self.canvas.create_window(245, 320, window=self.label72)
        else:
            self.label71 = Label(self.tk, text="Le vent se lève", font=("Kunstler Script", 50), bg='whitesmoke')
            self.id71 = self.canvas.create_window(150, 260, window=self.label71)
            self.label72 = Label(self.tk, text="il faut tenter de vivre", font=("Kunstler Script", 50), bg='whitesmoke')
            self.id72 = self.canvas.create_window(245, 320, window=self.label72)

    def Searching_port_launcher(self):
        self.th = Thread(target=self.Searching_port)
        self.th.setDaemon(True)
        self.th.start()

    def Searching_port(self):
        self.searching_status.set('搜索中...')
        self.port['value'] = ()
        self.temp_port = []
        self.port_list = list(comports())  # 这是一个二维list，每一个有效串口都对应一个子list，每个子list的第一个元素是‘COMx'
        if len(self.port_list) == 0:
            self.searching_status.set('搜索串口')
            showinfo("提示", "未找到可用串口")
            self.port['value'] = ('无串口')
            self.port.current(0)
        else:
            for a_port in self.port_list:
                self.temp_port.append(a_port[0])
                pass
            self.port['value'] = tuple(self.temp_port)

            self.searching_status.set('搜索串口')
            try:
                self.port.current(0)
            except:
                self.port['value'] = ('无串口')
                pass