from tkinter import *
from module.Hockey import*
from module.func import *
import tkinter.ttk as ttk
import threading
import tkinter.filedialog

# 摄像头设置窗口
def cam_set_gui(desk):
    root = Tk()
    canvas = Set_Win(root,"摄像头设置",200,100)
    
    def select():  # 选择键的响应函数
        desk.id = int(Dev.get())
        # desk.set_capture()
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

# 透视变换设置窗口
def transform_set_gui(desk):
    root = Tk()
    canvas = Set_Win(root, "摄像头控制台——透视变换设置", 300, 500)
    button1 = Button(root, text='显示原视频', width=15, height=5, command=lambda:show_original(desk, desk))
    id_button1 = canvas.create_window(150, 100, window=button1)
    button2 = Button(root, text='角点标定', width=15, height=5, command=desk.set_corner_dict)
    id_button2 = canvas.create_window(150, 250, window=button2)
    button3 = Button(root, text='显示变换后视频', width=15, height=5, command=lambda :show_transform(desk,desk))
    id_button3 = canvas.create_window(150, 400, window=button3)
    root.mainloop()

# 球追踪设置窗口
def ball_set_gui(desk,ball):
    root = Tk()
    canvas = Set_Win(root, "摄像头控制台——球追踪设置", 300, 600)
    ball_before = Ball()

    hmin, smin, vmin, hmax, smax, vmax, kernel1, kernel2, sleep_time = Set_Ball_Track_Param(root,canvas,ball)
    
    def recover_default():  # 把各参数恢复默认
        ball.kernel_open_size = 10
        ball.kernel_close_size = 6
        ball.lower = np.array([115, 50, 50])
        ball.upper = np.array([125, 255, 255])
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
        ball.lower = np.array([int(hmin.get()), int(smin.get()), int(vmin.get())])
        ball.upper = np.array([int(hmax.get()), int(smax.get()), int(vmax.get())])
        ball.kernel_open_size = int(kernel1.get())
        ball.kernel_close_size = int(kernel2.get())
        ball.time = float(sleep_time.get())
        showinfo("提示", "新参数设置成功！")
        root.destroy()
    
    def save_setting():  # 将设置保存为文件
        path = tkinter.filedialog.asksaveasfilename()
        if ('(球追踪参数存档)' in path) == False:
            path = './save/' + path + '(球追踪参数存档).txt'
        
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
        ball.lower = np.array([int(s[0]), int(s[1]), int(s[2])])
        ball.upper = np.array([int(s[3]), int(s[4]), int(s[5])])
        ball.kernel_open_size = int(s[6])
        ball.kernel_close_size = int(s[7])
        ball.time = float(s[8])
        f.close()
        hmin.set(str(ball.lower[0]))
        smin.set(str(ball.lower[1]))
        vmin.set(str(ball.lower[2]))
        hmax.set(str(ball.upper[0]))
        smax.set(str(ball.upper[1]))
        vmax.set(str(ball.upper[2]))
        kernel1.set(str(ball.kernel_open_size))
        kernel2.set(str(ball.kernel_close_size))
        sleep_time.set(ball.time)
        showinfo("提示", "参数读档成功！")
        root.update()
    button1 = Button(root, text='显示原视频', width=10, height=3, command=lambda :show_original(desk,ball))
    button2 = Button(root, text='显示阈值效果', width=10, height=3, command=lambda:show_segmentation(desk,ball,hmin, smin, vmin, hmax, smax, vmax))
    button3 = Button(root, text='显示降噪效果', width=10, height=3, command=lambda:show_reduce_noise(desk,ball,hmin, smin, vmin, hmax, smax, vmax ,kernel1,kernel2))
    button4 = Button(root, text='显示二值图像', width=10, height=3, command=lambda:show_thresh(desk,ball,hmin, smin, vmin, hmax, smax, vmax))
    button5 = Button(root, text='恢复默认', width=5, height=1, command=recover_default)
    button6 = Button(root, text='设置启动', width=5, height=1, command=set_change)
    button7 = Button(root, text='保存设置', width=5, height=1, command=save_setting)
    button8 = Button(root, text='读取设置', width=5, height=1, command=load_setting)
    button9 = Button(root, text='显示定位追踪效果', width=12, height=3, command=lambda:show_track(desk,ball,ball_before,hmin, smin, vmin, hmax, smax, vmax,kernel1,kernel2,sleep_time))
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


# 手柄追踪设置窗口
def paddle_set_gui(desk, paddle):
    root = Tk()
    canvas = Set_Win(root, "摄像头控制台——手柄追踪设置", 300, 600)
    
    hmin, smin, vmin, hmax, smax, vmax, kernel1, kernel2 = Set_Paddle_Track_Param(root, canvas, paddle)
    
    def recover_default():  # 把各参数恢复默认
        paddle.kernel_open_size = 10
        paddle.kernel_close_size = 6
        paddle.lower = np.array([70, 50, 50])
        paddle.upper = np.array([90, 255, 255])
        paddle.time = 0
        hmin.set('70')
        smin.set('50')
        vmin.set('50')
        hmax.set('90')
        smax.set('255')
        vmax.set('255')
        kernel1.set('10')
        kernel2.set('6')
        root.update()
        showinfo("提示", "重新设为默认！")
    
    def set_change():  # 将所有参数导入ball对象
        paddle.lower = np.array([int(hmin.get()), int(smin.get()), int(vmin.get())])
        paddle.upper = np.array([int(hmax.get()), int(smax.get()), int(vmax.get())])
        paddle.kernel_open_size = int(kernel1.get())
        paddle.kernel_close_size = int(kernel2.get())
        showinfo("提示", "新参数设置成功！")
        root.destroy()
    
    def save_setting():  # 将设置保存为文件
        path = tkinter.filedialog.asksaveasfilename()
        if ('(手柄追踪参数存档)' in path) == False:
            path='./save/'+path+'(手柄追踪参数存档).txt'
        f = open(path, 'w')
        f.write(hmin.get() + '|' + smin.get() + '|' + vmin.get() + '|' + hmax.get() + '|' +
                smax.get() + '|' + vmax.get() + '|' + kernel1.get() + '|' +
                kernel2.get())
        f.close()
        showinfo("提示", "参数存档成功！")
    
    def load_setting():  # 从文件导入设置
        path = tkinter.filedialog.askopenfilename()
        f = open(path, 'r+')
        s = f.readline()
        s = s.split('|')
        paddle.lower = np.array([int(s[0]), int(s[1]), int(s[2])])
        paddle.upper = np.array([int(s[3]), int(s[4]), int(s[5])])
        paddle.kernel_open_size = int(s[6])
        paddle.kernel_close_size = int(s[7])
        paddle.time = float(s[8])
        f.close()
        hmin.set(str(paddle.lower[0]))
        smin.set(str(paddle.lower[1]))
        vmin.set(str(paddle.lower[2]))
        hmax.set(str(paddle.upper[0]))
        smax.set(str(paddle.upper[1]))
        vmax.set(str(paddle.upper[2]))
        kernel1.set(str(paddle.kernel_open_size))
        kernel2.set(str(paddle.kernel_close_size))
        showinfo("提示", "参数读档成功！")
        root.update()
    
    button1 = Button(root, text='显示原视频', width=10, height=3, command=lambda: show_original(desk, paddle))
    button2 = Button(root, text='显示阈值效果', width=10, height=3,
                     command=lambda: show_segmentation(desk, paddle, hmin, smin, vmin, hmax, smax, vmax))
    button3 = Button(root, text='显示降噪效果', width=10, height=3,
                     command=lambda: show_reduce_noise(desk, paddle, hmin, smin, vmin, hmax, smax, vmax,kernel1,kernel2))
    button4 = Button(root, text='显示二值图像', width=10, height=3,
                     command=lambda: show_thresh(desk, paddle, hmin, smin, vmin, hmax, smax, vmax))
    button5 = Button(root, text='恢复默认', width=5, height=1, command=recover_default)
    button6 = Button(root, text='设置启动', width=5, height=1, command=set_change)
    button7 = Button(root, text='保存设置', width=5, height=1, command=save_setting)
    button8 = Button(root, text='读取设置', width=5, height=1, command=load_setting)
    button9 = Button(root, text='显示定位效果', width=12, height=3,
                     command=lambda: show_locate(desk,paddle,hmin, smin, vmin, hmax, smax, vmax,kernel1,kernel2))
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

#摄像头设置窗口
def Cam_Setting(desk, ball, paddle):
    tk = Tk()
    tk.title("摄像头设置 ——XYZ小组")
    tk.maxsize(250, 400)  # （宽度，高度）
    tk.minsize(250, 400)
    Center(tk, 250, 400)
    tk.resizable(width=False, height=False)
    canvas = Canvas(tk, width=250, height=400, bg='whitesmoke')
    canvas.pack()
    ball.corner_points = desk.corner_points
    ball.frame_original = desk.frame
    button1 = Button(tk, text='摄像头设置', width=10, height=3, command=lambda :cam_set_gui(desk))
    id_button1 = canvas.create_window(130, 60, window=button1)
    button2 = Button(tk, text='透视变换设置', width=10, height=3, command=lambda:transform_set_gui(desk))
    id_button2 = canvas.create_window(130, 150, window=button2)
    button3 = Button(tk, text='球追踪设置', width=10, height=3, command=lambda :ball_set_gui(desk,ball))
    id_button3 = canvas.create_window(130, 240, window=button3)
    button4 = Button(tk, text='手柄追踪设置', width=10, height=3, command=lambda:paddle_set_gui(desk,paddle))
    id_button4 = canvas.create_window(130, 330, window=button4)
    tk.mainloop()



