# core/sound_manager.py

import pygame

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        
    def load_sound(self, name, path):
        try:
            self.sounds[name] = pygame.mixer.Sound(path)
        except:
            print(f"No se pudo cargar: {path}")
    
    def play(self, name):
        if name in self.sounds:
            self.sounds[name].play()
