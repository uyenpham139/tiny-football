import pygame
import math
import random

class AIController:
    
    def __init__(self, difficulty="medium"):
        self.difficulty = difficulty
        self.set_difficulty(difficulty)
        self.cooldown = 0
        self.last_ball_pos = (0, 0)
        self.decision_timer = 0
        
    def set_difficulty(self, difficulty):
        if difficulty == "easy":
            self.reaction_time = 3 
            self.speed_multiplier = 0.7
            self.accuracy = 0.7
            self.aggression = 0.6  
        elif difficulty == "medium":
            self.reaction_time = 2 
            self.speed_multiplier = 0.9
            self.accuracy = 0.8
            self.aggression = 0.8  
        elif difficulty == "hard":
            self.reaction_time = 1  
            self.speed_multiplier = 1.1
            self.accuracy = 0.9
            self.aggression = 0.9  
        else:  
            self.reaction_time = 1  
            self.speed_multiplier = 1.3
            self.accuracy = 0.95
            self.aggression = 0.95  
    
    def update_ai_player(self, ai_rect, ball, human_rect, screen_width, screen_height, goal_left, goal_right, ai_side):

        self.cooldown = max(0, self.cooldown - 1)
        self.decision_timer += 1
        
        if self.decision_timer >= self.reaction_time:
            self.decision_timer = 0
            target_x, target_y = self._calculate_target_position(ai_rect, ball, human_rect, screen_width, screen_height, goal_left, goal_right, ai_side)
        else:
            if not hasattr(self, 'target_x'):
                self.target_x = ai_rect.centerx
                self.target_y = ai_rect.centery
            target_x, target_y = self.target_x, self.target_y

        self._move_toward_target(ai_rect, target_x, target_y, screen_width, screen_height)

        self.target_x = target_x
        self.target_y = target_y
    
    def _calculate_target_position(self, ai_rect, ball, human_rect, screen_width, screen_height, goal_left, goal_right, ai_side):

        if ai_side == "left":
            my_goal_x = goal_left.centerx
            my_goal_y = goal_left.centery  
            human_goal_x = goal_right.centerx  
            human_goal_y = goal_right.centery
        else:
            my_goal_x = goal_right.centerx
            my_goal_y = goal_right.centery
            human_goal_x = goal_left.centerx   
            human_goal_y = goal_left.centery
        
        ball_to_ai = math.hypot(ball.x - ai_rect.centerx, ball.y - ai_rect.centery)
        ball_to_my_goal = math.hypot(ball.x - my_goal_x, ball.y - my_goal_y)
        ball_to_human_goal = math.hypot(ball.x - human_goal_x, ball.y - human_goal_y)
        ball_to_human = math.hypot(ball.x - human_rect.centerx, ball.y - human_rect.centery)

        if ball_to_human_goal < 150 and ball_to_ai < 100:
            angle_to_human_goal = math.atan2(human_goal_y - ball.y, human_goal_x - ball.x)
            approach_distance = 25
            target_x = ball.x - math.cos(angle_to_human_goal) * approach_distance
            target_y = ball.y - math.sin(angle_to_human_goal) * approach_distance
            
        elif ball_to_my_goal < 100:
            target_x = my_goal_x + (ball.x - my_goal_x) * 0.5
            target_y = my_goal_y + (ball.y - my_goal_y) * 0.6
            
        elif ball_to_ai < 120:
            angle_to_human_goal = math.atan2(human_goal_y - ball.y, human_goal_x - ball.x)
            approach_distance = 30
            target_x = ball.x - math.cos(angle_to_human_goal) * approach_distance
            target_y = ball.y - math.sin(angle_to_human_goal) * approach_distance
            
        else:

            human_to_my_goal_x = my_goal_x - human_rect.centerx
            human_to_my_goal_y = my_goal_y - human_rect.centery

            intercept_x = human_rect.centerx + human_to_my_goal_x * 0.3
            intercept_y = human_rect.centery + human_to_my_goal_y * 0.3

            aggression_factor = self.aggression
            target_x = ball.x * aggression_factor + intercept_x * (1 - aggression_factor)
            target_y = ball.y * aggression_factor + intercept_y * (1 - aggression_factor)

            if ball_to_ai > 60:
                target_x = ball.x + (ball.x - ai_rect.centerx) * 0.2
                target_y = ball.y + (ball.y - ai_rect.centery) * 0.2

        time_factor = self.decision_timer * 0.1  

        if ball_to_human < 100:
            angle_to_human = math.atan2(human_rect.centery - ball.y, human_rect.centerx - ball.x)
            target_x += math.cos(angle_to_human + 3.14159) * 40
            target_y += math.sin(angle_to_human + 3.14159) * 40
        
        hunting_radius = 20
        target_x += math.cos(time_factor) * hunting_radius
        target_y += math.sin(time_factor * 1.3) * hunting_radius
        
        if random.random() > self.accuracy:
            target_x += random.randint(-30, 30)
            target_y += random.randint(-30, 30)

        margin = 30
        target_x = max(margin, min(screen_width - margin, target_x))
        target_y = max(margin, min(screen_height - margin, target_y))
        
        return target_x, target_y
    
    def _move_toward_target(self, ai_rect, target_x, target_y, screen_width, screen_height):

        dx = target_x - ai_rect.centerx
        dy = target_y - ai_rect.centery
        distance = math.hypot(dx, dy)
        
        if distance > 2:  
            dx /= distance
            dy /= distance

            base_speed = 4.0  
            speed = base_speed * self.speed_multiplier

            ai_rect.x += dx * speed
            ai_rect.y += dy * speed

            ai_rect.clamp_ip(pygame.Rect(0, 0, screen_width, screen_height))