# core/input_handler.py

import pygame

class InputHandler:
    def __init__(self):
        self.keys = pygame.key.get_pressed()
        
    def update(self):
        self.keys = pygame.key.get_pressed()
        
    def get_keys(self):
        return self.keys
