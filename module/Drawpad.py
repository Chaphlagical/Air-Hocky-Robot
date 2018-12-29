import cv2 as cv
import numpy as np
from tkinter.messagebox import *
import time
from threading import*

drawing=False
mode=False
points=[]
count=0
#x:40~480 y:100~520
def Pad(ser):
    drawing = False
    mode = False
    points = []
    count = 0
    def draw_circle(event,x,y,flags,param):
        global drawing,mode,count
        if event==cv.EVENT_LBUTTONDOWN:
            drawing=True
        elif event==cv.EVENT_MOUSEMOVE :
            if drawing==True:
                cv.circle(img,(x,y),0,(0,255,0),-1)
                points.append((x+50, y+110))
                count+=1
                if count>=2:
                    cv.line(img, (points[count-1][0]-50,points[count-1][1]-110), (points[count-2][0]-50,points[count-2][1]-110), (0, 255, 0), 1)
        elif event==cv.EVENT_LBUTTONUP:
            drawing=False
    img=np.zeros((430,410,3),np.uint8)
    cv.namedWindow('pad')
    cv.setMouseCallback('pad',draw_circle)




    while(1):
        cv.imshow('pad',img)
        if cv.waitKey(20)&0xFF==13:
            break
    showinfo("提示","点击确定开始画图")
    for p in points:
        ser.msg = None
        ser.SendData(p[0], p[1], 2)
        #while(ser.msg==None):
            #a=1
        #print(ser.msg)
        time.sleep(0.1)

    cv.imwrite("img.jpg", img)
    #points=[]
    print("a")

    cv.destroyAllWindows()


def Recording(ser):
    ser.desk.set_capture()
    out=cv.VideoWriter("output.avi",cv.VideoWriter_fourcc(*'XVID') ,20,(600,1000))
    path=[]
    ser.SendData(0, 0, 1)
    ser.desk.get_frame()
    ser.desk.get_frame()
    while(True):
        if True:
            ser.desk.get_frame()
            ser.paddle.reflesh(ser.desk.frame_transformed)
            ser.paddle.preprocess()
            #if ser.msg=='s':


            path.append((ser.paddle.x,ser.paddle.y))
            for p in path[1:]:
                cv.circle(ser.paddle.frame_original,p,1,(255,0,0),1)
                q=p
            cv.imshow("frame", ser.paddle.frame_original)
            out.write(ser.paddle.frame_original)
            if cv.waitKey(1)&0xff==ord('q'):
                break
      #  except:
       #     print("a")
    out.release()

    print("a")
    cv.destroyAllWindows()


def Thread_cam(self):
    th2 = Thread(target=lambda: KeyBoard_Control(self, self.desk), args=())
    th2.setDaemon(True)
    th2.start()


def Thread_Pad(self):
    th2 = Thread(target=lambda: Pad(self), args=())
    th2.setDaemon(True)
    th2.start()