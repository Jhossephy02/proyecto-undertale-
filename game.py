# game.py - Loop principal

import pygame
import sys
from settings import *
from player import Player
from boss import Boss
from ai_brain import AIBrain
from core.input_handler import InputHandler
from core.sound_manager import SoundManager

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("BOSS FIGHT - IA Adaptativa")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.input_handler = InputHandler()
        self.sound_manager = SoundManager()
        self.ai_brain = AIBrain()
        
        self.player = Player(ARENA_X + ARENA_WIDTH // 2, ARENA_Y + ARENA_HEIGHT // 2)
        self.boss = Boss(WIDTH // 2, 100, self.ai_brain)
        
        self.game_time = 0
        self.ai_analysis_timer = 0
        self.game_over = False
        self.victory = False
        
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.game_time += dt
            
            self.handle_events()
            if not self.game_over:
                self.update(dt)
            self.draw()
        
        pygame.quit()
        sys.exit()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.key == pygame.K_r and self.game_over:
                    self.__init__()
    
    def update(self, dt):
        self.input_handler.update()
        keys = self.input_handler.get_keys()
        
        self.player.update(dt, keys)
        self.boss.update(dt, self.player)
        
        self.ai_analysis_timer += dt
        if self.ai_analysis_timer >= AI_ANALYSIS_INTERVAL:
            self.ai_brain.analyze_player(self.player, self.game_time)
            self.ai_analysis_timer = 0
        
        if self.player.hp <= 0:
            self.game_over = True
            self.victory = False
        if self.boss.hp <= 0:
            self.game_over = True
            self.victory = True
    
    def draw(self):
        self.screen.fill(BLACK)
        
        pygame.draw.rect(self.screen, WHITE, 
                        (ARENA_X, ARENA_Y, ARENA_WIDTH, ARENA_HEIGHT), 3)
        
        self.player.draw(self.screen)
        self.boss.draw(self.screen)
        
        self.draw_ui()
        
        if self.game_over:
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_ui(self):
        font = pygame.font.Font(None, 36)
        
        hp_text = font.render(f"HP: {self.player.hp}/{self.player.max_hp}", True, RED)
        self.screen.blit(hp_text, (20, 20))
        
        boss_hp_text = font.render(f"BOSS: {self.boss.hp}/{self.boss.max_hp}", True, GREEN)
        self.screen.blit(boss_hp_text, (WIDTH - 250, 20))
        
        state_text = font.render(f"Estado: {self.boss.state.upper()}", True, YELLOW)
        self.screen.blit(state_text, (WIDTH // 2 - 100, 20))
    
    def draw_game_over(self):
        font = pygame.font.Font(None, 72)
        small_font = pygame.font.Font(None, 36)
        
        if self.victory:
            text = font.render("¡VICTORIA!", True, GREEN)
            msg = small_font.render("¡Le ganaste al boss! 🎉", True, WHITE)
        else:
            text = font.render("GAME OVER", True, RED)
            msg = small_font.render("El boss te quebró 💀", True, WHITE)
        
        restart = small_font.render("Presiona R para reiniciar", True, YELLOW)
        
        self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 100))
        self.screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2))
        self.screen.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT // 2 + 50))

if __name__ == "__main__":
    game = Game()
    game.run()
