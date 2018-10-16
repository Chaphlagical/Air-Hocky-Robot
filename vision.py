# -*- coding:utf-8 -*-
import cv2 as cv
import numpy as np
import time
import math
from tkinter import *
import threading
from tkinter.messagebox import *
import tkinter.filedialog
import os
import platform
import tkinter.ttk as ttk


# 定义球桌类

class Desk:
    def __init__(self, id=-1):
        self.id = id  # 摄像头编号
        self.frame = None  # 帧
        self.capture = cv.VideoCapture(id)  # 视频流
        self.corner_points = {0: (0, 0), 1: (0, 0), 2: (0, 0), 3: (0, 0)}  # 角点字典
    
    def transform(self, frame, mode):  # 透视变换,输入帧生成frame_transformed
        a = 0
        for index in self.corner_points.keys():
            if self.corner_points[index] != (0, 0):
                a += 1
        if a != 4:
            return frame
        
        try:
            if mode == True:
                try:
                    rows, cols, ch = frame.shape  # 行，列，深度
                except:
                    rows, cols = frame.shape  # 兼容二值化图像
                pts1 = np.float32(
                    [self.corner_points[0], self.corner_points[1], self.corner_points[2], self.corner_points[3]])
                pts2 = np.float32([[0, 0], [0, 1000], [600, 1000], [600, 0]])
                M = cv.getPerspectiveTransform(pts1, pts2)
                frame_transformed = cv.warpPerspective(frame, M, (600, 1000))
                return frame_transformed
            else:
                pass
        except:
            showerror("错误！", "发生未知错误,请检查!")
    
    def get_frame(self):  # 获取帧
        try:
            ret, self.frame = self.capture.read()
            self.frame = self.transform(self.frame, True)
        except:
            showerror("错误！", "不能正确读取相机!")
    
    def clear_corner_points_dict(self):  # 清空角点字典
        self.corner_points = {0: (0, 0), 1: (0, 0), 2: (0, 0), 3: (0, 0)}
    
    def set_corner_dict(self):  # 设置角点字典
        self.clear_corner_points_dict()
        self.get_frame()
        
        def MouseCallBackfunc(event, x, y, flags, param):  # 设置触发响应函数
            if event == cv.EVENT_LBUTTONDBLCLK:  # 双击左键触发
                cv.circle(param, (x, y), 3, (255, 0, 0), 5)  # 画蓝点
                for index in self.corner_points.keys():  # 筛选第一个非(0,0)的元素进行赋值
                    if self.corner_points[index] == (0, 0):
                        self.corner_points[index] = (x, y)
                        return
        
        def judge_flag():  # 判断角点字典是否填满,作为跳出循环的标志
            a = 0
            for index in self.corner_points.keys():
                if self.corner_points[index] != (0, 0):
                    a += 1
            if a == 4:
                return True
            else:
                return False
        
        showinfo("角点设置提示", "请按照左上-右上-右下-左下的顺序双击左键你要变换区域的四个顶点")
        cv.destroyAllWindows()
        cv.namedWindow('camera setting')
        cv.setMouseCallback('camera setting', MouseCallBackfunc, self.frame)
        while (1):
            cv.imshow('camera setting', self.frame)
            if cv.waitKey(1) & 0xff == ord('q') or judge_flag():
                if judge_flag() != True:
                    showwarning("提示", "你所选择的点将不会被保存!")
                    self.clear_corner_points_dict()
                    cv.destroyAllWindows()
                else:
                    cv.destroyAllWindows()
                    showinfo("提示", "角点设置成功！")
                self.capture.release()
                self.capture = cv.VideoCapture(self.id)
                break
    
    def update_frame(self):  # 更新视频流
        self.capture = cv.VideoCapture(self.id)


# 定义球类
class Ball:
    def __init__(self, frame=None):
        self.frame_original = frame  # 初始图像
        self.frame_original = None  # 初始图像
        self.frame_segmentation = None  # 颜色分割后的图像
        self.frame_thresh = None  # 二值化后的图像
        self.frame_preprocess = None  # 预处理后的图像
        self.frame_locate = None  # 目标定位标定
        self.frame_track = None  # 目标追踪处理后的图像
        self.x = 0  # 目标最小外接矩形左上角横坐标
        self.y = 0  # 目标最小外接矩形左上角纵坐标
        self.w = 0  # 目标最小外接矩形宽度
        self.h = 0  # 目标最小外接矩形长度
        self.center_x = 0  # 目标质心的x坐标
        self.center_y = 0  # 目标质心的y坐标
        self.vx = 0  # 目标运动的x速度
        self.vy = 0  # 目标运动的y速度
        self.uint_x = 0  # 目标运动单位方向的x分量
        self.uint_y = 0  # 目标运动单位方向的y分量
        self.kernel_morphologyEx_size = 10  # 开运算核
        self.kernel_dilate_size = 6  # 膨胀运算核
        self.lower_blue = np.array([115, 50, 50])  # 蓝色阈值的下限
        self.upper_blue = np.array([125, 255, 255])  # 蓝色阈值的上限
        self.corner_points = {0: (0, 0), 1: (0, 0),  # 角点字典
                              2: (0, 0), 3: (0, 0)}
        self.time = 0  # 两帧停留的时间
    
    def reflesh(self, frame):  # 刷新帧
        self.frame_original = frame.copy()
    
    def preprocess(self, frame):  # 预处理,利用输入的帧生成frame_thresh,frame_segmentation,frame_preprocess
        try:
            hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)  # 颜色空间转化
            self.frame_thresh = cv.inRange(hsv, self.lower_blue, self.upper_blue)  # 取掩模
            self.frame_segmentation = cv.bitwise_and(frame, frame,
                                                     mask=self.frame_thresh)  # 按位运算
            imgray = cv.cvtColor(self.frame_segmentation, cv.COLOR_RGB2GRAY)  # 转灰度图
            self.frame_preprocess = cv.dilate(cv.morphologyEx(self.frame_thresh,
                                                              cv.MORPH_OPEN, np.ones(
                    (self.kernel_morphologyEx_size, self.kernel_morphologyEx_size), np.uint8)),
                                              np.ones((self.kernel_dilate_size, self.kernel_dilate_size), np.uint8),
                                              iterations=1)  # 先进行开运算降噪后进行膨胀复原
        except:
            showerror("错误！", "发生未知错误,请检查!")
    
    def locate(self):  # 球定位,生成外接矩形的各个参数
        try:
            image, contours, hierarchy = cv.findContours(self.frame_preprocess, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
            area = 0
            index = 0
            for i in range(len(contours)):  # 筛选最大面积轮廓
                if cv.contourArea(contours[i]) > area:
                    index = i
                    area = cv.contourArea(contours[i])
            self.x, self.y, self.w, self.h = cv.boundingRect(contours[index])
            self.center_x = int(self.x + self.w / 2)
            self.center_y = int(self.y + self.h / 2)
        except:
            pass
    
    def draw_locate_rectangle(self, frame):  # 绘制外接矩形,生成frame_locate
        try:
            self.frame_locate = frame.copy()
            cv.rectangle(self.frame_locate, (self.x, self.y), (self.x + self.w, self.y + self.h),
                         (0, 255, 0), 2)
        except:
            self.frame_locate = frame.copy()
            pass
    
    def tracking_analysis(self, frame, time):  # 运动分析，生成运动学各个参数,输入差帧和时间
        
        self.vx = (self.center_x - frame.center_x) / time
        self.vy = (self.center_y - frame.center_y) / time
        
        if math.fabs(self.vx + self.vy) > 70:
            pass
        else:
            self.vx = self.vy = 0
        try:
            L = (self.vx ** 2 + self.vy ** 2) ** 0.5
            if self.vy > 0:
                self.unit_x = math.ceil(self.vx * 10 / L)
            else:
                self.uint_x = int(self.vx * 10 / L)
            if self.vy > 0:
                self.uint_y = math.ceil(self.vy * 10 / L)
            else:
                self.uint_y = int(self.vy * 10 / L)
        except:
            self.uint_x = self.uint_y = 0
    
    def draw_tracking(self, frame):  # 根据运动学参数生成预测运动轨迹,生成frame_track
        try:
            self.frame_track = frame.copy()
            cv.line(self.frame_track, (self.center_x, self.center_y), (self.center_x+100 * self.uint_x, self.center_y+100 * self.uint_y),
                    (255, 0, 0), 5)
        except:
            self.frame_track = frame.copy()
            pass


def Cam_Select():  # 获取摄像头id列表
    if 'Linux' in platform.platform():  # 判断系统类型
        dev = os.popen('ls /dev').read()
        dev = dev.split('\n')
        devices = []
        for device in dev:
            if 'video' in device:
                devices.append(device[5])
        return devices
    else:
        pass

def Center(tk,w,h):
    sw = tk.winfo_screenwidth()
    sh = tk.winfo_screenheight()
    x = (sw - w) / 2
    y = (sh - h) / 2
    tk.geometry("%dx%d+%d+%d" % (w, h, x, y))
    
def Cam_Setting(desk, ball):
    tk = Tk()
    tk.title("摄像头设置 ——XYZ小组")
    tk.maxsize(250, 400)  # （宽度，高度）
    tk.minsize(250, 400)
    Center(tk,250,400)
    tk.resizable(width=False, height=False)
    canvas = Canvas(tk, width=250, height=400, bg='whitesmoke')
    canvas.pack()
    ball.corner_points = desk.corner_points
    ball.frame_original = desk.frame
    
    def cam_set_gui():  # 摄像头设置窗口
        root = Tk()
        root.title("摄像头设置")
        root.maxsize(200, 100)
        root.minsize(200, 100)
        Center(root,200,100)
        root.resizable(width=False, height=False)
        canvas = Canvas(root, width=800, height=900, bg='whitesmoke')
        canvas.pack()  # 初始化
        
        def select():  # 选择键的响应函数
            desk.id = int(Dev.get())
            desk.update_frame()
            showinfo("提示", "已选择编号为" + Dev.get() + "的摄像头")
            root.destroy()
        
        devices = Cam_Select()
        dev = StringVar()
        Dev = ttk.Combobox(root, width=7, textvariable=dev, state='readonly')
        Dev['value'] = tuple(devices)
        Dev.current(0)
        id_combobox1 = canvas.create_window(130, 20, window=Dev)
        
        label1 = Label(root, text="摄像头编号：", bg="whitesmoke")
        id_label1 = canvas.create_window(50, 20, window=label1)
        
        button1 = Button(root, text='选择', width=10, height=1, command=select)
        id_button1 = canvas.create_window(100, 70, window=button1)
    
    def transform_set_gui():  # 透视变换设置窗口
        root = Tk()
        root.title("摄像头控制台——透视变换设置")
        root.maxsize(300, 500)
        root.minsize(300, 500)
        Center(root,300,500)
        root.resizable(width=False, height=False)
        canvas = Canvas(root, width=800, height=900, bg='whitesmoke')
        canvas.pack()
        
        def show_original():  # 显示原始图像
            showinfo("提示", "退出请按键盘q键,播放过程请勿随意点击菜单界面")
            cv.startWindowThread()
            try:
                while (True):
                    ret, frame = desk.capture.read()
                    cv.imshow('camera original', frame)
                    if cv.waitKey(1) & 0xff == ord('q'):
                        cv.destroyWindow('camera original')
                        desk.capture.release()
                        desk.capture = cv.VideoCapture(desk.id)
                        break
            except:
                cv.destroyWindow('camera original')
                desk.capture.release()
                desk.capture = cv.VideoCapture(desk.id)
                showerror("错误", "出现未知错误,请检查!")
        
        def show_transform():  # 显示变换后的图像
            showinfo("提示", "退出请按键盘q键,播放过程请勿随意点击菜单界面")
            cv.startWindowThread()
            try:
                while (True):
                    desk.get_frame()
                    cv.imshow('camera transformed', desk.frame)
                    if cv.waitKey(1) & 0xff == ord('q'):
                        cv.destroyWindow('camera transformed')
                        desk.capture.release()
                        desk.capture = cv.VideoCapture(desk.id)
                        break
            except:
                cv.destroyWindow('camera transformed')
                desk.capture.release()
                desk.capture = cv.VideoCapture(desk.id)
                showerror("错误", "出现未知错误,请检查!")
        
        button1 = Button(root, text='显示原视频', width=15, height=5, command=show_original)
        id_button1 = canvas.create_window(150, 100, window=button1)
        button2 = Button(root, text='角点标定', width=15, height=5, command=desk.set_corner_dict)
        id_button2 = canvas.create_window(150, 250, window=button2)
        button3 = Button(root, text='显示变换后视频', width=15, height=5, command=show_transform)
        id_button3 = canvas.create_window(150, 400, window=button3)
        root.mainloop()
    
    def ball_set_gui():  # 球追踪设置窗口
        root = Tk()
        root.title("摄像头控制台——球追踪设置")
        root.maxsize(300, 600)
        root.minsize(300, 600)
        Center(root,300,600)
        root.resizable(width=False, height=False)
        canvas = Canvas(root, width=300, height=700, bg='whitesmoke')
        canvas.pack()
        ball_before = Ball()
        
        hmin = StringVar(root, value=str(ball.lower_blue[0]))
        hmax = StringVar(root, value=str(ball.upper_blue[0]))
        smin = StringVar(root, value=str(ball.lower_blue[1]))
        smax = StringVar(root, value=str(ball.upper_blue[1]))
        vmin = StringVar(root, value=str(ball.lower_blue[2]))
        vmax = StringVar(root, value=str(ball.upper_blue[2]))
        kernel1 = StringVar(root, value=str(ball.kernel_morphologyEx_size))
        kernel2 = StringVar(root, value=str(ball.kernel_dilate_size))
        sleep_time = StringVar(root, value=str(ball.time))
        
        Hmin = Entry(root, width=5, bg='white', textvariable=hmin)
        Hmax = Entry(root, width=5, bg='white', textvariable=hmax)
        Smin = Entry(root, width=5, bg='white', textvariable=smin)
        Smax = Entry(root, width=5, bg='white', textvariable=smax)
        Vmin = Entry(root, width=5, bg='white', textvariable=vmin)
        Vmax = Entry(root, width=5, bg='white', textvariable=vmax)
        Kernel1 = Entry(root, width=5, bg='white', textvariable=kernel1)
        Kernel2 = Entry(root, width=5, bg='white', textvariable=kernel2)
        Sleep_Time = Entry(root, width=5, bg='white', textvariable=sleep_time)
        
        id_Entry1 = canvas.create_window(75, 150, window=Hmin)
        id_Entry2 = canvas.create_window(175, 150, window=Smin)
        id_Entry3 = canvas.create_window(275, 150, window=Vmin)
        id_Entry4 = canvas.create_window(75, 190, window=Hmax)
        id_Entry5 = canvas.create_window(175, 190, window=Smax)
        id_Entry6 = canvas.create_window(275, 190, window=Vmax)
        id_Entry7 = canvas.create_window(90, 330, window=Kernel1)
        id_Entry8 = canvas.create_window(210, 330, window=Kernel2)
        id_Entry9 = canvas.create_window(140, 450, window=Sleep_Time)
        
        label0 = Label(root, text="设置阈值范围(默认蓝色)：", bg="whitesmoke")
        label1 = Label(root, text="Hmin", bg="whitesmoke")
        label2 = Label(root, text="Smin", bg="whitesmoke")
        label3 = Label(root, text="Vmin", bg="whitesmoke")
        label4 = Label(root, text="Hmax", bg="whitesmoke")
        label5 = Label(root, text="Smax", bg="whitesmoke")
        label6 = Label(root, text="Vmax", bg="whitesmoke")
        label7 = Label(root, text="形态学处理核设置：", bg="whitesmoke")
        label8 = Label(root, text="开运算:", bg="whitesmoke")
        label9 = Label(root, text="膨胀:", bg="whitesmoke")
        label10 = Label(root, text="设置两帧延时(s):", bg="whitesmoke")
        id_label0 = canvas.create_window(80, 110, window=label0)
        id_label1 = canvas.create_window(30, 150, window=label1)
        id_label2 = canvas.create_window(130, 150, window=label2)
        id_label3 = canvas.create_window(230, 150, window=label3)
        id_label4 = canvas.create_window(30, 190, window=label4)
        id_label5 = canvas.create_window(130, 190, window=label5)
        id_label6 = canvas.create_window(230, 190, window=label6)
        id_label7 = canvas.create_window(65, 300, window=label7)
        id_label8 = canvas.create_window(40, 330, window=label8)
        id_label9 = canvas.create_window(170, 330, window=label9)
        id_label10 = canvas.create_window(55, 450, window=label10)
        
        def show_hsv():  # 显示HSV颜色范围图
            if 'Linux' in platform.platform():
                os.system("eog HSV.png")
            else:
                pass
        
        def show_hsv_thread():
            th = threading.Thread(target=show_hsv)
            th.setDaemon(TRUE)
            th.start()
        
        def show_original():  # 显示原图像
            showinfo("提示", "退出请按键盘q键,播放过程请勿随意点击菜单界面")
            cv.startWindowThread()
            try:
                while (True):
                    desk.get_frame()
                    ball.reflesh(desk.frame)
                    cv.imshow('camera original', ball.frame_original)
                    if cv.waitKey(1) & 0xff == ord('q'):
                        cv.destroyWindow('camera original')
                        desk.capture.release()
                        desk.capture = cv.VideoCapture(desk.id)
                        break
            except:
                cv.destroyWindow('camera original')
                desk.capture.release()
                desk.capture = cv.VideoCapture(desk.id)
                showerror("错误", "出现未知错误,请检查!")
        
        def show_segmentation():  # 显示分割后的图像
            showinfo("提示", "退出请按键盘q键,播放过程请勿随意点击菜单界面")
            cv.startWindowThread()
            ball.lower_blue = np.array([int(hmin.get()), int(smin.get()), int(vmin.get())])
            ball.upper_blue = np.array([int(hmax.get()), int(smax.get()), int(vmax.get())])
            try:
                while (True):
                    desk.get_frame()
                    ball.reflesh(desk.frame)
                    ball.preprocess(ball.frame_original)
                    cv.imshow('camera segmentation', ball.frame_segmentation)
                    if cv.waitKey(1) & 0xff == ord('q'):
                        cv.destroyWindow('camera segmentation')
                        desk.capture.release()
                        desk.capture = cv.VideoCapture(desk.id)
                        break
            except:
                cv.destroyWindow('camera segmentation')
                desk.capture.release()
                desk.capture = cv.VideoCapture(desk.id)
                showerror("错误", "出现未知错误,请检查!")
        
        def show_thresh():  # 显示二值图像
            showinfo("提示", "退出请按键盘q键,播放过程请勿随意点击菜单界面")
            cv.startWindowThread()
            ball.lower_blue = np.array([int(hmin.get()), int(smin.get()), int(vmin.get())])
            ball.upper_blue = np.array([int(hmax.get()), int(smax.get()), int(vmax.get())])
            try:
                while (True):
                    desk.get_frame()
                    ball.reflesh(desk.frame)
                    ball.preprocess(ball.frame_original)
                    cv.imshow('camera thresh', ball.frame_thresh)
                    if cv.waitKey(1) & 0xff == ord('q'):
                        cv.destroyWindow('camera thresh')
                        desk.capture.release()
                        desk.capture = cv.VideoCapture(desk.id)
                        break
            except:
                cv.destroyWindow('camera thresh')
                desk.capture.release()
                desk.capture = cv.VideoCapture(desk.id)
                showerror("错误", "出现未知错误,请检查!")
        
        def show_reduce_noise():  # 显示降噪后的图像
            showinfo("提示", "退出请按键盘q键,播放过程请勿随意点击菜单界面")
            cv.startWindowThread()
            ball.lower_blue = np.array([int(hmin.get()), int(smin.get()), int(vmin.get())])
            ball.upper_blue = np.array([int(hmax.get()), int(smax.get()), int(vmax.get())])
            ball.kernel_morphologyEx_size = int(Kernel1.get())
            ball.kernel_dilate_size = int(Kernel2.get())
            try:
                while (True):
                    desk.get_frame()
                    ball.reflesh(desk.frame)
                    ball.preprocess(ball.frame_original)
                    cv.imshow('camera reduce noise', ball.frame_preprocess)
                    if cv.waitKey(1) & 0xff == ord('q'):
                        cv.destroyWindow('camera reduce noise')
                        desk.capture.release()
                        desk.capture = cv.VideoCapture(desk.id)
                        break
            except:
                cv.destroyWindow('camera reduce noise')
                desk.capture.release()
                desk.capture = cv.VideoCapture(desk.id)
                showerror("错误", "出现未知错误,请检查!")
        
        def show_track():  # 显示添加追踪定位标记后的图像
            ball.lower_blue = np.array([int(hmin.get()), int(smin.get()), int(vmin.get())])
            ball.upper_blue = np.array([int(hmax.get()), int(smax.get()), int(vmax.get())])
            ball.kernel_morphologyEx_size = int(Kernel1.get())
            ball.kernel_dilate_size = int(Kernel2.get())
            ball.time = float(sleep_time.get())
            try:
                while (True):
                    begin = time.time()
                    desk.get_frame()
                    ball_before.reflesh(desk.frame)
                    time.sleep(ball.time)
                    desk.get_frame()
                    ball.reflesh(desk.frame)
                    times = time.time() - begin
                    ball.preprocess(ball.frame_original)
                    ball_before.preprocess(ball_before.frame_original)
                    ball.locate()
                    ball_before.locate()
                    ball.draw_locate_rectangle(ball.frame_original)
                    ball.tracking_analysis(ball_before, times)
                    ball.draw_tracking(ball.frame_locate)
                    cv.imshow('camera track', ball.frame_track)
                    if cv.waitKey(1) & 0xff == ord('q'):
                        cv.destroyWindow('camera track')
                        desk.capture.release()
                        desk.capture = cv.VideoCapture(desk.id)
                        break
            except:
                cv.destroyWindow('camera track')
                desk.capture.release()
                desk.capture = cv.VideoCapture(desk.id)
                showerror("错误", "出现未知错误,请检查!")
        
        def recover_default():  # 把各参数恢复默认
            ball.kernel_morphologyEx_size = 10
            ball.kernel_dilate_size = 6
            ball.lower_blue = np.array([115, 50, 50])
            ball.upper_blue = np.array([125, 255, 255])
            ball.time = 0
            hmin.set('115')
            smin.set('50')
            vmin.set('50')
            hmax.set('125')
            smax.set('255')
            vmax.set('255')
            kernel1.set('10')
            kernel2.set('6')
            sleep_time.set('0')
            root.update()
            showinfo("提示", "重新设为默认！")
        
        def set_change():  # 将所有参数导入ball对象
            ball.lower_blue = np.array([int(hmin.get()), int(smin.get()), int(vmin.get())])
            ball.upper_blue = np.array([int(hmax.get()), int(smax.get()), int(vmax.get())])
            ball.kernel_morphologyEx_size = int(Kernel1.get())
            ball.kernel_dilate_size = int(Kernel2.get())
            ball.time = float(sleep_time.get())
            showinfo("提示", "新参数设置成功！")
        
        def save_setting():  # 将设置保存为文件
            path = tkinter.filedialog.asksaveasfilename()
            if ('(球追踪参数存档)' in path) == False:
                path += '(球追踪参数存档)'
            
            f = open(path, 'w')
            f.write(hmin.get() + '|' + smin.get() + '|' + vmin.get() + '|' + hmax.get() + '|' +
                    smax.get() + '|' + vmax.get() + '|' + kernel1.get() + '|' +
                    kernel2.get() + '|' + sleep_time.get())
            f.close()
            showinfo("提示", "参数存档成功！")
        
        def load_setting():  # 从文件导入设置
            path = tkinter.filedialog.askopenfilename()
            f = open(path, 'r+')
            s = f.readline()
            s = s.split('|')
            ball.lower_blue = np.array([int(s[0]), int(s[1]), int(s[2])])
            ball.upper_blue = np.array([int(s[3]), int(s[4]), int(s[5])])
            ball.kernel_morphologyEx_size = int(s[6])
            ball.kernel_dilate_size = int(s[7])
            ball.time = float(s[8])
            f.close()
            hmin.set(str(ball.lower_blue[0]))
            smin.set(str(ball.lower_blue[1]))
            vmin.set(str(ball.lower_blue[2]))
            hmax.set(str(ball.upper_blue[0]))
            smax.set(str(ball.upper_blue[1]))
            vmax.set(str(ball.upper_blue[2]))
            kernel1.set(str(ball.kernel_morphologyEx_size))
            kernel2.set(str(ball.kernel_dilate_size))
            sleep_time.set(ball.time)
            showinfo("提示", "参数读档成功！")
            root.update()
        
        button1 = Button(root, text='显示原视频', width=10, height=3, command=show_original)
        button2 = Button(root, text='显示阈值效果', width=10, height=3, command=show_segmentation)
        button3 = Button(root, text='显示降噪效果', width=10, height=3, command=show_reduce_noise)
        button4 = Button(root, text='显示二值图像', width=10, height=3, command=show_thresh)
        button5 = Button(root, text='恢复默认', width=5, height=1, command=recover_default)
        button6 = Button(root, text='设置启动', width=5, height=1, command=set_change)
        button7 = Button(root, text='保存设置', width=5, height=1, command=save_setting)
        button8 = Button(root, text='读取设置', width=5, height=1, command=load_setting)
        button9 = Button(root, text='显示定位追踪效果', width=12, height=3, command=show_track)
        button10 = Button(root, text='点击查看HSV颜色范围', width=14, height=1, command=show_hsv_thread)
        
        id_button1 = canvas.create_window(150, 50, window=button1)
        id_button2 = canvas.create_window(145, 250, window=button2)
        id_button3 = canvas.create_window(215, 390, window=button3)
        id_button4 = canvas.create_window(85, 390, window=button4)
        id_button5 = canvas.create_window(40, 560, window=button5)
        id_button6 = canvas.create_window(110, 560, window=button6)
        id_button7 = canvas.create_window(180, 560, window=button7)
        id_button8 = canvas.create_window(250, 560, window=button8)
        id_button9 = canvas.create_window(230, 475, window=button9)
        id_button10 = canvas.create_window(225, 110, window=button10)
    
    def paddle_set_gui():
        pass
    
    button1 = Button(tk, text='摄像头设置', width=10, height=3, command=cam_set_gui)
    id_button1 = canvas.create_window(130, 60, window=button1)
    button2 = Button(tk, text='透视变换设置', width=10, height=3, command=transform_set_gui)
    id_button2 = canvas.create_window(130, 150, window=button2)
    button3 = Button(tk, text='球追踪设置', width=10, height=3, command=ball_set_gui)
    id_button3 = canvas.create_window(130, 240, window=button3)
    button4 = Button(tk, text='手柄追踪设置', width=10, height=3, command=paddle_set_gui)
    id_button4 = canvas.create_window(130, 330, window=button4)
    tk.mainloop()


def Cam_Showing(desk, ball):
    tk = Tk()
    tk.title("摄像头选项 ——XYZ小组")
    tk.maxsize(250, 200)  # （宽度，高度）
    tk.minsize(250, 200)
    Center(tk,250,200)
    tk.resizable(width=False, height=False)
    canvas = Canvas(tk, width=250, height=400, bg='whitesmoke')
    canvas.pack()
    ball_before = Ball()
    
    def show_original():
        cv.startWindowThread()
        try:
            while (True):
                ret, frame = desk.capture.read()
                begin = time.time()
                desk.get_frame()
                ball_before.reflesh(desk.frame)
                time.sleep(ball.time)
                desk.get_frame()
                ball.reflesh(desk.frame)
                times = time.time() - begin
                ball.preprocess(ball.frame_original)
                ball_before.preprocess(ball_before.frame_original)
                ball.locate()
                ball_before.locate()
                ball.tracking_analysis(ball_before, times)
                cv.imshow('camera', frame)
                if cv.waitKey(1) & 0xff == ord('q'):
                    cv.destroyWindow('camera')
                    desk.capture.release()
                    desk.capture = cv.VideoCapture(desk.id)
                    break
        except:
            cv.destroyWindow('camera')
            desk.capture.release()
            desk.capture = cv.VideoCapture(desk.id)
            showerror("错误", "出现未知错误,请检查!")
    
    def show_process():
        try:
            while (True):
                begin = time.time()
                desk.get_frame()
                ball_before.reflesh(desk.frame)
                time.sleep(ball.time)
                desk.get_frame()
                ball.reflesh(desk.frame)
                times = time.time() - begin
                ball.preprocess(ball.frame_original)
                ball_before.preprocess(ball_before.frame_original)
                ball.locate()
                ball_before.locate()
                ball.draw_locate_rectangle(ball.frame_original)
                ball.tracking_analysis(ball_before, times)
                ball.draw_tracking(ball.frame_locate)
                cv.imshow('camera', ball.frame_track)
                if cv.waitKey(1) & 0xff == ord('q'):
                    cv.destroyWindow('camera')
                    desk.capture.release()
                    desk.capture = cv.VideoCapture(desk.id)
                    break
        except:
            cv.destroyWindow('camera')
            desk.capture.release()
            desk.capture = cv.VideoCapture(desk.id)
            showerror("错误", "出现未知错误,请检查!")
    
    button1 = Button(tk, text='显示原始图像', width=10, height=3, command=show_original)
    id_button1 = canvas.create_window(120, 50, window=button1)
    button2 = Button(tk, text='显示处理图像', width=10, height=3, command=show_process)
    id_button2 = canvas.create_window(120, 140, window=button2)
    tk.mainloop()

'''desk = Desk("./Matrial/Video/1.webm")

# desk = Desk()
ball = Ball()
Cam_Showing(desk, ball)
'''























