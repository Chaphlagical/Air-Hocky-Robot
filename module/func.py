import os
import platform
from tkinter import*
from tkinter.messagebox import *
import cv2 as cv
from module.Strategy import *
import threading
from module.Hockey import*
import time
import design

# 获取摄像头id列表
def Cam_Select():
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
    
# 取屏幕中心
def Center(tk,w,h):
    sw = tk.winfo_screenwidth()
    sh = tk.winfo_screenheight()
    x = (sw - w) / 2
    y = (sh - h) / 2
    tk.geometry("%dx%d+%d+%d" % (w, h, x, y))

def Set_Win(tk,title,width,height):
    tk.title(title)
    tk.maxsize(width,height)
    tk.minsize(width,height)
    Center(tk, width,height)
    tk.resizable(width=False, height=False)
    canvas = Canvas(tk, width=width, height=height, bg='whitesmoke')
    canvas.pack()
    return canvas

# 显示原图像
def show_original(desk,hockey):
    showinfo("提示", "退出请按键盘q键,播放过程请勿随意点击菜单界面")
    desk.set_capture()
    desk.capture.set(5,40)
    cv.startWindowThread()
    try:
        while (True):
            desk.get_frame()
            if hockey==desk:
                cv.imshow('camera original', hockey.frame)
            else:
                hockey.reflesh(desk.frame)
                cv.imshow('camera original', hockey.frame_original)
            if cv.waitKey(1) & 0xff == ord('q'):
                cv.destroyWindow('camera original')
                desk.capture.release()
                break
    except Exception as error:
        cv.destroyWindow('camera original')
        desk.capture.release()
        showerror("Error", str(error)+"\nPlease check!")

# 显示透视变换后的图像
def show_transform(desk,hockey):
    showinfo("提示", "退出请按键盘q键,播放过程请勿随意点击菜单界面")
    desk.set_capture()
    cv.startWindowThread()
    try:
        while (True):
            desk.get_frame()
            if hockey==desk:
                cv.imshow('camera transformed', desk.frame_transformed)
            else:
                hockey.reflesh(desk.frame_transformed)
                cv.imshow('camera transformed', hockey.frame_original)
            if cv.waitKey(1) & 0xff == ord('q'):
                cv.destroyWindow('camera transformed')
                desk.capture.release()
                break
    except Exception as error:
        cv.destroyWindow('camera transformed')
        desk.capture.release()
        showerror("Error", str(error) + "\nPlease check!")
        
def Set_Ball_Track_Param(root,canvas,ball):
    hmin = StringVar(root, value=str(ball.lower[0]))
    hmax = StringVar(root, value=str(ball.upper[0]))
    smin = StringVar(root, value=str(ball.lower[1]))
    smax = StringVar(root, value=str(ball.upper[1]))
    vmin = StringVar(root, value=str(ball.lower[2]))
    vmax = StringVar(root, value=str(ball.upper[2]))
    kernel1 = StringVar(root, value=str(ball.kernel_open_size))
    kernel2 = StringVar(root, value=str(ball.kernel_close_size))
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
    label9 = Label(root, text="闭运算:", bg="whitesmoke")
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
    id_label9 = canvas.create_window(160, 330, window=label9)
    id_label10 = canvas.create_window(55, 450, window=label10)
    return hmin,smin,vmin,hmax,smax,vmax,kernel1,kernel2,sleep_time
    
# 显示HSV颜色范围图
def show_hsv():
    if 'Linux' in platform.platform():
        os.system("eog HSV.png")
    else:
        pass
    
def show_hsv_thread():
    th = threading.Thread(target=show_hsv)
    th.setDaemon(TRUE)
    th.start()
    
def show_segmentation(desk,hockey,hmin, smin, vmin, hmax, smax, vmax):  # 显示分割后的图像
    showinfo("提示", "退出请按键盘q键,播放过程请勿随意点击菜单界面")
    cv.startWindowThread()
    hockey.lower = np.array([int(hmin.get()), int(smin.get()), int(vmin.get())])
    hockey.upper = np.array([int(hmax.get()), int(smax.get()), int(vmax.get())])
    desk.set_capture()
    try:
        while (True):
            desk.get_frame()
            hockey.reflesh(desk.frame_transformed)
            hockey.preprocess(None,False)
            cv.imshow('camera segmentation', hockey.frame_segmentation)
            if cv.waitKey(1) & 0xff == ord('q'):
                cv.destroyWindow('camera segmentation')
                desk.capture.release()
                break
    except Exception as error:
        cv.destroyWindow('camera segmentation')
        desk.capture.release()
        showerror("Error", str(error) + "\nPlease check!")
        
        
def show_thresh(desk,hockey,hmin, smin, vmin, hmax, smax, vmax):  # 显示二值图像
    showinfo("提示", "退出请按键盘q键,播放过程请勿随意点击菜单界面")
    cv.startWindowThread()
    hockey.lower = np.array([int(hmin.get()), int(smin.get()), int(vmin.get())])
    hockey.upper = np.array([int(hmax.get()), int(smax.get()), int(vmax.get())])
    desk.set_capture()
    try:
        while (True):
            desk.get_frame()
            hockey.reflesh(desk.frame_transformed)
            hockey.preprocess(None, False)
            cv.imshow('camera thresh', hockey.frame_thresh)
            if cv.waitKey(1) & 0xff == ord('q'):
                cv.destroyWindow('camera thresh')
                desk.capture.release()
                break
    except Exception as error:
        cv.destroyWindow('camera thresh')
        desk.capture.release()
        showerror("Error", str(error) + "\nPlease check!")
        
# 显示降噪后的图像
def show_reduce_noise(desk,hockey,hmin, smin, vmin, hmax, smax, vmax,kernel1,kernel2):
    showinfo("提示", "退出请按键盘q键,播放过程请勿随意点击菜单界面")
    cv.startWindowThread()
    desk.set_capture()
    hockey.lower = np.array([int(hmin.get()), int(smin.get()), int(vmin.get())])
    hockey.upper = np.array([int(hmax.get()), int(smax.get()), int(vmax.get())])
    hockey.kernel_open_size = int(kernel1.get())
    hockey.kernel_close_size = int(kernel2.get())
    try:
        while (True):
            desk.get_frame()
            hockey.reflesh(desk.frame_transformed)
            hockey.preprocess(None, False)
            cv.imshow('camera reduce noise', hockey.frame_preprocess)
            if cv.waitKey(1) & 0xff == ord('q'):
                cv.destroyWindow('camera reduce noise')
                desk.capture.release()
                break
    except Exception as error:
        cv.destroyWindow('camera reduce noise')
        desk.release_capture()
        showerror("Error", str(error) + "\nPlease check!")


def show_track(desk,ball,hmin, smin, vmin, hmax, smax, vmax,kernel1,kernel2,sleep_time):  # 显示添加追踪定位标记后的图像
    showinfo("提示", "退出请按键盘q键,播放过程请勿随意点击菜单界面")
    cv.startWindowThread()
    desk.set_capture()
    ball.lower = np.array([int(hmin.get()), int(smin.get()), int(vmin.get())])
    ball.upper = np.array([int(hmax.get()), int(smax.get()), int(vmax.get())])
    ball.kernel_open_size = int(kernel1.get())
    ball.kernel_close_size = int(kernel2.get())
    ball.time = float(sleep_time.get())
    start=end=0

    try:
        while (True):
            start = time.time()
            ball.pre_x = ball.rx
            ball.pre_y = ball.ry
            time.sleep(ball.time)
            desk.get_frame()
            ball.reflesh(desk.frame_transformed)
            ball.sec = start-end
            ball.preprocess(True)
            ball.draw()
            end = time.time()
            cv.imshow('camera track', ball.frame_track)
            if cv.waitKey(1) & 0xff == ord('q'):
                cv.destroyWindow('camera track')
                desk.capture.release()
                break
    except Exception as error:
        cv.destroyWindow('camera track')
        desk.capture.release()
        showerror("Error", str(error) + "\nPlease check!")
        
def show_locate(desk,paddle,hmin, smin, vmin, hmax, smax, vmax,kernel1,kernel2):  # 显示添加追踪定位标记后的图像
    showinfo("提示", "退出请按键盘q键,播放过程请勿随意点击菜单界面")
    cv.startWindowThread()
    desk.set_capture()
    paddle.lower = np.array([int(hmin.get()), int(smin.get()), int(vmin.get())])
    paddle.upper = np.array([int(hmax.get()), int(smax.get()), int(vmax.get())])
    paddle.kernel_open_size = int(kernel1.get())
    paddle.kernel_close_size = int(kernel2.get())
    desk.get_frame()
    paddle.reflesh(desk.frame_transformed)
    paddle.preprocess(None, True)
    paddle.draw()
    cv.circle(paddle.frame_locate, (paddle.x, paddle.y), 5, (0, 0, 255), 7)
    img=paddle.frame_locate
    try:
        while (True):
            desk.get_frame()
            paddle.reflesh(desk.frame_transformed)
            paddle.preprocess(None,True)
            paddle.draw()

            cv.circle(img,(paddle.x,paddle.y),5, (0, 0, 255), 7)
            cv.imshow('camera locate', paddle.frame_locate)
            if cv.waitKey(1) & 0xff == ord('q'):
                cv.destroyWindow('camera locate')
                desk.capture.release()
                break
    except Exception as error:
        cv.destroyWindow('camera locate')
        desk.capture.release()
        showerror("Error", str(error) + "\nPlease check!")

# 设置手柄参数
def Set_Paddle_Track_Param(root, canvas, paddle):
    hmin = StringVar(root, value=str(paddle.lower[0]))
    hmax = StringVar(root, value=str(paddle.upper[0]))
    smin = StringVar(root, value=str(paddle.lower[1]))
    smax = StringVar(root, value=str(paddle.upper[1]))
    vmin = StringVar(root, value=str(paddle.lower[2]))
    vmax = StringVar(root, value=str(paddle.upper[2]))
    kernel1 = StringVar(root, value=str(paddle.kernel_open_size))
    kernel2 = StringVar(root, value=str(paddle.kernel_close_size))
    
    Hmin = Entry(root, width=5, bg='white', textvariable=hmin)
    Hmax = Entry(root, width=5, bg='white', textvariable=hmax)
    Smin = Entry(root, width=5, bg='white', textvariable=smin)
    Smax = Entry(root, width=5, bg='white', textvariable=smax)
    Vmin = Entry(root, width=5, bg='white', textvariable=vmin)
    Vmax = Entry(root, width=5, bg='white', textvariable=vmax)
    Kernel1 = Entry(root, width=5, bg='white', textvariable=kernel1)
    Kernel2 = Entry(root, width=5, bg='white', textvariable=kernel2)
    
    id_Entry1 = canvas.create_window(75, 150, window=Hmin)
    id_Entry2 = canvas.create_window(175, 150, window=Smin)
    id_Entry3 = canvas.create_window(275, 150, window=Vmin)
    id_Entry4 = canvas.create_window(75, 190, window=Hmax)
    id_Entry5 = canvas.create_window(175, 190, window=Smax)
    id_Entry6 = canvas.create_window(275, 190, window=Vmax)
    id_Entry7 = canvas.create_window(90, 330, window=Kernel1)
    id_Entry8 = canvas.create_window(210, 330, window=Kernel2)
    
    label0 = Label(root, text="设置阈值范围(默认绿色)：", bg="whitesmoke")
    label1 = Label(root, text="Hmin", bg="whitesmoke")
    label2 = Label(root, text="Smin", bg="whitesmoke")
    label3 = Label(root, text="Vmin", bg="whitesmoke")
    label4 = Label(root, text="Hmax", bg="whitesmoke")
    label5 = Label(root, text="Smax", bg="whitesmoke")
    label6 = Label(root, text="Vmax", bg="whitesmoke")
    label7 = Label(root, text="形态学处理核设置：", bg="whitesmoke")
    label8 = Label(root, text="开运算:", bg="whitesmoke")
    label9 = Label(root, text="膨胀:", bg="whitesmoke")
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
    return hmin, smin, vmin, hmax, smax, vmax, kernel1, kernel2


'''ball=Ball()
desk=Desk()
paddle=Paddle()
ser=main_gui(ball,desk,paddle)'''
def Coordinate_Correction(desk,paddle,winname,ser):
    #cv.startWindowThread()
    cam_t1=mcu_t1=cam_t2=mcu_t2=cam_t3=mcu_t3=(0,0)
    cam_array=mcu_array=None
    flag=0
    ser.SendData(260,100,0)
    while(True):
        try:
            print(flag)
            desk.get_frame()
            paddle.reflesh(desk.frame_transformed)
            paddle.preprocess(None, True)
            time.sleep(0.6)
            if ser.msg=='1':
                #print(paddle.x, paddle.y)
                #x:40~480 y:100~520
                mcu_t1=(260,100)
                if flag<=3:
                    flag+=1
                elif flag>=4 and flag<=7:
                    cam_t1 = (cam_t1[0]+paddle.x, cam_t1[1]+paddle.y)
                    flag+=1
                else:
                    cam_t1=(cam_t1[0]/4,cam_t1[1]/4)
                    print(cam_t1)
                    flag=0
                    ser.msg=None
                    ser.ser.flush()
                    ser.SendData(400,450,0)
                    print("获得第一组数据")
            elif ser.msg=='2':
                #print(paddle.x, paddle.y)
                mcu_t2=(400,450)
                if flag<=3:
                    flag+=1
                elif flag>=4 and flag<=7:
                    cam_t2 = (cam_t2[0]+paddle.x, cam_t2[1]+paddle.y)
                    flag+=1
                else:
                    cam_t2=(cam_t2[0]/4,cam_t2[1]/4)
                    print(cam_t2)
                    flag=0
                    ser.msg=None
                    ser.ser.flush()
                    ser.SendData(100,450,0)
                    print('获得第二组数据')
            elif ser.msg=='3':
                #print(paddle.x, paddle.y)
                mcu_t3=(100,450)
                if flag<=3:
                   flag+=1
                elif flag>=4 and flag<=7:
                   cam_t3 = (cam_t3[0]+paddle.x, cam_t3[1]+paddle.y)
                   flag+=1
                else:
                   cam_t3=(cam_t3[0]/4,cam_t3[1]/4)
                   print(cam_t3)
                   flag=0
                   ser.msg='4'
                   ser.SendData(260,100,1)
            elif ser.msg=='4':
                cam_array=num2array_cam(cam_t1,cam_t2,cam_t3)
                mcu_array=num2array_mcu(mcu_t1,mcu_t2,mcu_t3)
                paddle.correct=Correct(cam_array,mcu_array)
                print(paddle.correct)
                ser.msg=None
                break
            if cv.waitKey(1) & 0xff == ord('q'):
                break
        except Exception as Err:
            ser.SendData(260,100,0)
            print(Err)
            pass

def Image_Processing(desk,ball,paddle,ser):
    th = threading.Thread(target=lambda :Image_Processing_target(desk,ball,paddle,ser))
    th.setDaemon(True)
    th.start()
def Image_Processing_target(desk,ball,paddle,ser):
    desk.set_capture()
    start=end=0
    #ball_before=Ball()
    move_x=move_y=-1
    #flag=0
    #cv.startWindowThread()
    #cv.namedWindow('main')
    Coordinate_Correction(desk,paddle,'main',ser)
    desk.get_frame()
    desk.get_frame()
    desk.get_frame()
    desk.get_frame()
    desk.get_frame()
    paddle.reflesh(desk.frame_transformed)
    paddle.preprocess(None,True)
    paddle.rx, paddle.ry = Get_mcu(paddle.correct, np.array(([paddle.x, paddle.y, 1])))
    paddle.rx = int(paddle.rx);paddle.ry = int(paddle.ry)
    print(paddle.rx,paddle.ry)
    bias=math.fabs(paddle.rx-260)+math.fabs(paddle.ry-100)
    print("误差：",bias)
    if bias>6:
        print("误差过大，重新采样")
    else:
        print("初始化成功！")
    while(bias>6):
        Coordinate_Correction(desk, paddle, 'main', ser)
        desk.get_frame()
        desk.get_frame()
        desk.get_frame()
        desk.get_frame()
        desk.get_frame()
        paddle.reflesh(desk.frame_transformed)
        paddle.preprocess(None, True)
        paddle.rx, paddle.ry = Get_mcu(paddle.correct, np.array(([paddle.x, paddle.y, 1])))
        paddle.rx = int(paddle.rx);paddle.ry = int(paddle.ry)
        print(paddle.rx, paddle.ry)
        bias = math.fabs(paddle.rx - 260) + math.fabs(paddle.ry - 100)
        print("误差：", bias)
        if bias > 6:
            print("误差过大，重新采样")
        else:
            print("初始化成功！")
    try:
        ball.correct=paddle.correct
        while(True):
            start = time.time()
            time.sleep(ball.time)
            
            desk.get_frame()
            #paddle.reflesh(desk.frame_transformed)
            #paddle.preprocess(None,True)
            ball.sec = start-end
            #ball_before.reflesh(desk.frame_transformed)
            
            #desk.get_frame()
            ball.reflesh(desk.frame_transformed)
            
            #ball_before.preprocess(None, False)
            
            ball.preprocess(True)
            #print('ball', ball.x, ball.y)
            #print('paddle', paddle.x, paddle.y)
            #paddle.rx,paddle.ry=Get_mcu(paddle.correct,np.array(([paddle.x,paddle.y,1])))
            #paddle.rx = int(paddle.rx);paddle.ry = int(paddle.ry)
            #print('ball=',ball.rx,ball.ry)
            #print('paddle=',paddle.rx,paddle.ry)
            move_x,move_y=design.pusher_defense(ball)
            #move_x=ball.rx
            #move_y=100
            #move_x,move_y=Pridict(ball)
            print(ball.vx,ball.vy)
            print(move_x,move_y)
            if move_x!=-1 and move_y!=-1:
                #print("Send")
                ser.SendData(move_x, move_y, 1)

            #paddle.draw()
            #cv.imshow('main', paddle.frame_locate)
            #if cv.waitKey(1) & 0xff == ord('q'):
                #cv.destroyWindow('main')
             ##  break
            end=time.time()
    except Exception as err:
        print(err)
        pass
    
    