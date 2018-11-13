# -*- coding:utf-8 -*-
import cv2 as cv
import numpy as np
import math
from tkinter.messagebox import *
from serial import *
from serial.tools.list_ports import *

# 桌子类
class Desk:
    def __init__(self, id=-1):
        self.id = id  # 摄像头编号
        self.frame = None  # 帧
        self.capture = None  # 视频流
        self.corner_points = {0: (0, 0), 1: (0, 0), 2: (0, 0), 3: (0, 0)}  # 角点字典
        self.frame_transformed = None  # 变换后的帧
    
    def set_capture(self):
        self.capture = cv.VideoCapture(self.id)
    
    def release_capture(self):
        self.capture.release()
    
    def judge_flag(self):  # 判断角点字典是否填满,作为跳出循环的标志
        count = 0
        for index in self.corner_points.keys():
            if self.corner_points[index] != (0, 0):
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
            '''轨迹计算mode为True开启'''
            if mode == True:
                self.vx = (self.x - frame.x) / self.sec
                self.vy = (self.y - frame.y) / self.sec
                if math.fabs(self.x - frame.x) > 10 or math.fabs(self.y - frame.y) > 4:
                    pass
                else:
                    self.vx = self.vy = 0
                    self.uint_x = self.uint_y = 0
                    return
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
        except Exception as error:
            showerror("Error", str(error) + "Please check!")
    
    def draw(self):
        try:
            self.frame_locate = self.frame_original.copy()
            center = (int(self.x), int(self.y))
            self.frame_locate = cv.circle(self.frame_original, center, self.radius, (0, 255, 0), 2)
            self.frame_locate = cv.circle(self.frame_locate, center, 1, (255, 0, 0), 2)
            self.frame_track = self.frame_locate.copy()
            cv.line(self.frame_track, (self.x, self.y), (self.x + 10 * self.uint_x, self.y + 10 * self.uint_y),
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
        self.kernel_open_size = 4  # 开运算核
        self.kernel_close_size = 3  # 闭运算核
        self.lower = np.array([70, 50, 50])  # 绿色阈值的下限
        self.upper = np.array([90, 255, 255])  # 绿色阈值的上限
        self.corner_points = {0: (0, 0), 1: (0, 0),  # 角点字典
                              2: (0, 0), 3: (0, 0)}
        self.mcu_point = (0, 0)  # 单片机坐标
        self.correct = None  # 纠正矩阵
        self.cam_array = np.zeros((3, 3))  # 求纠正矩阵需要的摄像头坐标数据
        self.mcu_array = np.zeros((3, 2))  # 求纠正矩阵需要的单片机坐标数据
    
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


class Coordinate:
    def __init__(self):
        self.cam = np.zeros((1, 3))
        self.mcu = np.zeros((1, 2))
        self.correct = np.zeros((3, 2))
        self.cam_array = np.zeros((3, 3))
        self.mcu_array = np.zeros((3, 2))
        self.flag_cam = 0
        self.flag_mcu = 0
    
    def get_cam_array(self, x, y):
        if self.flag_cam > 2:
            return
        else:
            self.cam_array[self.flag_cam] = np.array([x, y, 1])
            self.flag_cam += 1
    
    def get_mcu_array(self, x, y):
        if self.flag_mcu > 2:
            return
        else:
            self.mcu_array[self.flag_mcu] = np.array([x, y])
            self.flag_mcu += 1
    
    def Correct(self):
        try:
            if self.flag_mcu > 2 and self.flag_cam > 2 and self.correct == np.zeros((3, 2)):
                self.correct = np.matmul(np.linalg.inv(self.cam_array), self.mcu_array)
        except:
            self.flag_cam=self.flag_mcu=0
            
    def num2cam(self, x, y):
        self.cam = np.array([x, y, 1])
    
    def get_mcu(self):
        self.mcu = np.matmul(self.cam, self.correct)

    def point2msg(self, x, y, mode):  # 点坐标转消息
        return str(int(mode)) + (3 - len(str(x))) * '0' + str(x) + (3 - len(str(y))) * '0' + str(y)
        
    def send_msg(self,ser,mode):
        msg=self.point2msg(self.mcu[0],self.mcu[1], mode)
        ser.write(bytes(msg, encoding='ascii'))
        
    def receive_msg(self,ser):
        print(ser.read(8))
        
    def print_coordinate(self):
        print('单片机坐标',self.mcu,'摄像头坐标',self.cam)

