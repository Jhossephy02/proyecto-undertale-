<<<<<<< HEAD
# game.py - Loop principal con sistema de turnos
=======
# game.py - Loop principal con sistema de 3 fases
>>>>>>> 2b5238c2a1999933b19cc3548f5f28c867526c49

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
<<<<<<< HEAD
        pygame.display.set_caption("BOSS FIGHT - Sistema de Turnos Undertale")
=======
        pygame.display.set_caption("BOSS FIGHT - Sistema de 3 Fases")
>>>>>>> 2b5238c2a1999933b19cc3548f5f28c867526c49
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.input_handler = InputHandler()
        self.sound_manager = SoundManager()
        self.ai_brain = AIBrain()
        
<<<<<<< HEAD
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
=======
        # Jugador
        self.player = Player(ARENA_X + ARENA_WIDTH // 2, ARENA_Y + ARENA_HEIGHT // 2)
>>>>>>> 2b5238c2a1999933b19cc3548f5f28c867526c49
        
        # Sistema de bosses
        self.current_phase = 1
        self.boss = Boss(WIDTH // 2, 100, self.ai_brain, phase=self.current_phase)
        self.revived_bosses = []  # Bosses revividos en fase 3
        
        # Timers y estados
        self.game_time = 0
        self.ai_analysis_timer = 0
        self.game_over = False
        self.victory = False
        self.phase_transition = False
        self.transition_timer = 0
        self.transition_duration = 3.0
        
        # Estadísticas
        self.stats = {
            "damage_dealt": 0,
            "damage_taken": 0,
            "accuracy": 0,
            "time": 0,
<<<<<<< HEAD
            "bosses_defeated": 0
=======
            "phases_completed": 0,
            "special_attacks_used": 0
>>>>>>> 2b5238c2a1999933b19cc3548f5f28c867526c49
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
        self.score_timer = 0  # Para score gradual
    
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
                if not self.phase_transition:
                    self.update(dt)
                else:
                    self.update_transition(dt)
            
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
        
<<<<<<< HEAD
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
=======
        # Guardar HP para estadísticas
        prev_boss_hp = self.boss.hp
        prev_player_hp = self.player.hp
        
        # Actualizar jugador
        self.player.update(dt, keys)
        
        # Actualizar boss principal
        self.boss.update(dt, self.player)
        
        # Actualizar bosses revividos (fase 3)
        for revived_boss in self.revived_bosses[:]:
            revived_boss.update(dt, self.player)
            if revived_boss.hp <= 0:
                self.revived_bosses.remove(revived_boss)
                print(f"Boss Fase {revived_boss.phase} eliminado")
        
        # Estadísticas
        damage_to_boss = prev_boss_hp - self.boss.hp
        damage_to_player = prev_player_hp - self.player.hp
        if damage_to_boss > 0:
            self.stats["damage_dealt"] += damage_to_boss
        if damage_to_player > 0:
            self.stats["damage_taken"] += damage_to_player
        
        # Análisis IA
>>>>>>> 2b5238c2a1999933b19cc3548f5f28c867526c49
        self.ai_analysis_timer += dt
        if self.ai_analysis_timer >= AI_ANALYSIS_INTERVAL:
            self.ai_brain.analyze_player(self.player, self.game_time)
            self.ai_analysis_timer = 0
        
<<<<<<< HEAD
        # Verificar game over
        if self.player.hp <= 0:
            self.game_over = True
            self.victory = False
            self.stats["time"] = self.total_time
            
            # Calcular precisión
            if self.player.shots_fired > 0:
                hits = int(self.stats["damage_dealt"] / PLAYER_BULLET_DAMAGE)
                self.stats["accuracy"] = (hits / self.player.shots_fired) * 100
=======
        # Resurrección de bosses (solo fase 3)
        if self.current_phase == 3 and self.boss.hp < self.boss.max_hp * 0.5:
            new_bosses = self.boss.revive_previous_bosses()
            self.revived_bosses.extend(new_bosses)
        
        # Verificar derrota del boss
        if self.boss.hp <= 0:
            if self.current_phase < 3:
                self.start_phase_transition()
            else:
                # Victoria final
                self.game_over = True
                self.victory = True
                self.stats["time"] = self.game_time
                self.stats["phases_completed"] = 3
                if self.player.shots_fired > 0:
                    hits = int(self.stats["damage_dealt"] / PLAYER_BULLET_DAMAGE)
                    self.stats["accuracy"] = (hits / self.player.shots_fired) * 100
        
        # Verificar derrota del jugador
        if self.player.hp <= 0:
            self.game_over = True
            self.victory = False
            self.stats["time"] = self.game_time
            self.stats["phases_completed"] = self.current_phase - 1
    
    def start_phase_transition(self):
        """Inicia la transición a la siguiente fase"""
        self.phase_transition = True
        self.transition_timer = 0
        self.stats["phases_completed"] = self.current_phase
        print(f"¡Fase {self.current_phase} completada! Preparando Fase {self.current_phase + 1}...")
    
    def update_transition(self, dt):
        """Actualiza la transición entre fases"""
        self.transition_timer += dt
        
        if self.transition_timer >= self.transition_duration:
            self.advance_to_next_phase()
    
    def advance_to_next_phase(self):
        """Avanza a la siguiente fase"""
        self.current_phase += 1
        self.phase_transition = False
        self.transition_timer = 0
        
        # Crear nuevo boss
        self.boss = Boss(WIDTH // 2, 100, self.ai_brain, phase=self.current_phase)
        
        # Resetear jugador para la nueva fase
        self.player.reset_for_new_phase()
        
        # Limpiar bosses revividos
        self.revived_bosses.clear()
        
        print(f"¡FASE {self.current_phase} INICIADA!")
>>>>>>> 2b5238c2a1999933b19cc3548f5f28c867526c49
    
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
<<<<<<< HEAD
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
=======
        pygame.draw.rect(self.screen, WHITE, 
                        (ARENA_X, ARENA_Y, ARENA_WIDTH, ARENA_HEIGHT), 3)
        
        if not self.phase_transition:
            # Dibujar entidades
            self.player.draw(self.screen)
            self.boss.draw(self.screen)
            
            # Dibujar bosses revividos
            for revived_boss in self.revived_bosses:
                revived_boss.draw(self.screen)
            
            # UI
            self.draw_ui()
        else:
            # Pantalla de transición
            self.draw_phase_transition()
        
        # Game Over
>>>>>>> 2b5238c2a1999933b19cc3548f5f28c867526c49
        if self.game_over:
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_ui(self):
        """Dibuja la interfaz"""
        font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 24)
        
        # HP del jugador
        hp_text = font.render(f"HP: {self.player.hp}/{self.player.max_hp}", True, RED)
        self.screen.blit(hp_text, (20, 20))
        
        # Barra HP jugador
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
        
<<<<<<< HEAD
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
        
=======
        # Estado del boss
        phase_color = BOSS_PHASES[self.current_phase]["color"]
        phase_text = font.render(f"FASE {self.current_phase} - {self.boss.state.upper()}", 
                                True, phase_color)
        self.screen.blit(phase_text, (WIDTH - 350, 20))
        
        # Contador de esquivos y modo ataque
        dodges_text = small_font.render(f"Esquivos: {self.player.dodges_for_special}/{SPECIAL_ATTACK_DODGES}", 
                                       True, CYAN if not self.player.attack_mode else GOLD)
        self.screen.blit(dodges_text, (20, 80))
        
        # Indicador de modo ataque
        if self.player.attack_mode:
            time_left = SPECIAL_ATTACK_WINDOW - self.player.attack_mode_timer
            mode_text = font.render(f"¡MODO ATAQUE! {int(time_left)}s", True, GOLD)
            self.screen.blit(mode_text, (WIDTH // 2 - 150, HEIGHT - 50))
            
            if self.player.can_use_special:
                special_text = small_font.render("Presiona X para PODER ESPECIAL", True, GOLD)
                self.screen.blit(special_text, (WIDTH // 2 - 150, HEIGHT - 80))
        
        # Tiempo
        time_text = small_font.render(f"Tiempo: {int(self.game_time)}s", True, WHITE)
        self.screen.blit(time_text, (WIDTH // 2 - 50, HEIGHT - 30))
        
        # Instrucciones (primeros segundos)
        if self.game_time < 5:
            controls = small_font.render("WASD: Mover | Z: Disparar (modo ataque) | X: Especial", 
                                       True, YELLOW)
            self.screen.blit(controls, (WIDTH // 2 - 270, HEIGHT - 110))
        
        # Contador de bosses revividos
        if len(self.revived_bosses) > 0:
            revived_text = small_font.render(f"Bosses revividos: {len(self.revived_bosses)}", 
                                           True, PURPLE)
            self.screen.blit(revived_text, (WIDTH - 200, 60))
    
    def draw_phase_transition(self):
        """Dibuja la pantalla de transición entre fases"""
>>>>>>> 2b5238c2a1999933b19cc3548f5f28c867526c49
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
<<<<<<< HEAD
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(text, text_rect)
    
    def draw_game_over(self):
        """Dibuja la pantalla de game over con estadísticas"""
=======
        font = pygame.font.Font(None, 72)
        small_font = pygame.font.Font(None, 36)
        
        # Fase completada
        completed_text = font.render(f"FASE {self.current_phase} COMPLETADA", True, GREEN)
        self.screen.blit(completed_text, 
                        (WIDTH // 2 - completed_text.get_width() // 2, HEIGHT // 2 - 100))
        
        # Siguiente fase
        next_phase = self.current_phase + 1
        next_text = font.render(f"PREPARANDO FASE {next_phase}...", True, 
                              BOSS_PHASES[next_phase]["color"])
        self.screen.blit(next_text, 
                        (WIDTH // 2 - next_text.get_width() // 2, HEIGHT // 2))
        
        # Advertencia
        if next_phase == 2:
            warning = small_font.render("¡Mayor velocidad y daño!", True, YELLOW)
        else:
            warning = small_font.render("¡El boss puede revivir a los anteriores!", True, RED)
        
        self.screen.blit(warning, 
                        (WIDTH // 2 - warning.get_width() // 2, HEIGHT // 2 + 80))
        
        # Timer
        time_left = self.transition_duration - self.transition_timer
        timer_text = small_font.render(f"Comenzando en: {int(time_left) + 1}", True, WHITE)
        self.screen.blit(timer_text, 
                        (WIDTH // 2 - timer_text.get_width() // 2, HEIGHT // 2 + 130))
    
    def draw_game_over(self):
        """Dibuja pantalla de game over"""
>>>>>>> 2b5238c2a1999933b19cc3548f5f28c867526c49
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
<<<<<<< HEAD
            title = font.render("¡VICTORIA TOTAL!", True, GREEN)
            subtitle = medium_font.render("¡Derrotaste a todos los bosses! 🎉", True, WHITE)
        else:
            title = font.render("GAME OVER", True, RED)
            subtitle = medium_font.render("El boss te derrotó 💀", True, WHITE)
=======
            title = font.render("¡VICTORIA ÉPICA!", True, GOLD)
            subtitle = medium_font.render("¡Derrotaste a los 3 bosses! 🎉👑", True, WHITE)
        else:
            title = font.render("GAME OVER", True, RED)
            subtitle = medium_font.render(f"Llegaste a la Fase {self.current_phase} 💀", True, WHITE)
>>>>>>> 2b5238c2a1999933b19cc3548f5f28c867526c49
        
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, y_offset))
        self.screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, y_offset + 80))
        
        # Estadísticas
        y_offset += 150
        stats_title = medium_font.render("ESTADÍSTICAS:", True, YELLOW)
        self.screen.blit(stats_title, (WIDTH // 2 - stats_title.get_width() // 2, y_offset))
        
        y_offset += 50
        stats_texts = [
<<<<<<< HEAD
            f"Tiempo total: {int(self.stats['time'])} segundos",
            f"Score final: {self.score}",
            f"Bosses derrotados: {self.stats['bosses_defeated']}",
            f"Balas esquivadas: {self.dodges_count}",
            f"Daño infligido: {int(self.stats['damage_dealt'])}",
            f"Daño recibido: {int(self.stats['damage_taken'])}",
            f"Velocidad final: {self.speed_multiplier:.1f}x"
=======
            f"Tiempo: {int(self.stats['time'])} segundos",
            f"Fases completadas: {self.stats['phases_completed']}/3",
            f"Daño infligido: {int(self.stats['damage_dealt'])}",
            f"Daño recibido: {int(self.stats['damage_taken'])}",
            f"Disparos: {self.player.shots_fired}",
            f"Esquivos totales: {self.player.total_dodges}",
            f"Precisión: {int(self.stats.get('accuracy', 0))}%" if self.victory else ""
>>>>>>> 2b5238c2a1999933b19cc3548f5f28c867526c49
        ]
        
        if self.victory and self.player.shots_fired > 0:
            hits = int(self.stats["damage_dealt"] / PLAYER_BULLET_DAMAGE)
            accuracy = (hits / self.player.shots_fired) * 100
            stats_texts.append(f"Precisión: {int(accuracy)}%")
        
<<<<<<< HEAD
        for text in stats_texts:
            stat_surf = small_font.render(text, True, WHITE)
            self.screen.blit(stat_surf, (WIDTH // 2 - stat_surf.get_width() // 2, y_offset))
            y_offset += 35
=======
        # Ranking
        if self.victory:
            y_offset += 20
            rank = "S" if self.stats['time'] < 180 else ("A" if self.stats['time'] < 300 else "B")
            rank_text = font.render(f"RANGO: {rank}", True, GOLD if rank == "S" else (YELLOW if rank == "A" else GREEN))
            self.screen.blit(rank_text, (WIDTH // 2 - rank_text.get_width() // 2, y_offset))
>>>>>>> 2b5238c2a1999933b19cc3548f5f28c867526c49
        
        # Reinicio
        restart = medium_font.render("Presiona R para reiniciar", True, CYAN)
        self.screen.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT - 60))

if __name__ == "__main__":
    game = Game()
    game.run()