import math
import time

def pusher_defense(Ball):
    ball_x = Ball.rx
    ball_y = Ball.ry
    ball_vx = Ball.vx
    ball_vy = Ball.vy
    #pusher_x = Paddle.x
    #pusher_y = Paddle.y

    ball_x1 = Ball.pre_x
    ball_y1 = Ball.pre_y
    ball_vx1 = Ball.pre_vx
    ball_vy1 = Ball.pre_vy
    #pusher_x1 = Paddle.pre_x
    #pusher_y1 = Paddle.pre_y

    ball_x2 = Ball.ppre_x
    ball_y2 = Ball.ppre_y
    ball_vx2 = Ball.ppre_vx
    ball_vy2 = Ball.ppre_vy
    #pusher_x2 = Paddle.ppre_x
   # pusher_y2 = Paddle.ppre_y
    corner_points = {'0':[40,100],'1':[480,100],'2':[480,520],'3':[40,520]}
    y_limit = 100
    width = 5
    try:
        #y_limit
        k = ball_vy / ball_vx
        b = ball_y - k * ball_x
        m = (y_limit - b) / k
        while (k > 0 and m < corner_points['0'][0]) or (k < 0 and m > corner_points['2'][0]):
            if k > 0 and m < corner_points['0'][0]:
                b = 2 * k * corner_points['0'][0] + b
                k = -k
                m = y_limit-b / k
            if k < 0 and m > corner_points['2'][0]:
                b = 2 * k * corner_points['2'][0] + b
                k = -k
                m = y_limit-b / k
        predict_y = y_limit
        predict_x = (predict_y - b) / k




        k1 = ball_vy1 / ball_vx1
        b1 = ball_y1 - k1 * ball_x1
        m1 = (y_limit - b1) / k1
        while (k1 > 0 and m1 < corner_points['0'][0]) or (k1 < 0 and m1 > corner_points['2'][0]):
            if k1 > 0 and m1 < corner_points['0'][0]:
                b1 = 2 * k1 * corner_points['0'][0] + b1
                k1 = -k1
                m1 = y_limit - b1 / k1
            if k1 < 0 and m1 > corner_points['2'][0]:
                b1 = 2 * k1 * corner_points['2'][0] + b1
                k1 = -k1
                m1 = y_limit - b1 / k1
        predict_y1 = y_limit
        predict_x1 = (predict_y - b1) / k1

        k2 = ball_vy2 / ball_vx2
        b2 = ball_y2 - k2 * ball_x2
        m2 = (y_limit - b2) / k2
        while (k2 > 0 and m2 < corner_points['0'][0]) or (k2 < 0 and m2 > corner_points['2'][0]):
            if k2 > 0 and m2 < corner_points['0'][0]:
                b2 = 2 * k2 * corner_points['0'][0] + b2
                k2 = -k2
                m2 = y_limit - b2 / k2
            if k2 < 0 and m2 > corner_points['2'][0]:
                b2 = 2 * k2 * corner_points['2'][0] + b2
                k2 = -k2
                m2 = y_limit - b2 / k2
        predict_y2 = y_limit
        predict_x2 = (predict_y - b2) / k2

        sequence_x = [predict_x, predict_x1, predict_x2]
        sequence_y = [predict_y, predict_y1, predict_y2]
        sorted(sequence_y)
        sorted(sequence_y)

        predict_x = sequence_x[1]
        predict_y = sequence_y[1]

        if predict_x>480 or predict_x<40 or predict_y>520 or predict_y<100:
            return -1,-1
        else:
            return int(predict_x), int(predict_y)
    except:
        return -1,-1

