# game.py - Loop principal con sistema de turnos

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
        pygame.display.set_caption("BOSS FIGHT - Sistema de Turnos Undertale")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.input_handler = InputHandler()
        self.sound_manager = SoundManager()
        self.ai_brain = AIBrain()
        
        # Sistema de fases
        self.game_phase = "ATTACK"  # ATTACK, DODGE, TRANSITION
        self.phase_timer = 0
        self.phase_duration = ATTACK_PHASE_DURATION
        
        # Sistema de bosses progresivos
        self.current_boss_index = 0
        self.total_time = 0
        self.speed_multiplier = 1.0
        
        # Crear jugador y primer boss
        self.player = Player(ARENA_X + ARENA_WIDTH // 2, ARENA_Y + ARENA_HEIGHT // 2)
        self.boss = self.create_boss(self.current_boss_index)
        
        self.game_time = 0
        self.ai_analysis_timer = 0
        self.game_over = False
        self.victory = False
        
        # Estadísticas
        self.stats = {
            "damage_dealt": 0,
            "damage_taken": 0,
            "accuracy": 0,
            "time": 0,
            "bosses_defeated": 0
        }
        
        # Mensaje de transición
        self.transition_message = ""
        self.show_phase_message = False
        self.phase_message_timer = 0
        
        # Sistema de score y ultimate
        self.score = 0
        self.ultimate_ready = False
        self.ultimate_cooldown = 0
        self.last_bullet_count = 0
        self.dodges_count = 0
    
    def create_boss(self, index):
        """Crea un boss según el índice"""
        if index >= len(BOSS_LIST):
            index = len(BOSS_LIST) - 1
        
        boss_config = BOSS_LIST[index]
        return Boss(WIDTH // 2, 100, self.ai_brain, boss_config)
    
    def calculate_speed_multiplier(self):
        """Calcula el multiplicador de velocidad basado en tiempo y bosses derrotados"""
        # Aumenta 10% cada 20 segundos + 20% por boss
        time_multiplier = 1.0 + (self.total_time // 20) * 0.10
        boss_multiplier = 1.0 + self.stats["bosses_defeated"] * 0.20
        return time_multiplier * boss_multiplier
    
    def next_boss(self):
        """Carga el siguiente boss"""
        self.current_boss_index += 1
        self.stats["bosses_defeated"] += 1
        
        if self.current_boss_index >= len(BOSS_LIST):
            # Victoria final
            self.game_over = True
            self.victory = True
            self.stats["time"] = self.total_time
            return
        
        # Crear nuevo boss
        self.boss = self.create_boss(self.current_boss_index)
        
        # Mostrar mensaje de introducción
        intro = BOSS_LIST[self.current_boss_index]["intro"]
        self.transition_message = intro
        self.game_phase = "TRANSITION"
        self.phase_timer = 0
        self.phase_duration = PHASE_TRANSITION_TIME
        
        # Curar un poco al jugador
        self.player.hp = min(self.player.hp + 30, self.player.max_hp)
        
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.game_time += dt
            self.total_time += dt
            
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
        
        # Calcular multiplicador de velocidad
        self.speed_multiplier = self.calculate_speed_multiplier()
        
        # Actualizar timer de mensajes de fase
        if self.phase_message_timer > 0:
            self.phase_message_timer -= dt
        
        # Actualizar cooldown de ultimate
        if self.ultimate_cooldown > 0:
            self.ultimate_cooldown -= dt
        
        # Sistema de fases
        self.phase_timer += dt
        
        if self.game_phase == "TRANSITION":
            # Fase de transición
            if self.phase_timer >= self.phase_duration:
                self.game_phase = "ATTACK"
                self.phase_timer = 0
                self.phase_duration = ATTACK_PHASE_DURATION
        
        elif self.game_phase == "ATTACK":
            # FASE DE ATAQUE: Jugador puede disparar, boss no ataca
            prev_boss_hp = self.boss.hp
            
            self.player.update(dt, keys, can_shoot=True)
            
            # Verificar colisiones de balas del jugador con el boss
            for bullet in self.player.bullets[:]:
                boss_rect = pygame.Rect(self.boss.x - 40, self.boss.y - 40, 80, 80)
                if bullet.get_rect().colliderect(boss_rect):
                    if self.boss.take_damage(bullet.damage):
                        # Boss derrotado
                        self.next_boss()
                    bullet.active = False
                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)
            
            damage_to_boss = prev_boss_hp - self.boss.hp
            if damage_to_boss > 0:
                self.stats["damage_dealt"] += damage_to_boss
            
            # Ultimate con X (si está lista y no en cooldown)
            if keys[pygame.K_x] and self.score >= 200 and self.ultimate_cooldown <= 0:
                self.activate_ultimate()
            
            # Cambiar a fase DODGE después de 3 segundos
            if self.phase_timer >= self.phase_duration:
                self.game_phase = "DODGE"
                self.phase_timer = 0
                self.phase_duration = DODGE_PHASE_DURATION
                self.player.clear_bullets()
                self.last_bullet_count = len(self.boss.bullets)
        
        elif self.game_phase == "DODGE":
            # FASE DE ESQUIVA: Boss ataca, jugador no puede disparar
            prev_player_hp = self.player.hp
            prev_bullet_count = len(self.boss.bullets)
            
            self.player.update(dt, keys, can_shoot=False)
            self.boss.update(dt, self.player, self.game_phase, self.speed_multiplier)
            
            # Sistema de score por esquiva
            current_bullet_count = len(self.boss.bullets)
            bullets_dodged = prev_bullet_count - current_bullet_count
            if bullets_dodged > 0 and prev_player_hp == self.player.hp:
                # Solo dar puntos si esquivó (no recibió daño)
                self.score += bullets_dodged * 2
                self.dodges_count += bullets_dodged
            
            damage_to_player = prev_player_hp - self.player.hp
            if damage_to_player > 0:
                self.stats["damage_taken"] += damage_to_player
            
            # Cambiar a fase ATTACK después de 7 segundos
            if self.phase_timer >= self.phase_duration:
                self.game_phase = "ATTACK"
                self.phase_timer = 0
                self.phase_duration = ATTACK_PHASE_DURATION
                self.boss.clear_bullets()
                
                # Analizar patrones del jugador para la IA
                self.ai_brain.analyze_movement_pattern(self.player, self.total_time)
        
        # Análisis de IA
        self.ai_analysis_timer += dt
        if self.ai_analysis_timer >= AI_ANALYSIS_INTERVAL:
            self.ai_brain.analyze_player(self.player, self.game_time)
            self.ai_analysis_timer = 0
        
        # Verificar game over
        if self.player.hp <= 0:
            self.game_over = True
            self.victory = False
            self.stats["time"] = self.total_time
            
            # Calcular precisión
            if self.player.shots_fired > 0:
                hits = int(self.stats["damage_dealt"] / PLAYER_BULLET_DAMAGE)
                self.stats["accuracy"] = (hits / self.player.shots_fired) * 100
    
    def activate_ultimate(self):
        """Activa la ultimate del jugador"""
        ultimate_damage = int(self.boss.max_hp * 0.5)
        self.boss.take_damage(ultimate_damage)
        self.score -= 200
        self.ultimate_cooldown = 5.0
        
        if self.boss.hp <= 0:
            self.next_boss()
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Arena
        arena_color = WHITE
        if self.game_phase == "ATTACK":
            arena_color = CYAN
        elif self.game_phase == "DODGE":
            arena_color = RED
        
        pygame.draw.rect(self.screen, arena_color, 
                        (ARENA_X, ARENA_Y, ARENA_WIDTH, ARENA_HEIGHT), 3)
        
        # Entidades
        self.player.draw(self.screen)
        self.boss.draw(self.screen, self.game_phase)
        
        # UI
        self.draw_ui()
        
        # Mensaje de transición
        if self.game_phase == "TRANSITION":
            self.draw_transition_message()
        
        # Game over
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
        
        # Score y Ultimate
        score_text = font.render(f"SCORE: {self.score}", True, YELLOW)
        self.screen.blit(score_text, (20, 80))
        
        # Indicador de Ultimate
        if self.score >= 200 and self.ultimate_cooldown <= 0:
            ult_text = font.render("ULTIMATE LISTA! (X)", True, PURPLE)
            self.screen.blit(ult_text, (20, 115))
            
            if int(self.total_time * 5) % 2 == 0:
                pygame.draw.rect(self.screen, PURPLE, (15, 110, 300, 35), 3)
        elif self.ultimate_cooldown > 0:
            cd_text = small_font.render(f"Ultimate: {int(self.ultimate_cooldown)}s", True, (150, 150, 150))
            self.screen.blit(cd_text, (20, 115))
        else:
            progress_text = small_font.render(f"Ultimate: {self.score}/200", True, (200, 200, 200))
            self.screen.blit(progress_text, (20, 115))
        
        # Timer de fase (esquina inferior izquierda)
        time_left = self.phase_duration - self.phase_timer
        phase_name = "ATAQUE" if self.game_phase == "ATTACK" else "ESQUIVA"
        phase_color = CYAN if self.game_phase == "ATTACK" else RED
        
        timer_bg = pygame.Rect(15, HEIGHT - 50, 120, 35)
        pygame.draw.rect(self.screen, BLACK, timer_bg)
        pygame.draw.rect(self.screen, phase_color, timer_bg, 2)
        
        timer_text = small_font.render(f"{phase_name}: {int(time_left)}s", True, phase_color)
        self.screen.blit(timer_text, (20, HEIGHT - 45))
        
        # Velocidad del juego
        speed_text = small_font.render(f"Velocidad: {self.speed_multiplier:.1f}x", True, ORANGE)
        self.screen.blit(speed_text, (WIDTH - 160, HEIGHT - 30))
        
        # Bosses derrotados
        bosses_text = small_font.render(f"Bosses: {self.stats['bosses_defeated']}", True, YELLOW)
        self.screen.blit(bosses_text, (WIDTH - 140, 20))
    
    def draw_transition_message(self):
        """Dibuja mensaje de transición entre bosses"""
        font = pygame.font.Font(None, 48)
        text = font.render(self.transition_message, True, YELLOW)
        
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(text, text_rect)
    
    def draw_game_over(self):
        """Dibuja la pantalla de game over con estadísticas"""
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        font = pygame.font.Font(None, 72)
        medium_font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 28)
        
        y_offset = HEIGHT // 2 - 200
        
        # Título
        if self.victory:
            title = font.render("¡VICTORIA TOTAL!", True, GREEN)
            subtitle = medium_font.render("¡Derrotaste a todos los bosses! 🎉", True, WHITE)
        else:
            title = font.render("GAME OVER", True, RED)
            subtitle = medium_font.render("El boss te derrotó 💀", True, WHITE)
        
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, y_offset))
        self.screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, y_offset + 80))
        
        # Estadísticas
        y_offset += 150
        stats_title = medium_font.render("ESTADÍSTICAS:", True, YELLOW)
        self.screen.blit(stats_title, (WIDTH // 2 - stats_title.get_width() // 2, y_offset))
        
        y_offset += 50
        stats_texts = [
            f"Tiempo total: {int(self.stats['time'])} segundos",
            f"Score final: {self.score}",
            f"Bosses derrotados: {self.stats['bosses_defeated']}",
            f"Balas esquivadas: {self.dodges_count}",
            f"Daño infligido: {int(self.stats['damage_dealt'])}",
            f"Daño recibido: {int(self.stats['damage_taken'])}",
            f"Velocidad final: {self.speed_multiplier:.1f}x"
        ]
        
        if self.victory and self.player.shots_fired > 0:
            hits = int(self.stats["damage_dealt"] / PLAYER_BULLET_DAMAGE)
            accuracy = (hits / self.player.shots_fired) * 100
            stats_texts.append(f"Precisión: {int(accuracy)}%")
        
        for text in stats_texts:
            stat_surf = small_font.render(text, True, WHITE)
            self.screen.blit(stat_surf, (WIDTH // 2 - stat_surf.get_width() // 2, y_offset))
            y_offset += 35
        
        # Reinicio
        restart = medium_font.render("Presiona R para reiniciar", True, CYAN)
        self.screen.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT - 80))

if __name__ == "__main__":
    game = Game()
    game.run()