from module.Hockey import *
import numpy as np

#设摄像头坐标为cam,单片机坐标为mcu
#转摄像头矩阵
def num2array_cam(p1,p2,p3):
    return np.array(([p1[0],p1[1],1],
                     [p2[0],p2[1],1],
                     [p3[0],p3[1],1]))
   
def num2array_mcu(p1,p2,p3):
    return np.array(([p1[0], p1[1]],
                     [p2[0], p2[1]],
                     [p3[0], p3[1]]))

def Correct(cam,mcu):#坐标纠正
    return np.matmul(np.linalg.inv(cam),mcu)

def Get_mcu(correct,cam):#获得单片机的坐标
    real=np.matmul(cam,correct)
    return real[0],real[1]

def get_angle(ball,x0,y0):
    return (ball.y-y0)/(ball.x-x0)

def point2msg(x,y,mode):#点坐标转消息
    return str(int(mode))+(3-len(str(x)))*'0'+str(x)+(3-len(str(y)))*'0'+str(y)

