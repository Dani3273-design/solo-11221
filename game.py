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
    SETTINGS = 3
    PAUSED = 4

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
        self.pause_time = 0
        self.total_paused_time = 0
        
        self.target = None
        self.waiting_for_new_target = False
        
        self.initial_speed_level = 3
        self.speed_increment = 2
        
        self._create_buttons()
        
        self.running = True

    def _create_buttons(self):
        button_width = 200
        button_height = 60
        center_x = (self.SCREEN_WIDTH - button_width) // 2
        
        self.start_button = Button(
            center_x, 380,
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
        
        self.settings_button_start = Button(
            center_x, 460,
            button_width, button_height,
            "设置",
            self.ui.chinese_font,
            color=(100, 100, 100),
            hover_color=(150, 150, 150)
        )
        
        self.settings_button_gameover = Button(
            center_x, 430,
            button_width, button_height,
            "设置",
            self.ui.chinese_font,
            color=(100, 100, 100),
            hover_color=(150, 150, 150)
        )
        
        self.back_button = Button(
            center_x, 480,
            button_width, button_height,
            "返回",
            self.ui.chinese_font,
            color=(180, 50, 50),
            hover_color=(210, 80, 80)
        )

    def _start_game(self):
        self.state = GameState.PLAYING
        self.score = 0
        self.time_left = self.GAME_DURATION
        self.start_time = time.time()
        self.total_paused_time = 0
        self.movement = Movement(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, initial_speed_level=self.initial_speed_level, speed_increment=self.speed_increment)
        
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
        elapsed = current_time - self.start_time - self.total_paused_time
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

    def _pause_game(self):
        self.state = GameState.PAUSED
        self.pause_time = time.time()
        self.control.set_cursor(True)

    def _resume_game(self):
        self.state = GameState.PLAYING
        if self.pause_time > 0:
            self.total_paused_time += time.time() - self.pause_time
            self.pause_time = 0
        self.control.set_cursor(False)

    def _open_settings(self, from_state):
        self.previous_state = from_state
        self.state = GameState.SETTINGS
        self.control.set_cursor(True)

    def _close_settings(self):
        self.state = self.previous_state
        if self.previous_state != GameState.PAUSED:
            self.control.set_cursor(True)

    def run(self):
        self.previous_state = GameState.START
        
        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            
            if not self.control.handle_events():
                self.running = False
                break
            
            if self.state == GameState.START:
                self.start_button.check_hover(mouse_pos)
                self.settings_button_start.check_hover(mouse_pos)
                
                if self.control.is_mouse_clicked():
                    if self.start_button.is_clicked(mouse_pos, True):
                        self._start_game()
                    elif self.settings_button_start.is_clicked(mouse_pos, True):
                        self._open_settings(GameState.START)
                
                self.ui.draw_start_screen(self.start_button, self.settings_button_start)
            
            elif self.state == GameState.PLAYING:
                self._update_game_logic()
                
                pause_button_clicked = self.ui.is_pause_button_clicked(mouse_pos, self.control.is_mouse_clicked())
                if pause_button_clicked:
                    self._pause_game()
                elif self.control.is_mouse_clicked():
                    self._handle_shoot()
                
                self.ui.draw_game_screen(
                    self.target,
                    self.score,
                    self.time_left,
                    mouse_pos,
                    self.movement.get_speed_level() if self.movement else 0
                )
            
            elif self.state == GameState.PAUSED:
                if self.control.is_mouse_clicked():
                    self._resume_game()
                
                self.ui.draw_pause_screen()
            
            elif self.state == GameState.GAME_OVER:
                self.restart_button.check_hover(mouse_pos)
                self.settings_button_gameover.check_hover(mouse_pos)
                
                if self.control.is_mouse_clicked():
                    if self.restart_button.is_clicked(mouse_pos, True):
                        self._start_game()
                    elif self.settings_button_gameover.is_clicked(mouse_pos, True):
                        self._open_settings(GameState.GAME_OVER)
                
                self.ui.draw_game_over_screen(self.score, self.restart_button, self.settings_button_gameover)
            
            elif self.state == GameState.SETTINGS:
                self.back_button.check_hover(mouse_pos)
                
                action = self.ui.handle_settings_input(
                    mouse_pos,
                    self.control.is_mouse_clicked(),
                    self.initial_speed_level,
                    self.speed_increment
                )
                
                if action:
                    if action['type'] == 'set_initial_speed':
                        self.initial_speed_level = action['value']
                    elif action['type'] == 'set_speed_increment':
                        self.speed_increment = action['value']
                    elif action['type'] == 'back':
                        self._close_settings()
                
                if self.control.is_mouse_clicked() and self.back_button.is_clicked(mouse_pos, True):
                    self._close_settings()
                
                self.ui.draw_settings_screen(
                    self.initial_speed_level,
                    self.speed_increment,
                    self.back_button
                )
            
            pygame.display.flip()
            self.clock.tick(self.FPS)
        
        pygame.quit()
        sys.exit()


def main():
    game = ShootingGame()
    game.run()


if __name__ == "__main__":
    main()
