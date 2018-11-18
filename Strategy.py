import time
import math

#GLOBAL VARIABLES
defense_position#Y
attack_position#Y

PUCK_SIZE
TABLE_LENGTH=490
TABLE_WIDTH=520
ROBOT_CENTER_X=TABLE_WIDTH/2  
ROBOT_CENTER_Y=TABLE_LENGTH/2

Width=8#allow error

def constrain(value, lower_limit, upper_limit):
    if(value < lower_limit): 
        return lower_limit
    if(value > upper_limit):
        return upper_limit
    return value

# Return the predicted position of the puck in predict_time miliseconds
def predictPuckXPosition(predict_time):
    #predict_time += VISION_SYSTEM_LAG
    return (puckCoordX + puckSpeedX * predict_time)

# Return the predicted position of the puck in predict_time miliseconds
def predictPuckYPosition(predict_time):
    #predict_time += VISION_SYSTEM_LAG
    return (puckCoordY + puckSpeedX * predict_time )
    
# This function returns true if the puck is behind the robot and there are posibilities of an auto goal when the robots moves back
def checkOwnGoal():
    if (real_position_y > (defense_position + PUCK_SIZE)) and (puckCoordY < real_position_y) and (puckCoordX > (ROBOT_CENTER_X - PUCK_SIZE * 5)) and (puckCoordX < (ROBOT_CENTER_X + PUCK_SIZE * 5)):
        return true
    else:
        return false

def newDataStrategy(attack_time,attack_status,predict_x_old,predict_bounce,predict_bounce_status,puckCoordX,puckCoordY,puckSpeedX,puckSpeedY,puckOldSpeedX,puckOldSpeedY,real_position_x,real_position_y):
    # predict_status == 0 => No risk
    # predict_status == 1 => Puck is moving to our field directly
    # predict_status == 2 => Puck is moving to our field with a bounce
    # predict_status == 3 => ?
    # It´s time to predict...
    # Based on actual position and move vector we need to know the future...
    # Posible impact? speed Y is negative when the puck is moving to the robot
    if puckSpeedY < -50:  #-25
        predict_status = 1
        # Puck is comming...
        # We need to predict the puck position when it reaches our goal Y position = defense_position
        # slope formula: m = (y2-y1)/(x2-x1)
        if puckSpeedX== 0:  # To avoid division by 0
            puckSpeedX=1
            slope = puckSpeedY/puckSpeedX
        else:
            slope = puckSpeedY/puckSpeedX

        # Prediction of the new x position at defense position: x2 = (y2-y1)/m + x1
        predict_y = defense_position + PUCK_SIZE
        predict_x = (predict_y - puckCoordY) / slope
        predict_x += puckCoordX
        # Prediction of the new x position at attack position
        predict_x_attack = ((attack_position + PUCK_SIZE) - puckCoordY) / slope
        predict_x_attack += puckCoordX

        # puck has a bounce with side wall?
        if (predict_x < PUCK_SIZE) or (predict_x > (TABLE_WIDTH - PUCK_SIZE)):
            predict_status = 2
            predict_bounce = 1
            predict_bounce_status = 1
            # We start a new prediction
            # Wich side?
            if predict_x < PUCK_SIZE:
                #Left side. We calculare the impact point
                bounce_x = PUCK_SIZE
            else:
                #Right side. We calculare the impact point
                bounce_x = (TABLE_WIDTH - PUCK_SIZE)
            bounce_y = (bounce_x - puckCoordX) * slope + puckCoordY
            predict_time = (bounce_y - puckCoordY)  / puckSpeedY # time until bouce
            # bounce prediction => slope change  with the bounce, we only need to change the sign, easy!!
            slope = -slope
            predict_y = defense_position + PUCK_SIZE
            predict_x = (predict_y - bounce_y) / slope
            predict_x += bounce_x

            if (predict_x < PUCK_SIZE) or (predict_x > (TABLE_WIDTH - PUCK_SIZE)): # New bounce with side wall?
                # We do nothing then... with two bounces there are small risk of goal...
                predict_x_old = -1
                predict_status = 0
            else:
                # only one side bounce...
                # If the puckSpeedY has changed a lot this mean that the puck has touch one side
                if abs(puckSpeedY - puckOldSpeedY) > 50:
                    # We dont make a new prediction...
                    predict_x_old = -1
                else:
                    # average of the results (some noise filtering)
                    if predict_x_old != -1:
                        predict_x = (predict_x_old + predict_x) >> 1
                    predict_x_old = predict_x
                    # We introduce a factor (120 instead of 100) to model the bounce (20% loss in speed)(to improcve...)
                    predict_time = predict_time + (predict_y - puckCoordY) / puckSpeedY # in ms
                    #predict_time -= VISION_SYSTEM_LAG
        else:  # No bounce, direct impact
            if predict_bounce_status == 1:  # This is the first direct impact trajectory after a bounce
                # We dont predict nothing new...
                predict_bounce_status = 0
            else:
                # average of the results (some noise filtering)
                if predict_x_old > 0:
                    predict_x = (predict_x_old + predict_x) >> 1
                    predict_x_old = predict_x

                predict_time = ((defense_position + PUCK_SIZE) - puckCoordY) / puckSpeedY # in ms
                predict_time_attack = ((attack_position + PUCK_SIZE) - puckCoordY) / puckSpeedY # in ms
                    #predict_time -= VISION_SYSTEM_LAG
                    #predict_time_attack -= VISION_SYSTEM_LAG
    else :# Puck is moving slowly or to the other side
        predict_x_old = -1
        predict_status = 0
        predict_bounce = 0
        predict_bounce_status = 0
        
    # Default
    robot_status = 0   # Going to initial position (defense)

    if predict_status == 1: # Puck comming?
        if predict_bounce == 0:  # Direct impact?
            if (predict_x > (ROBOT_MIN_X + (PUCK_SIZE * 2))) and (predict_x < (ROBOT_MAX_X - (PUCK_SIZE * 2))):
                if puckSpeedY > -280:
                    robot_status = 2  # defense+attack
                else:
                    robot_status = 1  # Puck too fast => only defense
            else:
                if predict_time < 500:
                    robot_status = 1 #1  # Defense
                else:
                    robot_status = 0
        else: # Puck come from a bounce?
            if puckSpeedY > -160: # Puck is moving fast?
                robot_status = 2  # Defense+Attack
            else:
                robot_status = 1  # Defense (too fast...)

    # Prediction with side bound
    if predict_status == 2:
        if predict_time < 500:
        # Limit movement
            predict_x = constrain(predict_x, ROBOT_CENTER_X - (PUCK_SIZE * 4), ROBOT_CENTER_X + (PUCK_SIZE * 4))
            robot_status = 1   # only defense mode
        else:
            robot_status = 0

    # If the puck is moving slowly in the robot field we could start an attack
    if (predict_status == 0) and (puckCoordY < (ROBOT_CENTER_Y - 20)) and (abs(puckSpeedY) < 60) and (abs(puckSpeedX) < 100):
        robot_status = 3
  
    if robot_status==0 :
        attack_time = 0
        if checkOwnGoal() == false :
            com_pos_y = defense_position
            com_pos_x = ROBOT_CENTER_X  #center X axis
        else:
            com_pos_y = real_position_y
            com_pos_x = real_position_x  #center X axis# The robot stays on it´s position
        if (abs(com_pos_x - real_position_x) < width) and (abs(com_pos_x - real_position_x) < width):
            return [-1, -1]
        else:
            return [com_pos_x, com_pos_y]

    elif robot_status==1 :
        predict_x = constrain(predict_x, (PUCK_SIZE * 3), TABLE_WIDTH - (PUCK_SIZE * 3))  # we leave some space near the borders...
        attack_time = 0
        if checkOwnGoal() == false :
            com_pos_y = defense_position
            com_pos_x = predict_x  #center X axis
        else:
            com_pos_y = real_position_y
            com_pos_x = real_position_x  #center X axis# The robot stays on it´s position
        if (abs(com_pos_x - real_position_x) < width) and (abs(com_pos_x - real_position_x) < width):
            return [-1, -1]
        else:
            return [com_pos_x, com_pos_y]

    elif robot_status==2 : 
        if predict_time_attack < 150: # If time is less than 150ms we start the attack HACELO DEPENDIENTE DE LA VELOCIDAD?? NO, solo depende de cuanto tardemos desde defensa a ataque...
            
            if checkOwnGoal() == false :
                com_pos_y = attack_position + PUCK_SIZE * 4
                com_pos_x = predict_x_attack 
            else:
                com_pos_y = real_position_y
                com_pos_x = real_position_x  
                
            if (abs(com_pos_x - real_position_x) < width) and (abs(com_pos_x - real_position_x) < width):
                return [-1, -1]
            else:
                return [com_pos_x, com_pos_y]
            
        else:# Defense position
            attack_time = 0
            if checkOwnGoal() == false :
                com_pos_y = defense_position
                com_pos_x = predict_x 
            else:
                com_pos_y = real_position_y
                com_pos_x = real_position_x  
                
            if (abs(com_pos_x - real_position_x) < width) and (abs(com_pos_x - real_position_x) < width):
                return [-1, -1]
            else:
                return [com_pos_x, com_pos_y]

    elif robot_status==3 : 
        if attack_time == 0:
            attack_predict_x = predictPuckXPosition(500)
            attack_predict_y = predictPuckYPosition(500)
            if (attack_predict_x > (PUCK_SIZE * 3)) and (attack_predict_x < (TABLE_WIDTH - (PUCK_SIZE * 3))) and (attack_predict_y > (PUCK_SIZE * 4)) and (attack_predict_y < (ROBOT_CENTER_Y - (PUCK_SIZE * 5))):
                attack_time = time.time + 500  # Prepare an attack in 500ms
                attack_pos_x = attack_predict_x  # predict_x
                attack_pos_y = attack_predict_y  # predict_y
                attack_status = 1
                com_pos_x = attack_pos_x
                com_pos_y = attack_pos_y - PUCK_SIZE * 4
                
                if checkOwnGoal() == true :
                    com_pos_y = real_position_y
                    com_pos_x = real_position_x  #center X axis# The robot stays on it´s position
                if (abs(com_pos_x - real_position_x) < width) and (abs(com_pos_x - real_position_x) < width):
                    return [-1, -1]
                else:
                    return [com_pos_x, com_pos_y]
                
            else:
                attack_time = 0  # Continue waiting for the right attack moment...
                attack_status = 0
                # And go to defense position
                com_pos_y = defense_position
                com_pos_x = ROBOT_CENTER_X  #center X axis
                if checkOwnGoal() == false :
                    com_pos_y = defense_position
                    com_pos_x = ROBOT_CENTER_X  #center X axis
                else:
                    com_pos_y = real_position_y
                    com_pos_x = real_position_x  #center X axis# The robot stays on it´s position
                if (abs(com_pos_x - real_position_x) < width) and (abs(com_pos_x - real_position_x) < width):
                    return [-1, -1]
                else:
                    return [com_pos_x, com_pos_y]
        else:
            if attack_status == 1:
                impact_time = attack_time - time.time
                if impact_time < 170:  # less than 150ms to start the attack
                    # Attack movement
                    attack_status = 2 # Attacking
                    if checkOwnGoal() == false :
                        com_pos_y = predictPuckYPosition(impact_time)+ PUCK_SIZE * 2
                        com_pos_x = predictPuckXPosition(impact_time)  #center X axis
                    else:
                        com_pos_y = real_position_y
                        com_pos_x = real_position_x 
                
                    if (abs(com_pos_x - real_position_x) < width) and (abs(com_pos_x - real_position_x) < width):
                        return [-1, -1]
                    else:
                        return [com_pos_x, com_pos_y]
                    
                else:  # attack_status=1 but it´s no time to attack yet
                    # Go to pre-attack position
                    
                    if checkOwnGoal() == false :
                        com_pos_y = attack_pos_y - PUCK_SIZE * 4
                        com_pos_x = attack_pos_x
                    else:
                        com_pos_y = real_position_y
                        com_pos_x = real_position_x 
                
                    if (abs(com_pos_x - real_position_x) < width) and (abs(com_pos_x - real_position_x) < width):
                        return [-1, -1]
                    else:
                        return [com_pos_x, com_pos_y]
                        
            if attack_status == 2:
                if time.time > (attack_time + 80): # Attack move is done? => Reset to defense position
                    attack_time = 0
                    robot_status = 0
                    attack_status = 0
    else :
        predict_x = constrain(predict_x, (PUCK_SIZE * 3), TABLE_WIDTH - (PUCK_SIZE * 3))  # we leave some space near the borders...
        attack_time = 0
        if checkOwnGoal() == false :
            com_pos_y = defense_position
            com_pos_x = predict_x  
        else:
            com_pos_y = real_position_y
            com_pos_x = real_position_x  
        if (abs(com_pos_x - real_position_x) < width) and (abs(com_pos_x - real_position_x) < width):
            return [-1, -1]
        else:
            return [com_pos_x, com_pos_y]

