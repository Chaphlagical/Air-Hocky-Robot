# -*- coding:utf-8 -*-
import cv2 as cv
import numpy as np
import math
from tkinter.messagebox import *
from serial import *
from serial.tools.list_ports import *
from threading import *
import platform
import time

# 桌子类
class Desk:
    def __init__(self, id=-1):
        if 'Linux' in platform.platform():
            self.id = id  # 摄像头编号
        else:
            self.id=1
        self.frame = None  # 帧
        self.capture = None  # 视频流
        self.corner_points = {0: (0, 0), 1: (0, 0), 2: (0, 0), 3: (0, 0)}  # 角点字典
        self.frame_transformed = None  # 变换后的帧
    
    def set_capture(self):
        self.capture = cv.VideoCapture(self.id)
        self.capture.set(cv.CAP_PROP_FPS,60)
    
    def release_capture(self):
        self.capture.release()
    
    def judge_flag(self):  # 判断角点字典是否填满,作为跳出循环的标志
        count = 0
        for index in self.corner_points.keys():
            if self.corner_points[index]!= (0, 0):
                count += 1
        if count == 4:
            return True
        else:
            return False
    
    def transform(self, mode):  # 透视变换,输入帧生成frame_transformed
        if self.judge_flag() == False:
            self.frame_transformed = self.frame.copy()
            return
        try:
            if mode == True:
                try:
                    rows, cols, ch = self.frame.shape  # 行，列，深度
                except:
                    rows, cols = self.frame.shape  # 兼容二值化图像
                pts1 = np.float32(
                    [self.corner_points[0], self.corner_points[1], self.corner_points[2], self.corner_points[3]])
                pts2 = np.float32([[0, 0], [0, 1000], [600, 1000], [600, 0]])
                M = cv.getPerspectiveTransform(pts1, pts2)
                self.frame_transformed = cv.warpPerspective(self.frame, M, (600, 1000))
            else:
                pass
        except Exception as error:
            showerror("Error！", str(error) + "\nPlease check!")
    
    def get_frame(self):  # 获取帧
        try:
            ret, self.frame = self.capture.read()
            self.transform(True)
        except Exception as error:
            showerror("错误！", str(error) + "\nPlease check!")
    
    def clear_corner_points_dict(self):  # 清空角点字典
        self.corner_points = {0: (0, 0), 1: (0, 0), 2: (0, 0), 3: (0, 0)}
    
    def set_corner_dict(self):  # 设置角点字典
        self.set_capture()
        self.clear_corner_points_dict()
        self.get_frame()
        
        def MouseCallBackfunc(event, x, y, flags, param):  # 设置触发响应函数
            if event == cv.EVENT_LBUTTONDBLCLK:  # 双击左键触发
                cv.circle(param, (x, y), 3, (255, 0, 0), 5)  # 画蓝点
                for index in self.corner_points.keys():  # 筛选第一个非(0,0)的元素进行赋值
                    if self.corner_points[index] == (0, 0):
                        self.corner_points[index] = (x, y)
                        return
        
        showinfo("角点设置提示", "请按照左上-右上-右下-左下的顺序双击左键你要变换区域的四个顶点")
        cv.destroyAllWindows()
        cv.namedWindow('camera setting')
        cv.setMouseCallback('camera setting', MouseCallBackfunc, self.frame)
        while (True):
            cv.imshow('camera setting', self.frame)
            if cv.waitKey(1) & 0xff == ord('q') or self.judge_flag():
                if self.judge_flag() != True:
                    if askokcancel("提示", "你所选择的角点将不会被保存！\n确定继续吗？"):
                        self.clear_corner_points_dict()
                        cv.destroyAllWindows()
                else:
                    cv.destroyAllWindows()
                    showinfo("提示", "角点设置成功！")
                self.capture.release()
                break


# 定义球类
class Ball:
    def __init__(self, frame=None):
        self.frame_original = frame  # 初始图像
        self.frame_segmentation = None  # 颜色分割后的图像
        self.frame_thresh = None  # 二值化后的图像
        self.frame_preprocess = None  # 预处理后的图像
        self.frame_locate = None  # 目标定位标定
        self.frame_track = None  # 目标追踪处理后的图像
        self.radius = 0  # 目标外接球半径
        self.x = 0  # 目标质心的x坐标测量
        self.y = 0  # 目标质心的y坐标测量
        self.vx = 0  # 目标运动的x速度
        self.vy = 0  # 目标运动的y速度
        self.uint_x = 0  # 目标运动单位方向的x分量
        self.uint_y = 0  # 目标运动单位方向的y分量
        self.kernel_open_size = 4  # 开运算核
        self.kernel_close_size = 3  # 闭运算核
        self.lower = np.array([115, 50, 50])  # 蓝色阈值的下限
        self.upper = np.array([125, 255, 255])  # 蓝色阈值的上限
        self.corner_points = {0: (0, 0), 1: (0, 0),  # 角点字典
                              2: (0, 0), 3: (0, 0)}
        self.time = 0  # 两帧停留的时间
        self.sec = 0
        self.pre_x = None#上一次x
        self.pre_y = None#上一次y
        self.ppre_x = None#上上次x
        self.ppre_y = None#上上次y
        self.pre_vx = None  # 上一次x
        self.pre_vy = None  # 上一次y
        self.ppre_vx = None  # 上上次x
        self.ppre_vy = None  # 上上次y
        self.rx=None
        self.ry=None
        self.correct=None
    
    def reflesh(self, frame):  # 刷新帧
        self.frame_original = frame.copy()
    
    def preprocess(self, mode, mode_=False):  # 预处理,利用输入的帧生成frame_thresh,frame_segmentation,frame_preprocess
        try:
            '''颜色阈值'''
            start=time.time()
            hsv = cv.cvtColor(self.frame_original, cv.COLOR_BGR2HSV)  # 颜色空间转化
            self.frame_thresh = cv.inRange(hsv, self.lower, self.upper)  # 取掩模
            if mode_==True:
                self.frame_segmentation = cv.bitwise_and(self.frame_original, self.frame_original,
                                                         mask=self.frame_thresh)  # 按位运算
            self.frame_preprocess = cv.morphologyEx(self.frame_thresh, cv.MORPH_OPEN,
                                                    np.ones((self.kernel_open_size, self.kernel_open_size),
                                                            np.uint8))  # 开运算
            self.frame_preprocess = cv.morphologyEx(self.frame_preprocess, cv.MORPH_CLOSE,
                                                    np.ones((self.kernel_close_size, self.kernel_close_size),
                                                            np.uint8))  # 闭运算
            mid=time.time()
            print("预处理：",mid-start)
            
            '''轮廓检测'''
            image, contours, hierarchy = cv.findContours(self.frame_preprocess, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
            #area = 0
            contour=None
            for i in contours:  # 筛选最大面积轮廓
                if cv.contourArea(i) > 100:
                    contour=i
                    break
            
            (self.x, self.y), self.radius = cv.minEnclosingCircle(contour)
            self.radius = int(self.radius)
            self.x = round(self.x)
            self.y = round(self.y)
            mid_=time.time()
            print("轮廓检测：",mid_-mid)
            '''轨迹计算mode为True开启'''
            if mode == True:
                try:
                    real = np.matmul(np.array([self.x, self.y,1]), self.correct)
                    self.rx=int(real[0]);self.ry=int(real[1])
                except:
                    self.rx=self.x;self.ry=self.y
                try:
                    self.vx = (self.rx - self.pre_x)
                    self.vy = (self.ry - self.pre_y)
                except:
                    pass
                self.ppre_x = self.pre_x
                self.ppre_y = self.pre_y
                self.pre_x = self.rx
                self.pre_y = self.ry
                self.ppre_vx = self.pre_vx
                self.ppre_vy = self.pre_vy
                self.pre_vx = self.vx
                self.pre_vy = self.vy
                print("轨迹运算：",time.time()-mid_)
                if math.fabs(self.vx) > 2 or math.fabs(self.vy) > 2:
                    pass
                else:
                    self.vx = self.vy = 0
                    return
        except Exception as error:
            pass
    def draw(self):
        try:
            self.frame_locate = self.frame_original.copy()
            center = (int(self.x), int(self.y))
            self.frame_locate = cv.circle(self.frame_original, center, self.radius, (0, 255, 0), 2)
            self.frame_locate = cv.circle(self.frame_locate, center, 1, (255, 0, 0), 2)
            self.frame_track = self.frame_locate.copy()
            cv.line(self.frame_track, (self.x, self.y), (int(self.x + 300 * self.vx), int(self.y + 300 * self.vy)),
                    (255, 0, 0), 5)
        except Exception as error:
            showerror("Error!", str(error) + "\nPlease check!")


# 定义手柄类
class Paddle:
    def __init__(self, frame=None):
        self.frame_original = frame  # 初始图像
        self.frame_segmentation = None  # 颜色分割后的图像
        self.frame_thresh = None  # 二值化后的图像
        self.frame_preprocess = None  # 预处理后的图像
        self.frame_locate = None  # 目标定位标定
        self.radius = 0  # 目标外接球半径
        self.x = 0  # 目标质心的x坐标测量
        self.y = 0  # 目标质心的y坐标测量
        self.angle = 0  # 目标应运动的方向
        self.kernel_open_size = 2  # 开运算核
        self.kernel_close_size = 3  # 闭运算核
        self.lower = np.array([156, 25, 100])  # 绿色阈值的下限
        self.upper = np.array([180, 255, 255])  # 绿色阈值的上限
        self.corner_points = {0: (0, 0), 1: (0, 0),  # 角点字典
                              2: (0, 0), 3: (0, 0)}
        self.mcu_point = (0, 0)  # 单片机坐标
        self.correct = None  # 纠正矩阵
        self.rx=None #纠正后的x坐标
        self.ry=None #纠正后的y坐标
        self.msg=None #串口数据
        
    
    def reflesh(self, frame):  # 刷新帧
        self.frame_original = frame.copy()
    
    def preprocess(self, frame, mode):  # 预处理,利用输入的帧生成frame_thresh,frame_segmentation,frame_preprocess
        try:
            '''颜色阈值'''
            hsv = cv.cvtColor(self.frame_original, cv.COLOR_BGR2HSV)  # 颜色空间转化
            self.frame_thresh = cv.inRange(hsv, self.lower, self.upper)  # 取掩模
            self.frame_segmentation = cv.bitwise_and(self.frame_original, self.frame_original,
                                                     mask=self.frame_thresh)  # 按位运算
            self.frame_preprocess = cv.morphologyEx(self.frame_thresh, cv.MORPH_OPEN,
                                                    np.ones((self.kernel_open_size, self.kernel_open_size),
                                                            np.uint8))  # 开运算
            self.frame_preprocess = cv.morphologyEx(self.frame_preprocess, cv.MORPH_CLOSE,
                                                    np.ones((self.kernel_close_size, self.kernel_close_size),
                                                            np.uint8))  # 闭运算
            '''轮廓检测'''
            image, contours, hierarchy = cv.findContours(self.frame_preprocess, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
            area = 0
            index = 0
            for i in range(len(contours)):  # 筛选最大面积轮廓
                if cv.contourArea(contours[i]) > area:
                    index = i
                    area = cv.contourArea(contours[i])
            (self.x, self.y), self.radius = cv.minEnclosingCircle(contours[index])
            self.radius = int(self.radius)
            self.x = round(self.x)
            self.y = round(self.y)
        except:
            pass
    
    def draw(self):
        try:
            self.frame_locate = self.frame_original.copy()
            center = (int(self.x), int(self.y))
            self.frame_locate = cv.circle(self.frame_locate, center, 5, (0, 0, 255), 7)
        except Exception as error:
            showerror("Error!", str(error) + "\nPlease check!")
    
    def get_msg(self,mode):
        self.msg='a'+str(int(mode)) + (3 - len(str(self.rx))) * '0' + str(self.rx) + (3 - len(str(self.ry))) * '0' + str(self.ry)


class MySerial():#没必要继承Serial类，最好还是创建一个实例，起到隔离方法的作用
    def __init__(self):
        self.can_receive=True;
        self.ser=Serial()
        self.coordinate_or_modification=0  # 0表示目标点的坐标，1表示修正手柄坐标
        self.X_COORDINATE=0  # 整型量，不管是修正手柄坐标还是指示目标坐标，都存在这里面
        self.Y_COORDINATE=0  # 整型量，不管是修正手柄坐标还是指示目标坐标，都存在这里面
        self.can_send=False  # 每次策略函数更新一次数据就把它置真一次

        self.RECEIVE_X_COORDINATE = 0
        self.RECEIVE_Y_COORDINATE = 0
        
        self.msg=None

        # 定义参数字典
        # dict_COM没有设置必要，本来就需要用字符串赋值
        self.dict_Baudrate = {"9600": 9600, "14500": 14500}
        self.dict_Bytesize = {"8": 8, "7": 7, "6": 6, "5": 5}
        self.dict_Stopbits = {"1": 1, "1.5": 1.5, "2": 2}
        self.dict_Parity = {"No": 'N', "Even": 'E', "Odd": "O", "Mark": "M", "Space": 'S'}


    def Serial_init(self):
        self.ser.port = self.Port.get()#Port变量是gui部分的，怎么才能访问到它
        self.ser.baudrate = self.dict_Baudrate[self.Baudrate.get()]
        self.ser.bytesize = self.dict_Bytesize[self.Bytesize.get()]
        self.stopbits = self.dict_Stopbits[self.Stopbits.get()]
        self.parity = self.dict_Parity[self.Parity.get()]

    def ana_simu_timer(self):


        if self.X_COORDINATE < 500:
            self.X_COORDINATE = self.X_COORDINATE + 1
        else:
            self.X_COORDINATE = 100

        if self.Y_COORDINATE < 500:
            self.Y_COORDINATE = self.Y_COORDINATE + 1
        else:
            self.Y_COORDINATE = 100
            self.can_send = True
        #self.mytimer = Timer(1, self.ana_simu_timer)  # 自调mytimer#不能省略！赋值定义就是初始化，执行过一次之后必须初始化！有标记的
        #self.mytimer.start()

    def Start_serial_launcher(self):
        self.th = Thread(target=self.Start_serial, args=())
        self.th.setDaemon(True)
        self.th.start()
        self.mytimer = Timer(1, self.ana_simu_timer)  # 定义定时器timer
        self.mytimer.start()


    def Start_serial(self):
        # 提前创建x_coordinate也没用，之后赋值时又会重新创建
        if self.Switch_mode.get() == "开始串口通信":
            self.Switch_mode.set("停止串口通信")
            print("切换到开始")
            try:
                self.Serial_init()  # 设置串口信息之后inwaiting会清空
                self.ser.open()
            except:
                showwarning("错误1！", "检查串口设置并重置总开关")

            # 开启串口接收线程
            self.th2 = Thread(target=self.Start_receive_serial, args=())
            self.th2.setDaemon(True)
            self.th2.start()

            while 1:  # 不必设置全局变量cansend，因为并行线程如果进入关闭模式，会直接关闭串口，这个线程会跟着发送错误然后退出
                try:
                    # ser.write(bytes(Message, encoding='gbk'))  # message是个字符
                    if self.can_send:
                        self.x_coordinate = self.X_COORDINATE
                        self.y_coordinate = self.Y_COORDINATE
                        self.can_send = False  # 为了避免发送过程中数据更新，那就把允许发送标记的置假放在一开始就行了......

                        self.ser.write(b"a")  # 先发送校验位'

                        self.ser.write(bytes(chr(self.coordinate_or_modification + 48), encoding='ascii'))  # ord('0')=48
                        self.ser.write(bytes(chr(self.x_coordinate // 100 + 48), encoding='ascii'))  # 如果发送过程中被改了怎么办？必须先复制一次两个坐标！
                        self.ser.write(bytes(chr(self.x_coordinate % 100 // 10 + 48), encoding='ascii'))
                        self.ser.write(bytes(chr(self.x_coordinate % 10 + 48), encoding='ascii'))
                        self.ser.write(bytes(chr(self.y_coordinate // 100 + 48), encoding='ascii'))
                        self.ser.write(bytes(chr(self.y_coordinate % 100 // 10 + 48), encoding='ascii'))
                        self.ser.write(bytes(chr(self.y_coordinate % 10 + 48), encoding='ascii'))
                        time.sleep(0.01)  # 暂停0.1秒，等待单片机
                except:
                    if self.ser.isOpen():  # 区分两种情形
                        showwarning("错误2！", "检查串口设置并重置总开关")
                    break
        elif self.Switch_mode.get() == "停止串口通信":
            self.Switch_mode.set("开始串口通信")
            print("切换到停止")
            self.ser.close()

    def Start_receive_serial(self):
        while self.can_receive:
            try:
                if not self.ser.isOpen():
                    #print('ser is close, thus incable of receiving')
                    break

                if self.ser.inWaiting() > 0:
                    self.msg = str(self.ser.read(1))[2]  # 重要知识，ser.write参数必须是bytes，ser.read的输出参数也是bytes
                    '''if ch == b'b':
                        self.RECEIVE_X_COORDINATE = int(self.ser.read(1)) * 100 + int(self.ser.read(1)) * 10 + int(self.ser.read(1))
                        self.RECEIVE_Y_COORDINATE = int(self.ser.read(1)) * 100 + int(self.ser.read(1)) * 10 + int(self.ser.read(1))
                        print(self.RECEIVE_X_COORDINATE)
                        print(self.RECEIVE_Y_COORDINATE)'''

            except:
                pass
    
    def SendData(self,x,y,mode):
        self.coordinate_or_modification=mode#0 modification ,1 coordinate
        self.X_COORDINATE=x
        self.Y_COORDINATE=y
        self.can_send=True
        #print("Send Data:"+str(x)+str(y))

        