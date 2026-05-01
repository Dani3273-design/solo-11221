import pygame
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kernel.ui import UI, Button, Target
from kernel.control import GameControl
from kernel.move import Movement

class GameState:
    START = 0
    PLAYING = 1
    GAME_OVER = 2

class ShootingGame:
    def __init__(self):
        pygame.init()
        
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600
        self.GAME_DURATION = 30.0
        
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("射击靶子游戏")
        
        self.clock = pygame.time.Clock()
        self.FPS = 60
        
        self.ui = UI(self.screen, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.control = GameControl(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.movement = None
        
        self.state = GameState.START
        self.score = 0
        self.time_left = self.GAME_DURATION
        self.start_time = 0
        
        self.target = None
        self.waiting_for_new_target = False
        
        self._create_buttons()
        
        self.running = True

    def _create_buttons(self):
        button_width = 200
        button_height = 60
        center_x = (self.SCREEN_WIDTH - button_width) // 2
        
        self.start_button = Button(
            center_x, 400,
            button_width, button_height,
            "开始游戏",
            self.ui.chinese_font,
            color=(50, 150, 50),
            hover_color=(80, 180, 80)
        )
        
        self.restart_button = Button(
            center_x, 350,
            button_width, button_height,
            "再来一局",
            self.ui.chinese_font,
            color=(50, 100, 180),
            hover_color=(80, 130, 210)
        )

    def _start_game(self):
        self.state = GameState.PLAYING
        self.score = 0
        self.time_left = self.GAME_DURATION
        self.start_time = time.time()
        self.movement = Movement(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        
        x, y = self.movement.spawn_target()
        self.target = Target(x, y)
        self.waiting_for_new_target = False
        
        self.control.set_cursor(False)

    def _game_over(self):
        self.state = GameState.GAME_OVER
        self.control.set_cursor(True)

    def _spawn_new_target(self):
        x, y = self.movement.spawn_target()
        self.target = Target(x, y)
        self.waiting_for_new_target = False

    def _update_game_logic(self):
        if self.state != GameState.PLAYING:
            return
        
        current_time = time.time()
        elapsed = current_time - self.start_time
        self.time_left = max(0, self.GAME_DURATION - elapsed)
        
        if self.time_left <= 0:
            self._game_over()
            return
        
        if self.target and not self.target.animating and self.movement:
            new_x, new_y = self.movement.update_position(self.target.x, self.target.y)
            self.target.x = new_x
            self.target.y = new_y
        
        if self.waiting_for_new_target and self.target and self.target.is_animation_done():
            self._spawn_new_target()

    def _handle_shoot(self):
        if self.state != GameState.PLAYING:
            return
        
        mouse_pos = self.control.get_mouse_pos()
        
        if self.target and not self.target.animating:
            if self.target.collidepoint(mouse_pos):
                self.score += 1
                self.target.hit()
                self.waiting_for_new_target = True
                if self.movement:
                    self.movement.increase_speed_level()

    def run(self):
        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            
            if not self.control.handle_events():
                self.running = False
                break
            
            if self.state == GameState.START:
                self.start_button.check_hover(mouse_pos)
                
                if self.control.is_mouse_clicked():
                    if self.start_button.is_clicked(mouse_pos, True):
                        self._start_game()
                
                self.ui.draw_start_screen(self.start_button)
            
            elif self.state == GameState.PLAYING:
                self._update_game_logic()
                
                if self.control.is_mouse_clicked():
                    self._handle_shoot()
                
                self.ui.draw_game_screen(
                    self.target,
                    self.score,
                    self.time_left,
                    mouse_pos
                )
            
            elif self.state == GameState.GAME_OVER:
                self.restart_button.check_hover(mouse_pos)
                
                if self.control.is_mouse_clicked():
                    if self.restart_button.is_clicked(mouse_pos, True):
                        self._start_game()
                
                self.ui.draw_game_over_screen(self.score, self.restart_button)
            
            pygame.display.flip()
            self.clock.tick(self.FPS)
        
        pygame.quit()
        sys.exit()


def main():
    game = ShootingGame()
    game.run()


if __name__ == "__main__":
    main()
