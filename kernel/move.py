import random
import math

class Movement:
    def __init__(self, screen_width, screen_height, target_radius=30, initial_speed_level=3, speed_increment=2):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.target_radius = target_radius
        
        self.speed_per_level = 1.5
        self.speed_level = initial_speed_level
        self.speed_increment = speed_increment
        self.max_speed_level = 10
        
        self.direction_change_timer = 0
        self.direction_change_interval = 120
        
        self.vx = 0
        self.vy = 0
        
        self.current_speed = self.speed_per_level * self.speed_level
        self.target_vx = 0
        self.target_vy = 0
        self.smoothing_factor = 0.1

    def _random_position(self):
        margin = self.target_radius + 50
        x = random.randint(margin, self.screen_width - margin)
        y = random.randint(margin + 80, self.screen_height - margin)
        return x, y

    def increase_speed_level(self):
        if self.speed_level < self.max_speed_level:
            self.speed_level = min(self.speed_level + self.speed_increment, self.max_speed_level)
            self.current_speed = self.speed_per_level * self.speed_level

    def get_speed_level(self):
        return self.speed_level

    def spawn_target(self):
        x, y = self._random_position()
        self._set_random_direction()
        self.target_vx = self.vx
        self.target_vy = self.vy
        self.direction_change_timer = 0
        return x, y

    def _set_random_direction(self):
        angle = random.random() * math.pi * 2
        self.vx = math.cos(angle) * self.current_speed
        self.vy = math.sin(angle) * self.current_speed
        self.target_vx = self.vx
        self.target_vy = self.vy

    def _smooth_direction_change(self, target_angle):
        current_angle = math.atan2(self.target_vy, self.target_vx)
        self.target_vx = math.cos(target_angle) * self.current_speed
        self.target_vy = math.sin(target_angle) * self.current_speed

    def update_position(self, x, y):
        self.direction_change_timer += 1
        
        if self.direction_change_timer >= self.direction_change_interval:
            self.direction_change_timer = 0
            if random.random() < 0.3:
                self._set_random_direction()
            else:
                angle_adjust = random.uniform(-math.pi/6, math.pi/6)
                current_angle = math.atan2(self.target_vy, self.target_vx)
                new_angle = current_angle + angle_adjust
                self._smooth_direction_change(new_angle)
        
        self.vx += (self.target_vx - self.vx) * self.smoothing_factor
        self.vy += (self.target_vy - self.vy) * self.smoothing_factor
        
        new_x = x + self.vx
        new_y = y + self.vy
        
        margin = self.target_radius
        
        if new_x < margin or new_x > self.screen_width - margin:
            self.vx = -self.vx
            self.target_vx = -self.target_vx
            new_x = max(margin, min(self.screen_width - margin, new_x))
        
        if new_y < margin + 80 or new_y > self.screen_height - margin:
            self.vy = -self.vy
            self.target_vy = -self.target_vy
            new_y = max(margin + 80, min(self.screen_height - margin, new_y))
        
        return new_x, new_y

    def get_current_speed(self):
        return self.current_speed
