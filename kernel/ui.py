import pygame
import sys
import math
import random

class Button:
    def __init__(self, x, y, width, height, text, font, color=(100, 100, 100), hover_color=(150, 150, 150), text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False

    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 3, border_radius=10)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos, mouse_click):
        return self.rect.collidepoint(mouse_pos) and mouse_click


class Target:
    def __init__(self, x, y, radius=30):
        self.x = x
        self.y = y
        self.radius = radius
        self.is_hit = False
        self.particles = []
        self.alpha = 255
        self.animating = False

    def draw(self, screen):
        if not self.animating:
            pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.radius * 0.7)
            pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(self.y)), self.radius * 0.4)
            pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.radius * 0.15)
        else:
            for particle in self.particles:
                particle["alpha"] = max(0, particle["alpha"] - 5)
                if particle["alpha"] > 0:
                    s = pygame.Surface((particle["size"], particle["size"]), pygame.SRCALPHA)
                    pygame.draw.circle(s, (*particle["color"], particle["alpha"]), 
                                      (particle["size"]//2, particle["size"]//2), particle["size"]//2)
                    screen.blit(s, (int(particle["x"]), int(particle["y"])))
                    particle["x"] += particle["vx"]
                    particle["y"] += particle["vy"]
                    particle["vy"] += 0.3

    def hit(self):
        self.is_hit = True
        self.animating = True
        self.particles = []
        for _ in range(15):
            angle = random.random() * math.pi * 2
            speed = random.randint(3, 8)
            self.particles.append({
                "x": self.x,
                "y": self.y,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed - 2,
                "size": random.randint(6, 12),
                "color": (255, random.randint(0, 100), random.randint(0, 50)),
                "alpha": 255
            })

    def is_animation_done(self):
        if not self.animating:
            return False
        return all(p["alpha"] <= 0 for p in self.particles)

    def collidepoint(self, pos):
        dx = pos[0] - self.x
        dy = pos[1] - self.y
        return dx * dx + dy * dy <= self.radius * self.radius


class UI:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.bg_color = (0, 0, 0)
        
        self.chinese_font = None
        self.small_font = None
        self.large_font = None
        self._init_fonts()
        
        self.pause_button_rect = pygame.Rect(self.width - 60, 20, 40, 40)
        
        self.initial_speed_plus_rect = None
        self.initial_speed_minus_rect = None
        self.speed_increment_plus_rect = None
        self.speed_increment_minus_rect = None

    def _init_fonts(self):
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        ]
        
        for path in font_paths:
            try:
                self.chinese_font = pygame.font.Font(path, 36)
                self.small_font = pygame.font.Font(path, 24)
                self.large_font = pygame.font.Font(path, 48)
                test_surface = self.chinese_font.render("测试中文", True, (255, 255, 255))
                if test_surface:
                    break
            except:
                continue
        
        if self.chinese_font is None:
            self.chinese_font = pygame.font.SysFont("simhei, microsoftyahei, arial", 36)
            self.small_font = pygame.font.SysFont("simhei, microsoftyahei, arial", 24)
            self.large_font = pygame.font.SysFont("simhei, microsoftyahei, arial", 48)

    def draw_start_screen(self, start_button, settings_button=None):
        self.screen.fill(self.bg_color)
        
        title = self.large_font.render("射击靶子游戏", True, (255, 100, 100))
        title_rect = title.get_rect(center=(self.width // 2, 100))
        self.screen.blit(title, title_rect)
        
        instructions = [
            "游戏说明：",
            "1. 点击鼠标射击移动的靶子",
            "2. 游戏限时30秒",
            "3. 越到后面靶子移动越快",
            "4. 击中越多分数越高！"
        ]
        
        left_margin = title_rect.left
        instructions_start_y = 150
        for i, line in enumerate(instructions):
            text = self.small_font.render(line, True, (200, 200, 200))
            self.screen.blit(text, (left_margin, instructions_start_y + i * 40))
        
        start_button.draw(self.screen)
        if settings_button:
            settings_button.draw(self.screen)

    def draw_game_screen(self, target, score, time_left, crosshair_pos, speed_level=0):
        self.screen.fill(self.bg_color)
        
        score_text = self.small_font.render(f"击中: {score}", True, (255, 255, 255))
        self.screen.blit(score_text, (20, 20))
        
        time_text = self.small_font.render(f"时间: {time_left:.1f}秒", True, (255, 255, 255))
        self.screen.blit(time_text, (20, 60))
        
        self._draw_pause_button()
        
        if target:
            target.draw(self.screen)
        
        self._draw_crosshair(crosshair_pos)

    def _draw_pause_button(self):
        pygame.draw.rect(self.screen, (100, 100, 100), self.pause_button_rect, border_radius=5)
        pygame.draw.rect(self.screen, (200, 200, 200), self.pause_button_rect, 2, border_radius=5)
        
        pause_x = self.pause_button_rect.centerx
        pause_y = self.pause_button_rect.centery
        pygame.draw.line(self.screen, (255, 255, 255), (pause_x - 8, pause_y - 10), (pause_x - 8, pause_y + 10), 3)
        pygame.draw.line(self.screen, (255, 255, 255), (pause_x + 8, pause_y - 10), (pause_x + 8, pause_y + 10), 3)

    def is_pause_button_clicked(self, mouse_pos, mouse_click):
        return self.pause_button_rect.collidepoint(mouse_pos) and mouse_click

    def draw_pause_screen(self):
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.large_font.render("游戏暂停", True, (255, 100, 100))
        pause_rect = pause_text.get_rect(center=(self.width // 2, self.height // 2 - 50))
        self.screen.blit(pause_text, pause_rect)
        
        resume_text = self.small_font.render("点击屏幕继续游戏", True, (200, 200, 200))
        resume_rect = resume_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
        self.screen.blit(resume_text, resume_rect)

    def _draw_crosshair(self, pos):
        x = int(pos[0])
        y = int(pos[1])
        size = 15
        color = (255, 0, 0)
        gap = 4
        line_width = 2
        
        crosshair_size = (size + 1) * 2
        crosshair_surface = pygame.Surface((crosshair_size, crosshair_size), pygame.SRCALPHA)
        center = crosshair_size // 2
        
        pygame.draw.line(crosshair_surface, color, (center - size, center), (center - gap, center), line_width)
        pygame.draw.line(crosshair_surface, color, (center + gap, center), (center + size, center), line_width)
        pygame.draw.line(crosshair_surface, color, (center, center - size), (center, center - gap), line_width)
        pygame.draw.line(crosshair_surface, color, (center, center + gap), (center, center + size), line_width)
        
        outer_radius = 8
        inner_radius = 2
        
        pygame.draw.circle(crosshair_surface, color, (center, center), outer_radius, line_width)
        pygame.draw.circle(crosshair_surface, color, (center, center), inner_radius, 0)
        
        self.screen.blit(crosshair_surface, (x - center, y - center))

    def draw_settings_screen(self, initial_speed, speed_increment, back_button):
        self.screen.fill(self.bg_color)
        
        title = self.large_font.render("游戏设置", True, (255, 100, 100))
        title_rect = title.get_rect(center=(self.width // 2, 80))
        self.screen.blit(title, title_rect)
        
        item_y_start = 180
        item_spacing = 100
        
        self._draw_setting_item("初始靶子移动速度", initial_speed, 1, 10, item_y_start)
        self._draw_setting_item("靶子每次提速", speed_increment, 1, 10, item_y_start + item_spacing)
        
        back_button.draw(self.screen)

    def _draw_setting_item(self, label_text, value, min_val, max_val, y):
        label = self.small_font.render(label_text, True, (255, 255, 255))
        label_rect = label.get_rect(midleft=(100, y))
        self.screen.blit(label, label_rect)
        
        button_size = 40
        button_spacing = 15
        value_spacing = 30
        
        plus_x = self.width - 100 - button_size
        minus_x = plus_x - button_spacing - button_size
        value_x = minus_x - value_spacing
        button_y = y - button_size // 2
        
        value_text = self.chinese_font.render(str(value), True, (255, 255, 255))
        value_rect = value_text.get_rect(midright=(value_x, y))
        self.screen.blit(value_text, value_rect)
        
        minus_rect = pygame.Rect(minus_x, button_y, button_size, button_size)
        plus_rect = pygame.Rect(plus_x, button_y, button_size, button_size)
        
        if label_text == "初始靶子移动速度":
            self.initial_speed_minus_rect = minus_rect
            self.initial_speed_plus_rect = plus_rect
        elif label_text == "靶子每次提速":
            self.speed_increment_minus_rect = minus_rect
            self.speed_increment_plus_rect = plus_rect
        
        pygame.draw.rect(self.screen, (50, 100, 180), minus_rect, border_radius=5)
        pygame.draw.rect(self.screen, (200, 200, 200), minus_rect, 2, border_radius=5)
        
        minus_center_x = minus_rect.centerx
        minus_center_y = minus_rect.centery
        pygame.draw.line(self.screen, (255, 255, 255), 
                        (minus_center_x - 10, minus_center_y), 
                        (minus_center_x + 10, minus_center_y), 3)
        
        pygame.draw.rect(self.screen, (50, 100, 180), plus_rect, border_radius=5)
        pygame.draw.rect(self.screen, (200, 200, 200), plus_rect, 2, border_radius=5)
        
        plus_center_x = plus_rect.centerx
        plus_center_y = plus_rect.centery
        pygame.draw.line(self.screen, (255, 255, 255), 
                        (plus_center_x - 10, plus_center_y), 
                        (plus_center_x + 10, plus_center_y), 3)
        pygame.draw.line(self.screen, (255, 255, 255), 
                        (plus_center_x, plus_center_y - 10), 
                        (plus_center_x, plus_center_y + 10), 3)
        
        if value <= min_val:
            overlay = pygame.Surface((button_size, button_size))
            overlay.set_alpha(100)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (minus_x, button_y))
        
        if value >= max_val:
            overlay = pygame.Surface((button_size, button_size))
            overlay.set_alpha(100)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (plus_x, button_y))

    def handle_settings_input(self, mouse_pos, mouse_click, initial_speed, speed_increment):
        if not mouse_click:
            return None
        
        if self.initial_speed_minus_rect and self.initial_speed_minus_rect.collidepoint(mouse_pos):
            if initial_speed > 1:
                return {'type': 'set_initial_speed', 'value': initial_speed - 1}
        
        if self.initial_speed_plus_rect and self.initial_speed_plus_rect.collidepoint(mouse_pos):
            if initial_speed < 10:
                return {'type': 'set_initial_speed', 'value': initial_speed + 1}
        
        if self.speed_increment_minus_rect and self.speed_increment_minus_rect.collidepoint(mouse_pos):
            if speed_increment > 1:
                return {'type': 'set_speed_increment', 'value': speed_increment - 1}
        
        if self.speed_increment_plus_rect and self.speed_increment_plus_rect.collidepoint(mouse_pos):
            if speed_increment < 10:
                return {'type': 'set_speed_increment', 'value': speed_increment + 1}
        
        return None

    def draw_game_over_screen(self, score, restart_button, settings_button=None):
        self.screen.fill(self.bg_color)
        
        game_over = self.large_font.render("游戏结束", True, (255, 100, 100))
        game_over_rect = game_over.get_rect(center=(self.width // 2, 150))
        self.screen.blit(game_over, game_over_rect)
        
        score_text = self.large_font.render(f"击中靶子数: {score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(self.width // 2, 250))
        self.screen.blit(score_text, score_rect)
        
        restart_button.draw(self.screen)
        if settings_button:
            settings_button.draw(self.screen)
