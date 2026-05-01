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
        self._init_fonts()

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

    def draw_start_screen(self, start_button):
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
        
        for i, line in enumerate(instructions):
            text = self.small_font.render(line, True, (200, 200, 200))
            text_rect = text.get_rect(center=(self.width // 2, 200 + i * 40))
            self.screen.blit(text, text_rect)
        
        start_button.draw(self.screen)

    def draw_game_screen(self, target, score, time_left, crosshair_pos):
        self.screen.fill(self.bg_color)
        
        score_text = self.small_font.render(f"击中: {score}", True, (255, 255, 255))
        self.screen.blit(score_text, (20, 20))
        
        time_text = self.small_font.render(f"时间: {time_left:.1f}秒", True, (255, 255, 255))
        self.screen.blit(time_text, (20, 60))
        
        if target:
            target.draw(self.screen)
        
        self._draw_crosshair(crosshair_pos)

    def _draw_crosshair(self, pos):
        x, y = pos
        size = 15
        color = (255, 0, 0)
        
        pygame.draw.line(self.screen, color, (x - size, y), (x + size, y), 2)
        pygame.draw.line(self.screen, color, (x, y - size), (x, y + size), 2)
        pygame.draw.circle(self.screen, color, (x, y), 8, 2)
        pygame.draw.circle(self.screen, color, (x, y), 2)

    def draw_game_over_screen(self, score, restart_button):
        self.screen.fill(self.bg_color)
        
        game_over = self.large_font.render("游戏结束", True, (255, 100, 100))
        game_over_rect = game_over.get_rect(center=(self.width // 2, 150))
        self.screen.blit(game_over, game_over_rect)
        
        score_text = self.large_font.render(f"击中靶子数: {score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(self.width // 2, 250))
        self.screen.blit(score_text, score_rect)
        
        restart_button.draw(self.screen)
