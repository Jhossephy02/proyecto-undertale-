# game.py - Loop principal del juego

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
        pygame.display.set_caption("BOSS FIGHT - IA Adaptativa Undertale Style")
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
        
        # Estadísticas de la partida
        self.stats = {
            "damage_dealt": 0,
            "damage_taken": 0,
            "accuracy": 0,
            "time": 0
        }
        
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
        
        # Guardar HP anterior para calcular daño
        prev_boss_hp = self.boss.hp
        prev_player_hp = self.player.hp
        
        # Actualizar jugador y boss
        self.player.update(dt, keys)
        self.boss.update(dt, self.player)
        
        # Calcular estadísticas
        damage_to_boss = prev_boss_hp - self.boss.hp
        damage_to_player = prev_player_hp - self.player.hp
        if damage_to_boss > 0:
            self.stats["damage_dealt"] += damage_to_boss
        if damage_to_player > 0:
            self.stats["damage_taken"] += damage_to_player
        
        # Análisis de IA periódico
        self.ai_analysis_timer += dt
        if self.ai_analysis_timer >= AI_ANALYSIS_INTERVAL:
            self.ai_brain.analyze_player(self.player, self.game_time)
            self.ai_analysis_timer = 0
        
        # Verificar condiciones de game over
        if self.player.hp <= 0:
            self.game_over = True
            self.victory = False
            self.stats["time"] = self.game_time
        elif self.boss.hp <= 0:
            self.game_over = True
            self.victory = True
            self.stats["time"] = self.game_time
            # Calcular precisión
            if self.player.shots_fired > 0:
                hits = int(self.stats["damage_dealt"] / PLAYER_BULLET_DAMAGE)
                self.stats["accuracy"] = (hits / self.player.shots_fired) * 100
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Dibujar arena
        pygame.draw.rect(self.screen, WHITE, 
                        (ARENA_X, ARENA_Y, ARENA_WIDTH, ARENA_HEIGHT), 3)
        
        # Dibujar entidades
        self.player.draw(self.screen)
        self.boss.draw(self.screen)
        
        # UI
        self.draw_ui()
        
        # Pantalla de game over
        if self.game_over:
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_ui(self):
        """Dibuja la interfaz de usuario"""
        font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 24)
        
        # HP del jugador
        hp_text = font.render(f"HP: {self.player.hp}/{self.player.max_hp}", True, RED)
        self.screen.blit(hp_text, (20, 20))
        
        # Barra de HP del jugador
        bar_width = 150
        bar_height = 15
        bar_x = 20
        bar_y = 55
        
        pygame.draw.rect(self.screen, WHITE, (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4), 2)
        pygame.draw.rect(self.screen, BLACK, (bar_x, bar_y, bar_width, bar_height))
        
        hp_percent = self.player.hp / self.player.max_hp
        hp_bar_width = int(bar_width * hp_percent)
        hp_color = GREEN if hp_percent > 0.5 else (YELLOW if hp_percent > 0.25 else RED)
        pygame.draw.rect(self.screen, hp_color, (bar_x, bar_y, hp_bar_width, bar_height))
        
        # Estado del boss (arriba a la derecha)
        state_text = font.render(f"Boss: {self.boss.state.upper()}", True, 
                                BOSS_STATES[self.boss.state]["color"])
        self.screen.blit(state_text, (WIDTH - 250, 20))
        
        # Tiempo de juego
        time_text = small_font.render(f"Tiempo: {int(self.game_time)}s", True, WHITE)
        self.screen.blit(time_text, (WIDTH // 2 - 50, HEIGHT - 30))
        
        # Instrucciones
        if self.game_time < 5:
            controls_text = small_font.render("WASD/Flechas: Mover | Z/Espacio: Disparar", 
                                             True, YELLOW)
            self.screen.blit(controls_text, 
                           (WIDTH // 2 - controls_text.get_width() // 2, HEIGHT - 60))
    
    def draw_game_over(self):
        """Dibuja la pantalla de game over con estadísticas"""
        # Overlay semi-transparente
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        font = pygame.font.Font(None, 72)
        medium_font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 28)
        
        y_offset = HEIGHT // 2 - 150
        
        # Título
        if self.victory:
            title = font.render("¡VICTORIA!", True, GREEN)
            subtitle = medium_font.render("¡Le ganaste al boss! 🎉", True, WHITE)
        else:
            title = font.render("GAME OVER", True, RED)
            subtitle = medium_font.render("El boss te quebró 💀", True, WHITE)
        
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, y_offset))
        self.screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, y_offset + 80))
        
        # Estadísticas
        y_offset += 150
        stats_title = medium_font.render("ESTADÍSTICAS:", True, YELLOW)
        self.screen.blit(stats_title, (WIDTH // 2 - stats_title.get_width() // 2, y_offset))
        
        y_offset += 50
        stats_texts = [
            f"Tiempo: {int(self.stats['time'])} segundos",
            f"Daño infligido: {int(self.stats['damage_dealt'])}",
            f"Daño recibido: {int(self.stats['damage_taken'])}",
            f"Disparos: {self.player.shots_fired}",
            f"Precisión: {int(self.stats.get('accuracy', 0))}%" if self.victory else ""
        ]
        
        for text in stats_texts:
            if text:
                stat_surf = small_font.render(text, True, WHITE)
                self.screen.blit(stat_surf, (WIDTH // 2 - stat_surf.get_width() // 2, y_offset))
                y_offset += 35
        
        # Instrucción de reinicio
        restart = medium_font.render("Presiona R para reiniciar", True, CYAN)
        self.screen.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT - 80))

if __name__ == "__main__":
    game = Game()
    game.run()