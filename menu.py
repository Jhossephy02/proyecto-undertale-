# menu.py - Sistema de menús

import pygame
from settings import *

class Button:
    def __init__(self, x, y, width, height, text, color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover = False
        
    def draw(self, screen, font):
        color = YELLOW if self.hover else self.color
        pygame.draw.rect(screen, color, self.rect, 2)
        
        text_surf = font.render(self.text, True, color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
    def check_hover(self, mouse_pos):
        self.hover = self.rect.collidepoint(mouse_pos)
        return self.hover
    
    def is_clicked(self, mouse_pos, mouse_pressed):
        return self.rect.collidepoint(mouse_pos) and mouse_pressed[0]

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        
        center_x = WIDTH // 2
        button_width = 300
        button_height = 60
        
        self.buttons = {
            "play": Button(center_x - button_width // 2, 250, button_width, button_height, "JUGAR"),
            "settings": Button(center_x - button_width // 2, 330, button_width, button_height, "CONFIGURACIÓN"),
            "quit": Button(center_x - button_width // 2, 410, button_width, button_height, "SALIR")
        }
        
    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        for button in self.buttons.values():
            button.check_hover(mouse_pos)
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.buttons["play"].is_clicked(mouse_pos, mouse_pressed):
                    return "play"
                elif self.buttons["settings"].is_clicked(mouse_pos, mouse_pressed):
                    return "settings"
                elif self.buttons["quit"].is_clicked(mouse_pos, mouse_pressed):
                    return "quit"
        
        return None
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Título
        title = self.font_large.render("BOSS FIGHT", True, RED)
        title_rect = title.get_rect(center=(WIDTH // 2, 120))
        self.screen.blit(title, title_rect)
        
        subtitle = self.font_small.render("Estilo Undertale", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, 180))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Botones
        for button in self.buttons.values():
            button.draw(self.screen, self.font_medium)

class SettingsMenu:
    def __init__(self, screen, config):
        self.screen = screen
        self.config = config
        self.font_large = pygame.font.Font(None, 56)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 28)
        
        center_x = WIDTH // 2
        button_width = 400
        button_height = 50
        y_start = 150
        y_spacing = 70
        
        self.buttons = {
            "difficulty": Button(center_x - button_width // 2, y_start, 
                               button_width, button_height, ""),
            "telegraph": Button(center_x - button_width // 2, y_start + y_spacing, 
                              button_width, button_height, ""),
            "sound": Button(center_x - button_width // 2, y_start + y_spacing * 2, 
                          button_width, button_height, ""),
            "music": Button(center_x - button_width // 2, y_start + y_spacing * 3, 
                          button_width, button_height, ""),
            "hitboxes": Button(center_x - button_width // 2, y_start + y_spacing * 4, 
                             button_width, button_height, ""),
            "back": Button(center_x - 150, HEIGHT - 100, 300, 50, "VOLVER")
        }
        
        self.update_button_texts()
        
    def update_button_texts(self):
        diff = self.config["difficulty"].upper()
        self.buttons["difficulty"].text = f"Dificultad: {diff}"
        
        telegraph = "SÍ" if self.config["telegraph_enabled"] else "NO"
        self.buttons["telegraph"].text = f"Advertencias: {telegraph}"
        
        sound = "SÍ" if self.config["sound_enabled"] else "NO"
        self.buttons["sound"].text = f"Sonidos: {sound}"
        
        music = "SÍ" if self.config["music_enabled"] else "NO"
        self.buttons["music"].text = f"Música: {music}"
        
        hitboxes = "SÍ" if self.config["show_hitboxes"] else "NO"
        self.buttons["hitboxes"].text = f"Mostrar Hitboxes: {hitboxes}"
    
    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        for button in self.buttons.values():
            button.check_hover(mouse_pos)
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.buttons["difficulty"].is_clicked(mouse_pos, mouse_pressed):
                    difficulties = ["easy", "normal", "hard"]
                    current = difficulties.index(self.config["difficulty"])
                    self.config["difficulty"] = difficulties[(current + 1) % 3]
                    self.update_button_texts()
                    
                elif self.buttons["telegraph"].is_clicked(mouse_pos, mouse_pressed):
                    self.config["telegraph_enabled"] = not self.config["telegraph_enabled"]
                    self.update_button_texts()
                    
                elif self.buttons["sound"].is_clicked(mouse_pos, mouse_pressed):
                    self.config["sound_enabled"] = not self.config["sound_enabled"]
                    self.update_button_texts()
                    
                elif self.buttons["music"].is_clicked(mouse_pos, mouse_pressed):
                    self.config["music_enabled"] = not self.config["music_enabled"]
                    self.update_button_texts()
                    
                elif self.buttons["hitboxes"].is_clicked(mouse_pos, mouse_pressed):
                    self.config["show_hitboxes"] = not self.config["show_hitboxes"]
                    self.update_button_texts()
                    
                elif self.buttons["back"].is_clicked(mouse_pos, mouse_pressed):
                    return "back"
        
        return None
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Título
        title = self.font_large.render("CONFIGURACIÓN", True, CYAN)
        title_rect = title.get_rect(center=(WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        # Botones
        for button in self.buttons.values():
            button.draw(self.screen, self.font_medium)
        
        # Información de dificultad
        y_pos = HEIGHT - 180
        diff_info = [
            "FÁCIL: Más vida, menos daño, ataques lentos",
            "NORMAL: Balanceado",
            "DIFÍCIL: Menos vida, más daño, ataques rápidos"
        ]
        
        for i, info in enumerate(diff_info):
            color = GREEN if i == 0 else (YELLOW if i == 1 else RED)
            if diff_info[i].split(":")[0].lower() == self.config["difficulty"]:
                text = self.font_small.render(info, True, color)
            else:
                text = self.font_small.render(info, True, (100, 100, 100))
            text_rect = text.get_rect(center=(WIDTH // 2, y_pos + i * 25))
            self.screen.blit(text, text_rect)   