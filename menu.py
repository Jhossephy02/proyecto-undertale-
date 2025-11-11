# menu.py - Sistema de menús con intro

import pygame
import math
from settings import *

class IntroScreen:
    """Pantalla de intro con transición"""
    def __init__(self, screen):
        self.screen = screen
        self.timer = 0
        self.duration = 3.0  # 3 segundos de intro
        self.finished = False
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        
    def update(self, dt):
        self.timer += dt
        if self.timer >= self.duration:
            self.finished = True
    
    def skip(self):
        """Saltar intro"""
        self.finished = True
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Efecto de fade
        alpha = 255
        if self.timer < 1.0:
            alpha = int(255 * (self.timer / 1.0))
        elif self.timer > self.duration - 1.0:
            alpha = int(255 * ((self.duration - self.timer) / 1.0))
        
        # Título con alpha
        surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        title = self.font_large.render("LEYENDAS DE LA SELVA", True, GOLD)
        title.set_alpha(alpha)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        self.screen.blit(title, title_rect)
        
        subtitle = self.font_medium.render("Boss Fight", True, CYAN)
        subtitle.set_alpha(alpha)
        subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Indicador para saltar
        if self.timer > 0.5:
            skip_font = pygame.font.Font(None, 24)
            skip_text = skip_font.render("Presiona cualquier tecla para continuar", True, WHITE)
            skip_text.set_alpha(int(128 + 127 * math.sin(self.timer * 5)))
            skip_rect = skip_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
            self.screen.blit(skip_text, skip_rect)

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
            "practica": Button(center_x - button_width // 2, 220, 
                              button_width, button_height, "PRÁCTICA", GREEN),
            "normal": Button(center_x - button_width // 2, 300, 
                            button_width, button_height, "NORMAL", YELLOW),
            "genocida": Button(center_x - button_width // 2, 380, 
                              button_width, button_height, "GENOCIDA", RED),
            "settings": Button(center_x - button_width // 2, 460, 
                             button_width, button_height, "CONFIGURACIÓN", CYAN),
            "quit": Button(center_x - button_width // 2, 540, 
                          button_width, button_height, "SALIR", WHITE)
        }
        
    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        for button in self.buttons.values():
            button.check_hover(mouse_pos)
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.buttons["practica"].is_clicked(mouse_pos, mouse_pressed):
                    return "practica"
                elif self.buttons["normal"].is_clicked(mouse_pos, mouse_pressed):
                    return "normal"
                elif self.buttons["genocida"].is_clicked(mouse_pos, mouse_pressed):
                    return "genocida"
                elif self.buttons["settings"].is_clicked(mouse_pos, mouse_pressed):
                    return "settings"
                elif self.buttons["quit"].is_clicked(mouse_pos, mouse_pressed):
                    return "quit"
        
        return None
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Título
        title = self.font_large.render("BOSS FIGHT", True, RED)
        title_rect = title.get_rect(center=(WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        subtitle = self.font_small.render("Leyendas de la Selva", True, GOLD)
        subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, 160))
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
        y_start = 200
        y_spacing = 80
        
        self.buttons = {
            "telegraph": Button(center_x - button_width // 2, y_start, 
                              button_width, button_height, ""),
            "sound": Button(center_x - button_width // 2, y_start + y_spacing, 
                          button_width, button_height, ""),
            "music": Button(center_x - button_width // 2, y_start + y_spacing * 2, 
                          button_width, button_height, ""),
            "back": Button(center_x - 150, HEIGHT - 100, 300, 50, "VOLVER")
        }
        
        self.update_button_texts()
        
    def update_button_texts(self):
        telegraph = "SÍ" if self.config["telegraph_enabled"] else "NO"
        self.buttons["telegraph"].text = f"Advertencias: {telegraph}"
        
        sound = "SÍ" if self.config["sound_enabled"] else "NO"
        self.buttons["sound"].text = f"Sonidos: {sound}"
        
        music = "SÍ" if self.config["music_enabled"] else "NO"
        self.buttons["music"].text = f"Música: {music}"
    
    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        for button in self.buttons.values():
            button.check_hover(mouse_pos)
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.buttons["telegraph"].is_clicked(mouse_pos, mouse_pressed):
                    self.config["telegraph_enabled"] = not self.config["telegraph_enabled"]
                    self.update_button_texts()
                    
                elif self.buttons["sound"].is_clicked(mouse_pos, mouse_pressed):
                    self.config["sound_enabled"] = not self.config["sound_enabled"]
                    self.update_button_texts()
                    
                elif self.buttons["music"].is_clicked(mouse_pos, mouse_pressed):
                    self.config["music_enabled"] = not self.config["music_enabled"]
                    self.update_button_texts()
                    
                elif self.buttons["back"].is_clicked(mouse_pos, mouse_pressed):
                    return "back"
        
        return None
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Título
        title = self.font_large.render("CONFIGURACIÓN", True, CYAN)
        title_rect = title.get_rect(center=(WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Botones
        for button in self.buttons.values():
            button.draw(self.screen, self.font_medium)