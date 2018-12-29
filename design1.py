import time
import math


def constrain(value, lower_limit, upper_limit):
    if value < lower_limit:
        return lower_limit
    if value > upper_limit:
        return upper_limit
    return value


def newdatastrategy(strategy_var, ball, paddle):
    # predict_status == 0 => No risk
    # predict_status == 1 => Puck is moving to our field directly
    # predict_status == 2 => Puck is moving to our field with a bounce
    # predict_status == 3 => ?

    # GLOBAL VARIABLES
    defense_position = 100  # Y
    attack_position = 200  # Y



    PUCK_SIZE = int(ball.radius)
    EDGE1=40
    EDGE2=500
    ROBOT_CENTER_X = 280
    ROBOT_CENTER_Y = 550

    width = 0  # allow error

    if ball.ry < (paddle.ry-PUCK_SIZE) and strategy_var.sign==0:
        return ROBOT_CENTER_X,defense_position
    if strategy_var.sign==1:
        strategy_var.sign=0

    if  abs(ball.vy)<50 and ball.ry<ROBOT_CENTER_Y and strategy_var.status==0:
        strategy_var.status=1
        return ball.rx,ball.ry-PUCK_SIZE
    if strategy_var.status==1:
        strategy_var.status=0
        return ball.rx,ball.ry+6*PUCK_SIZE

    strategy_var.status=0

    # It´s time to predict...
    # Based on actual position and move vector we need to know the future...
    # Posible impact? speed Y is negative when the puck is moving to the robot
    if ball.vy < -25:  # -25
        predict_status = 1
        # Puck is comming...
        # We need to predict the puck position when it reaches our goal Y position = defense_position
        # slope formula: m = (y2-y1)/(x2-x1)
        if ball.vx == 0:  # To avoid division by 0
            ball.vx = 1
            slope = ball.vy / ball.vx
        else:
            slope = ball.vy / ball.vx

        # Prediction of the new x position at defense position: x2 = (y2-y1)/m + x1
        predict_y = defense_position + PUCK_SIZE
        predict_x = (predict_y - ball.ry) / slope
        predict_x += ball.rx
        # Prediction of the new x position at attack position
        predict_x_attack = ((attack_position + PUCK_SIZE) - ball.ry) / slope
        predict_x_attack += ball.rx

        # puck has a bounce with side wall?
        if (predict_x < EDGE1) or (predict_x > EDGE2):
            predict_status = 2
            strategy_var.predict_bounce = 1
            strategy_var.predict_bounce_status = 1
            # We start a new prediction
            # Wich side?
            if predict_x < EDGE1:
                # Left side. We calculare the impact point
                bounce_x = EDGE1
            else:
                # Right side. We calculare the impact point
                bounce_x = EDGE2
            bounce_y = (bounce_x - ball.rx) * slope + ball.ry
            predict_time = (bounce_y - ball.ry) / ball.vy  # time until bouce
            # bounce prediction => slope change  with the bounce, we only need to change the sign, easy!!
            slope = -slope
            predict_y = defense_position + PUCK_SIZE
            predict_x = (predict_y - bounce_y) / slope
            predict_x += bounce_x

            if (predict_x < EDGE1) or (predict_x > EDGE2):  # New bounce with side wall?
                # We do nothing then... with two bounces there are small risk of goal...
                strategy_var.predict_x_old = -1
                predict_status = 0
            else:
                # only one side bounce...
                # If the ball.vy has changed a lot this mean that the puck has touch one side
                if abs(ball.vy - ball.pre_vy) > 50:
                    # We dont make a new prediction...
                    strategy_var.predict_x_old = -1
                else:
                    # average of the results (some noise filtering)
                    if strategy_var.predict_x_old != -1:
                        predict_x = (strategy_var.predict_x_old + predict_x)/2
                    strategy_var.predict_x_old = predict_x
                    # We introduce a factor (120 instead of 100) to model the bounce (20% loss in speed)(to improcve...)
                    predict_time = predict_time + (predict_y - ball.ry) / ball.vy  # in ms
                    # predict_time -= VISION_SYSTEM_LAG
        else:  # No bounce, direct impact
            if strategy_var.predict_bounce_status == 1:  # This is the first direct impact trajectory after a bounce
                # We dont predict nothing new...
                strategy_var.predict_bounce_status = 0
            else:
                # average of the results (some noise filtering)
                if strategy_var.predict_x_old > 0:
                    predict_x = (strategy_var.predict_x_old + predict_x) /2
                    strategy_var.predict_x_old = predict_x

                predict_time = ((defense_position + PUCK_SIZE) - ball.ry) / ball.vy  # in ms
                predict_time_attack = ((attack_position + PUCK_SIZE) - ball.ry) / ball.vy  # in ms
                # predict_time -= VISION_SYSTEM_LAG
                # predict_time_attack -= VISION_SYSTEM_LAG
    else:  # Puck is moving slowly or to the other side
        strategy_var.predict_x_old = -1
        predict_status = 0
        strategy_var.predict_bounce = 0
        strategy_var.predict_bounce_status = 0

    # Default
    robot_status = 0  # Going to initial position (defense)

    if predict_status == 1:  # Puck comming?
        if strategy_var.predict_bounce == 0:  # Direct impact?
            if (predict_x > EDGE1+PUCK_SIZE) and (predict_x < EDGE2-PUCK_SIZE):
                if ball.vy > -150:
                    robot_status = 2  # defense+attack
                else:
                    robot_status = 1  # Puck too fast => only defense
            else:
                if predict_time < 500:
                    robot_status = 1  # 1  # Defense
                else:
                    robot_status = 0
        else:  # Puck come from a bounce?
            if ball.vy > -160:  # Puck is moving fast?
                robot_status = 2  # Defense+Attack
            else:
                robot_status = 1  # Defense (too fast...)

    # Prediction with side bound
    if predict_status == 2:
        if predict_time < 500:
            # Limit movement
            predict_x = constrain(predict_x, ROBOT_CENTER_X - (PUCK_SIZE * 4), ROBOT_CENTER_X + (PUCK_SIZE * 4))
            robot_status = 1  # only defense mode
        else:
            robot_status = 0

    # If the puck is moving slowly in the robot field we could start an attack
    if (predict_status == 0) and (ball.ry < ROBOT_CENTER_Y) and (abs(ball.vy) < 60) and (abs(ball.vx) < 100):
        robot_status = 3

    if robot_status == 0:
        strategy_var.attack_time = 0
        if ~(paddle.y > (defense_position + PUCK_SIZE) and ball.ry < paddle.y and ball.rx > (ROBOT_CENTER_X - PUCK_SIZE * 5) and ball.rx < (ROBOT_CENTER_X + PUCK_SIZE * 5)) :
            com_pos_y = defense_position
            com_pos_x = ROBOT_CENTER_X  # center X axis
        else:
            com_pos_y = paddle.y
            com_pos_x = paddle.x  # center X axis# The robot stays on it´s position
        if (abs(com_pos_x - paddle.x) < width) and (abs(com_pos_x - paddle.x) < width):
            return int(paddle.x), int(paddle.y)
        else:
            return int(com_pos_x), int(com_pos_y)

    elif robot_status == 1:
        predict_x = constrain(predict_x, EDGE1+PUCK_SIZE,EDGE2-PUCK_SIZE)  # we leave some space near the borders...
        strategy_var.attack_time = 0
        if ~(paddle.y > (defense_position + PUCK_SIZE) and ball.ry < paddle.y and ball.rx > (ROBOT_CENTER_X - PUCK_SIZE * 5) and ball.rx < (ROBOT_CENTER_X + PUCK_SIZE * 5)):
            com_pos_y = defense_position
            com_pos_x = predict_x  # center X axis
        else:
            com_pos_y = paddle.y
            com_pos_x = paddle.x  # center X axis# The robot stays on it´s position
        if (abs(com_pos_x - paddle.x) < width) and (abs(com_pos_x - paddle.x) < width):
            return [paddle.x, paddle.y]
        else:
            return [com_pos_x, com_pos_y]

    elif robot_status == 2:
        if predict_time_attack < 150:  # If time is less than 150ms we start the attack HACELO DEPENDIENTE DE LA VELOCIDAD?? NO, solo depende de cuanto tardemos desde defensa a ataque...

            if ~(paddle.y > (defense_position + PUCK_SIZE) and ball.ry < paddle.y and ball.rx > (ROBOT_CENTER_X - PUCK_SIZE * 5) and ball.rx < (ROBOT_CENTER_X + PUCK_SIZE * 5)):
                com_pos_y = attack_position + PUCK_SIZE * 6
                com_pos_x = predict_x_attack
            else:
                com_pos_y = paddle.y
                com_pos_x = paddle.x

            if (abs(com_pos_x - paddle.x) < width) and (abs(com_pos_x - paddle.x) < width):
                return int(paddle.x), int(paddle.y)
            else:
                return int(com_pos_x), int(com_pos_y)

        else:  # Defense position
            strategy_var.attack_time = 0
            if ~(paddle.y > (defense_position + PUCK_SIZE) and ball.ry < paddle.y and ball.rx > (ROBOT_CENTER_X - PUCK_SIZE * 5) and ball.rx < (ROBOT_CENTER_X + PUCK_SIZE * 5)):
                com_pos_y = defense_position
                com_pos_x = predict_x
            else:
                com_pos_y = paddle.y
                com_pos_x = paddle.x

            if (abs(com_pos_x - paddle.x) < width) and (abs(com_pos_x - paddle.x) < width):
                return int(paddle.x), int(paddle.y)
            else:
                return int(com_pos_x), int(com_pos_y)

    elif robot_status == 3:
        if strategy_var.attack_time == 0:
            attack_predict_x = (ball.rx + ball.vx * 500)
            attack_predict_y = (ball.ry + ball.vy * 500)
            if (attack_predict_x > (PUCK_SIZE * 3)) and (attack_predict_x < EDGE2-PUCK_SIZE) and (attack_predict_y > defense_position) and (attack_predict_y < ROBOT_CENTER_Y):
                strategy_var.attack_time = time.time() + 500  # Prepare an attack in 500ms
                strategy_var.attack_pos_x = attack_predict_x  # predict_x
                strategy_var.attack_pos_y = attack_predict_y  # predict_y
                strategy_var.attack_status = 1
                com_pos_x = strategy_var.attack_pos_x
                com_pos_y = strategy_var.attack_pos_y - PUCK_SIZE * 4

                if ~(paddle.y > (defense_position + PUCK_SIZE) and ball.ry < paddle.y and ball.rx > (ROBOT_CENTER_X - PUCK_SIZE * 5) and ball.rx < (ROBOT_CENTER_X + PUCK_SIZE * 5)):
                    com_pos_y = paddle.y
                    com_pos_x = paddle.x  # center X axis# The robot stays on it´s position
                if (abs(com_pos_x - paddle.x) < width) and (abs(com_pos_x - paddle.x) < width):
                    return int(paddle.x), int(paddle.y)
                else:
                    return int(com_pos_x), int(com_pos_y)

            else:
                strategy_var.attack_time = 0  # Continue waiting for the right attack moment...
                strategy_var.attack_status = 0
                # And go to defense position
                com_pos_y = defense_position
                com_pos_x = ROBOT_CENTER_X  # center X axis
                if ~(paddle.y > (defense_position + PUCK_SIZE) and ball.ry < paddle.y and ball.rx > (ROBOT_CENTER_X - PUCK_SIZE * 5) and ball.rx < (ROBOT_CENTER_X + PUCK_SIZE * 5)):
                    com_pos_y = defense_position
                    com_pos_x = ROBOT_CENTER_X  # center X axis
                else:
                    com_pos_y = paddle.y
                    com_pos_x = paddle.x  # center X axis# The robot stays on it´s position
                if (abs(com_pos_x - paddle.x) < width) and (abs(com_pos_x - paddle.x) < width):
                    return int(paddle.x), int(paddle.y)
                else:
                    return int(com_pos_x), int(com_pos_y)
        else:
            if strategy_var.attack_status == 1:
                impact_time = strategy_var.attack_time - time.time()
                if impact_time < 170:  # less than 150ms to start the attack
                    # Attack movement
                    strategy_var.attack_status = 2  # Attacking
                    if ~(paddle.y > (defense_position + PUCK_SIZE) and ball.ry < paddle.y and ball.rx > (ROBOT_CENTER_X - PUCK_SIZE * 5) and ball.rx < (ROBOT_CENTER_X + PUCK_SIZE * 5)):
                        com_pos_y = (ball.ry + ball.vy * impact_time) + PUCK_SIZE * 6
                        com_pos_x = (ball.rx + ball.vx * impact_time)  # center X axis
                    else:
                        com_pos_y = paddle.y
                        com_pos_x = paddle.x

                    if (abs(com_pos_x - paddle.x) < width) and (abs(com_pos_x - paddle.x) < width):
                        return int(paddle.x), int(paddle.y)
                    else:
                        return int(com_pos_x), int(com_pos_y)

                else:  # attack_status=1 but it´s no time to attack yet
                    # Go to pre-attack position

                    if ~(paddle.y > (defense_position + PUCK_SIZE) and ball.ry < paddle.y and ball.rx > (ROBOT_CENTER_X - PUCK_SIZE * 5) and ball.rx < (ROBOT_CENTER_X + PUCK_SIZE * 5)):
                        com_pos_y = strategy_var.attack_pos_y - PUCK_SIZE * 4
                        com_pos_x = strategy_var.attack_pos_x
                    else:
                        com_pos_y = paddle.y
                        com_pos_x = paddle.x

                    if (abs(com_pos_x - paddle.x) < width) and (abs(com_pos_x - paddle.x) < width):
                        return int(paddle.x), int(paddle.y)
                    else:
                        return int(com_pos_x), int(com_pos_y)

            if strategy_var.attack_status == 2:
                if time.time() > (strategy_var.attack_time + 80):  # Attack move is done? => Reset to defense position
                    strategy_var.attack_time = 0
                    robot_status = 0
                    strategy_var.attack_status = 0
    else:
        predict_x = constrain(predict_x, EDGE1+PUCK_SIZE,EDGE2-PUCK_SIZE)  # we leave some space near the borders...
        strategy_var.attack_time = 0
        if ~(paddle.y > (defense_position + PUCK_SIZE) and ball.ry < paddle.y and ball.rx > (ROBOT_CENTER_X - PUCK_SIZE * 5) and ball.rx < (ROBOT_CENTER_X + PUCK_SIZE * 5)):
            com_pos_y = defense_position
            com_pos_x = predict_x
        else:
            com_pos_y = paddle.y
            com_pos_x = paddle.x
        if (abs(com_pos_x - paddle.x) < width) and (abs(com_pos_x - paddle.x) < width):
            return int(paddle.x), int(paddle.y)
        else:
            return int(com_pos_x), int(com_pos_y)



'''def attack(ser,mcu_x,mcu_y):
    if ser.ball.ry>700:
        return 280,100
    else:
        if (ser.ball.ry>460 and ser.ball.ry<=700) or ser.ball.ry<mcu_y and ser.msg!='a':
            return ser.ball.rx,100
        elif ser.ball.ry<460 and ser.ball.ry>mcu_y and ser.msg!=None:
            ser.msg='a'
            return ser.ball.rx,ser.ball.ry+10
        else:
            return 280,100'''

