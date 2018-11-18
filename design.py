import math


def pusher_defense(Ball, Paddle):
    try:
        ball_x = Ball.x
        ball_y = Ball.y
        ball_vx = Ball.vx
        ball_vy = Ball.vy
        pusher_x = Paddle.x
        pusher_y = Paddle.y
        corner_points = {'0':[40,100],'1':[480,100],'2':[480,520],'3':[40,520]}
        y_limit = 100
        width = 5

        #y_limit
        k = ball_vy / ball_vx
        b = ball_y - k * ball_x
        m = (y_limit - b) / k
        while (k > 0 and m < corner_points['0'][0]) or (k < 0 and m > corner_points['2'][0]):
            if k > 0 and m < corner_points['0'][0]:
                b = 2 * k * corner_points['0'][0] + b
                k = -k
                m = (y_limit -b) / k
            if k < 0 and m > corner_points['2'][0]:
                b = 2 * k * corner_points['2'][0] + b
                k = -k
                m = (y_limit -b) / k
        predict_y = y_limit
        predict_x = (predict_y - b) / k
        if abs(predict_x - pusher_x) < width:
            return -1, -1
        else:
            return int(predict_x), int(predict_y)
    except:
        return -1,-1

