import cv2 as cv
import numpy as np
from tkinter.messagebox import *
import time
import threading
#cv.waitKey(20)&0xFF==13:
def KeyBoard_Control(ser,desk):
    '''x0=260
    y0=100
    d=5
    ser.SendData(x0, y0, 1)
    desk.set_capture()
    desk.get_frame()
    while(True):
        desk.get_frame()
        key=cv.waitKey(1)&0xFF
        if key==119:
            y0+=d
            ser.SendData(x0, y0, 1)
            cv.imshow("camera", desk.frame_transformed)
        elif key==97:
            x0-=d
            ser.SendData(x0, y0, 1)
            cv.imshow("camera", desk.frame_transformed)
        elif key==115:
            y0-=d
            ser.SendData(x0, y0, 1)
            cv.imshow("camera", desk.frame_transformed)
        elif key==100:
            x0+=d
            ser.SendData(x0, y0, 1)
            cv.imshow("camera", desk.frame_transformed)
        elif key==113:
            d+=5
            cv.imshow("camera", desk.frame_transformed)
        elif key==101:
            if d>0:
                d-=5
            cv.imshow("camera", desk.frame_transformed)
        elif key==27:
            cv.imshow("camera", desk.frame_transformed)
            break
        else:
            cv.imshow("camera", desk.frame_transformed)
    cv.destroyAllWindows()'''
    path=[]
    out = cv.VideoWriter("output.avi", cv.VideoWriter_fourcc(*'XVID'), 20, (600, 1000))
    ser.desk.set_capture()
    ser.desk.get_frame()
    ser.desk.get_frame()
    while(True):
        ser.desk.get_frame()
        cv.imshow("frame",desk.frame_transformed)
        if cv.waitKey(1) & 0xff == ord('s'):
            break
    while (True):
        ser.desk.get_frame()
        ser.paddle.reflesh(ser.desk.frame_transformed)
        ser.paddle.preprocess()
        # if ser.msg=='s':
        path.append((ser.paddle.x, ser.paddle.y))
        for p in path[1:]:
            cv.circle(ser.paddle.frame_original, p, 1, (255, 0, 0), 2)
        cv.imshow("frame",ser.paddle.frame_original)
        out.write(ser.paddle.frame_original)
        key=cv.waitKey(1) & 0xff
        if  key== ord('q'):
            break
        elif key==ord('r'):
            path=[]
        elif key==ord('a'):
            ser.desk.get_frame()
            cv.imshow("frame", ser.paddle.frame_original)
            if key == ord('q'):
                break
    out.release()
    cv.destroyAllWindows()
    print("save")