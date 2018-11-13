# -*- coding : utf-8 -*-
from time import *
from threading import *
from serial import *
from serial.tools.list_ports import *
from module.gui_module import *
import platform


# 定义参数字典
# dict_COM没有设置必要，本来就需要用字符串赋值
dict_Baudrate = {"9600": 9600, "14500": 14500}
dict_Bytesize = {"8": 8, "7": 7, "6": 6, "5": 5}
dict_Stopbits = {"1": 1, "1.5": 1.5, "2": 2}
dict_Parity = {"No": 'N', "Even": 'E', "Odd": "O", "Mark": "M", "Space": 'S'}

# 全局变量,球对象和桌子对象
ball = Ball()
ball_before=Ball()
ball_before.kernel_close_size=ball.kernel_close_size
ball_before.kernel_open_size=ball.kernel_open_size
ball_before.upper=ball.upper
ball_before.lower=ball.lower

desk = Desk()
paddle = Paddle()
cor=Coordinate()
ser = Serial()


def Serial_init():
    ser.port = Port.get()
    ser.baudrate = dict_Baudrate[Baudrate.get()]
    ser.bytesize = dict_Bytesize[Bytesize.get()]
    ser.stopbits = dict_Stopbits[Stopbits.get()]
    ser.parity = dict_Parity[Parity.get()]


def send2stm32(message):  # message应该是一个字符,从策略分析函数那里接收这个message参数
    ser.write(message)


# GUI初始化
tk = Tk()
tk.title("冰球机器人控制台  ——XYZ小组")
tk.maxsize(450, 380)  # （宽度，高度）
tk.minsize(450, 380)
tk.resizable(width=False, height=False)
Center(tk, 450, 380)
if 'Linux' not in platform.platform():
    tk.iconbitmap("./Matrial/Photo/launcher.ico")
canvas = Canvas(tk, width=450, height=380, bg='whitesmoke')
canvas.pack()

# 先定义frame，避免覆盖
label00 = LabelFrame(tk, height=150, width=130, text="串口设置", labelanchor='n', bg="whitesmoke")
id00 = canvas.create_window(80, 140, window=label00)  # 坐标是正中
label01 = LabelFrame(tk, height=60, width=420, text="总开关", labelanchor='n', bg="whitesmoke")
id01 = canvas.create_window(225, 30, window=label01)  # 坐标是正中

# 串口信息选择框
Port = StringVar()
port = ttk.Combobox(tk, width=7, textvariable=Port, state='readonly')
port['value'] = ('无串口')
port.current(0)

Baudrate = StringVar()  # 用来盛放从下拉栏中选择的字符串值
baudrate = ttk.Combobox(tk, width=7, textvariable=Baudrate, state='readonly')
baudrate['values'] = ("9600", "14500")  # 下拉栏的显示内容
baudrate.current(0)

Bytesize = StringVar()
bytesize = ttk.Combobox(tk, width=7, textvariable=Bytesize, state='readonly')
bytesize['value'] = ("8", "7", "6", "5")
bytesize.current(0)

Stopbits = StringVar()
stopbits = ttk.Combobox(tk, width=7, textvariable=Stopbits, state='readonly')
stopbits['value'] = ("1", "1.5", "2")
stopbits.current(0)

Parity = StringVar()
parity = ttk.Combobox(tk, width=7, textvariable=Parity, state='readonly')
parity['value'] = ("No", "Odd", "Even", "Mark", "Space")
parity.current(0)

id11 = canvas.create_window(100, 95, window=port)
id12 = canvas.create_window(100, 120, window=baudrate)
id13 = canvas.create_window(100, 145, window=bytesize)
id14 = canvas.create_window(100, 170, window=stopbits)
id15 = canvas.create_window(100, 195, window=parity)

# 串口信息的标签
# 要先定义，不然会覆盖，也可以用子配件、父配件来解决label10 = LabelFrame(tk,height=150,width=130,text="串口设置",labelanchor='n',bg="whitesmoke")#labelanchor属性解决定位问题（n:北，nw:西北，center:正中，其余类推）
label11 = Label(tk, text="串口号", bg="whitesmoke")
label12 = Label(tk, text="波特率", bg="whitesmoke")
label13 = Label(tk, text="数据位", bg="whitesmoke")
label14 = Label(tk, text="停止位", bg="whitesmoke")
label15 = Label(tk, text="奇偶位", bg="whitesmoke")

id21 = canvas.create_window(40, 95, window=label11)  # 一个字符大概20*20，标签自动把中点定位到指定的那个坐标
id22 = canvas.create_window(40, 120, window=label12)  # 由于一个标签也有高度，所以不能让标签们靠得太近，否则新加的会覆盖之前的（只要二者有一点点重合）
id23 = canvas.create_window(40, 145, window=label13)
id24 = canvas.create_window(40, 170, window=label14)
id25 = canvas.create_window(40, 195, window=label15)

camera_image = PhotoImage(file='./Matrial/Photo/camera.png')



label30 = LabelFrame(tk, height=150, width=120, text="点击进入监控模式", labelanchor='n',
                     bg="whitesmoke")  # labelanchor属性解决定位问题（n:北，nw:西北，center:正中，其余类推）
button31 = Button(tk, image=camera_image, width=100, height=120, command=lambda :Image_Processing(desk,paddle,ser))
button32 = Button(tk, text='摄像头设置', width=15, height=1, command=lambda: Cam_Setting(desk, ball, paddle))
id30 = canvas.create_window(215, 140, window=label30)
id31 = canvas.create_window(215, 145, window=button31)
id32 = canvas.create_window(360, 203, window=button32)
# id31.pack()


# 电机状态
Motor1_direction = StringVar()
Motor1_speed = StringVar()
Motor2_direction = StringVar()
Motor2_speed = StringVar()
Motor1_direction.set('左')
Motor1_speed.set('0')
Motor2_direction.set('左')
Motor2_speed.set('0')

label50 = LabelFrame(tk, height=120, width=150, text="电机状态", labelanchor='n',
                     bg="whitesmoke")  # labelanchor属性解决定位问题（n:北，nw:西北，center:正中，其余类推）
label51 = Label(tk, text="电机1方向:", bg="whitesmoke")
label52 = Label(tk, text="电机1档位:", bg="whitesmoke")
label53 = Label(tk, text="电机2方向:", bg="whitesmoke")
label54 = Label(tk, text="电机2档位:", bg="whitesmoke")
label55 = Label(tk, textvariable=Motor1_direction, width=3, bg="white")
label56 = Label(tk, textvariable=Motor1_speed, width=3, bg="white")
label57 = Label(tk, textvariable=Motor1_direction, width=3, bg="white")
label58 = Label(tk, textvariable=Motor1_speed, width=3, bg="white")

id50 = canvas.create_window(360, 125, window=label50)  # label坐标是正中央的坐标
id51 = canvas.create_window(330, 95, window=label51)
id52 = canvas.create_window(330, 120, window=label52)
id53 = canvas.create_window(330, 145, window=label53)
id54 = canvas.create_window(330, 170, window=label54)
id55 = canvas.create_window(400, 95, window=label55)
id56 = canvas.create_window(400, 120, window=label56)
id57 = canvas.create_window(400, 145, window=label57)
id58 = canvas.create_window(400, 170, window=label58)

# 总开关
Switch_mode = StringVar()
Switch_mode.set("开始串口通信")


def Start_serial_launcher():
    th = Thread(target=Start_serial, args=())
    th.setDaemon(TRUE)
    th.start()


Message = 'a'


def Start_serial():
    global Message
    if Switch_mode.get() == "开始串口通信":
        Switch_mode.set("停止串口通信")
        print("切换到开始")
        try:
            Serial_init()  # 设置串口信息之后inwaiting会清空
            ser.open()
        except:
            showwarning("错误！", "检查串口设置并重置总开关")
            
        '''while 1:  # 不必设置全局变量cansend，因为并行线程如果进入关闭模式，会直接关闭串口，这个线程会跟着发送错误然后退出
            try:
                ser.write(bytes(Message, encoding='gbk'))  # message是个字符，由策略函数修改
                sleep(0.01)  # 暂停0.1秒，等待单片机
            except:
                if ser.isOpen():  # 区分两种情形
                    showwarning("错误！", "检查串口设置并重置总开关")
                break'''
    elif Switch_mode.get() == "停止串口通信":
        Switch_mode.set("开始串口通信")
        print("切换到停止")
        ser.close()


button41 = Button(tk, textvariable=Switch_mode, width=25,
                  command=Start_serial_launcher)  # button启动的函数不能接受参数，此时使用lambda，先计算函数结果，然后把结果强制重组为一个匿名简单函数
id41 = canvas.create_window(325, 35, window=button41)

# 搜索串口
searching_status = StringVar()
searching_status.set('搜索串口')


def Searching_port_launcher():
    th = Thread(target=Searching_port)
    th.setDaemon(TRUE)
    th.start()


def Searching_port():
    searching_status.set('搜索中...')
    port['value'] = ()
    temp_port = []
    port_list = list(comports())  # 这是一个二维list，每一个有效串口都对应一个子list，每个子list的第一个元素是‘COMx'
    if len(port_list) == 0:
        searching_status.set('搜索串口')
        showinfo("提示", "未找到可用串口")
        port['value'] = ('无串口')
        port.current(0)
    else:
        for a_port in port_list:
            temp_port.append(a_port[0])
            pass
        port['value'] = tuple(temp_port)
        
        searching_status.set('搜索串口')
        try:
            port.current(0)
        except:
            port['value'] = ('无串口')
            pass


button61 = Button(tk, textvariable=searching_status, width=25,
                  command=Searching_port_launcher)  # button启动的函数不能接受参数，此时使用lambda，先计算函数结果，然后把结果强制重组为一个匿名简单函数
id61 = canvas.create_window(120, 35, window=button61)

# 插图
if 'Linux' in platform.platform():
    label71 = Label(tk, text="Le vent se lève", font=("Kunstler Script", 30), bg='whitesmoke')
    id71 = canvas.create_window(150, 260, window=label71)
    label72 = Label(tk, text="il faut tenter de vivre", font=("Kunstler Script", 30), bg='whitesmoke')
    id72 = canvas.create_window(245, 320, window=label72)
else:
    label71 = Label(tk, text="Le vent se lève", font=("Kunstler Script", 50), bg='whitesmoke')
    id71 = canvas.create_window(150, 260, window=label71)
    label72 = Label(tk, text="il faut tenter de vivre", font=("Kunstler Script", 50), bg='whitesmoke')
    id72 = canvas.create_window(245, 320, window=label72)

##################################################




button100 = Button(tk, text='测试', width=5,
                  command=Searching_port_launcher)  # button启动的函数不能接受参数，此时使用lambda，先计算函数结果，然后把结果强制重组为一个匿名简单函数
id100 = canvas.create_window(350, 250, window=button100)

##################################################




tk.mainloop()
