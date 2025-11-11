# dialogue_system.py - Sistema de diálogos en Shipibo-Conibo

import pygame
from settings import *

class DialogueBox:
    """Sistema de diálogos con pausa del juego"""
    def __init__(self, screen):
        self.screen = screen
        self.active = False
        self.shipibo_text = ""
        self.spanish_text = ""
        self.speaker_name = ""
        self.font_large = pygame.font.Font(None, 32)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 24)
        self.waiting_for_input = False
        
    def show(self, shipibo, spanish, speaker):
        """Muestra un diálogo y pausa el juego"""
        self.active = True
        self.shipibo_text = shipibo
        self.spanish_text = spanish
        self.speaker_name = speaker
        self.waiting_for_input = True
        
    def update(self, events):
        """Actualiza el diálogo y detecta input para continuar"""
        if not self.active:
            return False
            
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN or event.key == pygame.K_z:
                    self.active = False
                    self.waiting_for_input = False
                    return True  # Diálogo completado
        
        return False
    
    def draw(self):
        """Dibuja el diálogo en pantalla"""
        if not self.active:
            return
        
        # Overlay semi-transparente
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Caja principal para Shipibo-Conibo
        main_box_height = 120
        main_box_y = HEIGHT // 2 - 100
        pygame.draw.rect(self.screen, BLACK, (50, main_box_y, WIDTH - 100, main_box_height))
        pygame.draw.rect(self.screen, WHITE, (50, main_box_y, WIDTH - 100, main_box_height), 3)
        
        # Nombre del hablante
        name_surf = self.font_medium.render(self.speaker_name, True, GOLD)
        self.screen.blit(name_surf, (70, main_box_y + 10))
        
        # Texto en Shipibo-Conibo (burbuja principal)
        shipibo_surf = self.font_large.render(self.shipibo_text, True, WHITE)
        shipibo_rect = shipibo_surf.get_rect(center=(WIDTH // 2, main_box_y + 70))
        self.screen.blit(shipibo_surf, shipibo_rect)
        
        # Caja secundaria para traducción en español
        spanish_box_y = main_box_y + main_box_height + 20
        spanish_box_height = 80
        pygame.draw.rect(self.screen, (30, 30, 30), (50, spanish_box_y, WIDTH - 100, spanish_box_height))
        pygame.draw.rect(self.screen, CYAN, (50, spanish_box_y, WIDTH - 100, spanish_box_height), 2)
        
        # Etiqueta "Español:"
        label_surf = self.font_small.render("Español:", True, CYAN)
        self.screen.blit(label_surf, (70, spanish_box_y + 10))
        
        # Texto en español
        spanish_surf = self.font_medium.render(self.spanish_text, True, WHITE)
        spanish_rect = spanish_surf.get_rect(center=(WIDTH // 2, spanish_box_y + 50))
        self.screen.blit(spanish_surf, spanish_rect)
        
        # Indicador para continuar
        continue_surf = self.font_small.render("Presiona ESPACIO para continuar", True, YELLOW)
        continue_rect = continue_surf.get_rect(center=(WIDTH // 2, HEIGHT - 40))
        self.screen.blit(continue_surf, continue_rect)

# Diálogos predefinidos en Shipibo-Conibo
DIALOGUES = {
    "yacuruna": {
        "intro": {
            "shipibo": "Eara Yacuruna, yoyo noko jakon",
            "spanish": "Yo soy Yacuruna, guardián de las aguas"
        },
        "defeat": {
            "shipibo": "Ea yoshtai... Jaskaka metsa ikax",
            "spanish": "Me has vencido... Pero la selva es eterna"
        }
    },
    "chullachaqui": {
        "intro": {
            "shipibo": "Eara Chullachaqui, bake shipash jakon",
            "spanish": "Yo soy Chullachaqui, el que confunde los caminos"
        },
        "defeat": {
            "shipibo": "Ea yoshtai... Mesko jaskaitai",
            "spanish": "Me has vencido... Eres muy fuerte"
        }
    },
    "yacumama": {
        "intro": {
            "shipibo": "Eara Yacumama, yoyo rono mama",
            "spanish": "Yo soy Yacumama, la madre serpiente"
        },
        "revival": {
            "shipibo": "¡Ea jakonbaon betan kopi yoibaon!",
            "spanish": "¡Invocaré a mis hermanos caídos!"
        },
        "defeat": {
            "shipibo": "Joia... ea pakoti yoshtai bena...",
            "spanish": "Así que... esta es mi derrota verdadera..."
        }
    }
}

def get_dialogue(boss_name, moment):
    """Obtiene un diálogo específico"""
    boss_key = boss_name.lower()
    if boss_key in DIALOGUES and moment in DIALOGUES[boss_key]:
        dialogue = DIALOGUES[boss_key][moment]
        return dialogue["shipibo"], dialogue["spanish"]
    return "...", "..."