# game.py - Loop principal con sistema de 3 fases

import pygame
import sys
# Importar todas las constantes y configuraciones básicas
from settings import * # Importar componentes principales
from player import Player
from boss import Boss
from ai_brain import AIBrain
from core.input_handler import InputHandler
from core.sound_manager import SoundManager
# Importar componentes de UI/Menú (asumiendo que menu.py está disponible)
from menu import MainMenu, SettingsMenu 


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("BOSS FIGHT - Sistema de 3 Fases")
        self.clock = pygame.time.Clock()
        
        # --- NUEVOS ESTADOS DE JUEGO ---
        self.current_state = "MENU" # Estado inicial: Menú
        self.running = True
        self.config = GAME_CONFIG.copy() # Copia la configuración global
        
        # Inicializar Menús
        self.main_menu = MainMenu(self.screen)
        self.settings_menu = SettingsMenu(self.screen, self.config)
        
        # Componentes del juego (inicializados en start_game)
        self.player = None
        self.boss = None
        self.input_handler = None
        self.sound_manager = None
        self.ai_brain = None
        
        # Música
        pygame.mixer.music.load("assets/sounds/soundtrack_undertale.mp3")
        pygame.mixer.music.set_volume(0.1)
        if self.config["music_enabled"]:
            pygame.mixer.music.play(-1)

    def start_game(self):
        """Inicializa todos los componentes del juego después de la selección de menú."""
        self.current_state = "GAME"
        
        # Los imports de Player, Boss, etc., ya están arriba
        self.input_handler = InputHandler()
        self.sound_manager = SoundManager()
        self.ai_brain = AIBrain()
        
        # Aplicar Modificadores de Dificultad
        mod = DIFFICULTY_MODIFIERS[self.config["difficulty"]]
        
        # Jugador (aplicar modificador de HP)
        base_hp = int(PLAYER_HP * mod["player_hp_mult"])
        self.player = Player(ARENA_X + ARENA_WIDTH // 2, ARENA_Y + ARENA_HEIGHT // 2)
        self.player.max_hp = base_hp
        self.player.hp = base_hp
        
        # Boss (pasar modificador)
        self.current_phase = 1
        # **NOTA: El boss debe aceptar 'difficulty_mod' en su __init__**
        self.boss = Boss(WIDTH // 2, 100, self.ai_brain, phase=self.current_phase, difficulty_mod=mod) 
        self.revived_bosses = []
        
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
            "phases_completed": 0,
            "special_attacks_used": 0
        }
        
        # Mensaje de transición
        self.transition_message = ""
        self.show_phase_message = False
        self.phase_message_timer = 0
    
    # game.py - REEMPLAZAR Game.run

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            events = pygame.event.get()
            self.handle_common_events(events) # Manejo de salida (QUIT, ESC)
            
            if self.current_state == "MENU":
                action = self.main_menu.handle_events(events)
                if action == "play":
                    self.start_game()
                elif action == "settings":
                    self.current_state = "SETTINGS"
                elif action == "quit":
                    self.running = False
                self.main_menu.draw()
            
            elif self.current_state == "SETTINGS":
                action = self.settings_menu.handle_events(events)
                if action == "back":
                    self.current_state = "MENU"
                # Actualiza la configuración de música/sonido en tiempo real
                if self.config["music_enabled"] and not pygame.mixer.music.get_busy():
                    pygame.mixer.music.play(-1)
                elif not self.config["music_enabled"] and pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()

                self.settings_menu.draw()
            
            elif self.current_state == "GAME":
                self.game_time += dt
                self.handle_events_game(events)
            
                if not self.game_over:
                    if not self.phase_transition:
                        self.update(dt)
                    else:
                        self.update_transition(dt)
                
                self.draw()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

    def handle_common_events(self, events):
        """Maneja eventos que cierran el juego o regresan al menú."""
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                # La tecla ESC regresa al menú desde el juego/configuración
                if event.key == pygame.K_ESCAPE and self.current_state != "MENU":
                    self.current_state = "MENU"
    
    def handle_events_game(self, events):
        """Maneja los eventos específicos cuando el juego está corriendo."""
        self.input_handler.update()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    # Reiniciar (volver a la configuración original)
                    self.__init__()
                    
    def update(self, dt):
        # El input_handler ya se actualizó en handle_events_game, solo tomamos las keys.
        keys = self.input_handler.get_keys()
        
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

        # --- COMBINACIÓN DE ATAQUES (NUEVO CÓDIGO) ---
        # El boss principal asume las balas de los revividos
        for revived_boss in self.revived_bosses:
            self.boss.bullets.extend(revived_boss.bullets)
            revived_boss.bullets.clear()
        # ---------------------------------------------
        
        # Estadísticas
        damage_to_boss = prev_boss_hp - self.boss.hp
        damage_to_player = prev_player_hp - self.player.hp
        if damage_to_boss > 0:
            self.stats["damage_dealt"] += damage_to_boss
        if damage_to_player > 0:
            self.stats["damage_taken"] += damage_to_player
        
        # Análisis IA
        self.ai_analysis_timer += dt
        if self.ai_analysis_timer >= AI_ANALYSIS_INTERVAL:
            self.ai_brain.analyze_player(self.player, self.game_time)
            self.ai_analysis_timer = 0
        
        # Resurrección de bosses (solo fase 3)
        if self.current_phase == 3 and self.boss.hp < self.boss.max_hp * 0.5:
            new_bosses = self.boss.revive_previous_bosses()
            self.revived_bosses.extend(new_bosses)
        
        # Verificar derrota del boss
        if self.boss.hp <= 0:
            if self.current_phase < 3:

                if self.current_phase == 1:
                    boss_death_sound = pygame.mixer.Sound("assets/sounds/roar_boss_1.mp3")
                elif self.current_phase == 2:
                    boss_death_sound = pygame.mixer.Sound("assets/sounds/roar_muerte_chullachaqui.mp3")

                boss_death_sound.play()
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
                    boss_death_sound = pygame.mixer.Sound("assets/sounds/roar_muerte_yakumama.mp3")
                    boss_death_sound.play()
        
        # Verificar derrota del jugador
        if self.player.hp <= 0:
            self.game_over = True
            self.victory = False
            self.stats["time"] = self.game_time
            self.stats["phases_completed"] = self.current_phase - 1

            player_death_sound = pygame.mixer.Sound("assets/sounds/derrota.mp3")
            player_death_sound.play()
    
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
        
        # Obtener modificadores de la dificultad seleccionada (NUEVO CÓDIGO)
        mod = DIFFICULTY_MODIFIERS[self.config["difficulty"]]

        # Crear nuevo boss (pasar el modificador de dificultad)
        self.boss = Boss(WIDTH // 2, 100, self.ai_brain, phase=self.current_phase, difficulty_mod=mod)
        boss_appear_sound = pygame.mixer.Sound("assets/sounds/roar_inicio_yakuruna.mp3")
        boss_appear_sound.play()
        
        # Resetear jugador para la nueva fase
        self.player.reset_for_new_phase()
        
        # Limpiar bosses revividos
        self.revived_bosses.clear()
        
        print(f"¡FASE {self.current_phase} INICIADA!")
    
    # ... (Resto de los métodos draw, draw_ui, draw_phase_transition, draw_game_over) ...
    # ... (Estos métodos de dibujo no necesitan cambios funcionales para este requerimiento)
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Arena
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
        if self.game_over:
            self.draw_game_over()
        
        # pygame.display.flip() se movió al final de Game.run
    
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
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
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
            title = font.render("¡VICTORIA ÉPICA!", True, GOLD)
            subtitle = medium_font.render("¡Derrotaste a los 3 bosses! 🎉👑", True, WHITE)
        else:
            title = font.render("GAME OVER", True, RED)
            subtitle = medium_font.render(f"Llegaste a la Fase {self.current_phase} 💀", True, WHITE)
        
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, y_offset))
        self.screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, y_offset + 80))
        
        # Estadísticas
        y_offset += 150
        stats_title = medium_font.render("ESTADÍSTICAS:", True, YELLOW)
        self.screen.blit(stats_title, (WIDTH // 2 - stats_title.get_width() // 2, y_offset))
        
        y_offset += 50
        stats_texts = [
            f"Tiempo: {int(self.stats['time'])} segundos",
            f"Fases completadas: {self.stats['phases_completed']}/3",
            f"Daño infligido: {int(self.stats['damage_dealt'])}",
            f"Daño recibido: {int(self.stats['damage_taken'])}",
            f"Disparos: {self.player.shots_fired}",
            f"Esquivos totales: {self.player.total_dodges}",
            f"Precisión: {int(self.stats.get('accuracy', 0))}%" if self.victory else ""
        ]
        
        for text in stats_texts:
            if text:
                stat_surf = small_font.render(text, True, WHITE)
                self.screen.blit(stat_surf, (WIDTH // 2 - stat_surf.get_width() // 2, y_offset))
                y_offset += 35
        
        # Ranking
        if self.victory:
            y_offset += 20
            rank = "S" if self.stats['time'] < 180 else ("A" if self.stats['time'] < 300 else "B")
            rank_text = font.render(f"RANGO: {rank}", True, GOLD if rank == "S" else (YELLOW if rank == "A" else GREEN))
            self.screen.blit(rank_text, (WIDTH // 2 - rank_text.get_width() // 2, y_offset))
        
        # Reinicio
        restart = medium_font.render("Presiona R para reiniciar", True, CYAN)
        self.screen.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT - 60))

if __name__ == "__main__":
    game = Game()
    game.run()