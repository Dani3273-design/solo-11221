import pygame
import threading
import os

class SoundManager:
    def __init__(self):
        self.shoot_sound = None
        self._init_sound()

    def _init_sound(self):
        try:
            pygame.mixer.init()
            self._generate_shoot_sound()
        except Exception as e:
            print(f"音效初始化失败: {e}")
            self.shoot_sound = None

    def _generate_shoot_sound(self):
        try:
            import array
            import math
            import random
            
            sample_rate = 22050
            duration = 0.15
            
            num_samples = int(sample_rate * duration)
            buffer = array.array('h', [0] * num_samples)
            
            decay_start = int(num_samples * 0.3)
            
            for i in range(num_samples):
                t = i / sample_rate
                noise = random.randint(-32768, 32767)
                envelope = 1.0
                
                if i > decay_start:
                    envelope = 1.0 - (i - decay_start) / (num_samples - decay_start)
                    envelope = max(0, envelope)
                
                freq_mod = 800 + 400 * math.sin(2 * math.pi * 50 * t)
                value = int(noise * envelope * 0.6)
                value = max(-32767, min(32767, value))
                buffer[i] = value
            
            sound = pygame.mixer.Sound(buffer=buffer)
            sound.set_volume(0.8)
            self.shoot_sound = sound
        except Exception as e:
            print(f"生成音效失败: {e}")
            self.shoot_sound = None

    def play_shoot(self):
        def play():
            if self.shoot_sound:
                try:
                    self.shoot_sound.play()
                except:
                    pass
        
        thread = threading.Thread(target=play)
        thread.daemon = True
        thread.start()


class GameControl:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.mouse_pos = (screen_width // 2, screen_height // 2)
        self.mouse_clicked = False
        self.sound_manager = SoundManager()

    def handle_events(self):
        self.mouse_clicked = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.mouse_clicked = True
                    self.sound_manager.play_shoot()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        
        return True

    def get_mouse_pos(self):
        return self.mouse_pos

    def is_mouse_clicked(self):
        return self.mouse_clicked

    def set_cursor(self, visible=False):
        pygame.mouse.set_visible(visible)
