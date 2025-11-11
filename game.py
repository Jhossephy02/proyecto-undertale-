# game.py - Loop principal con intro, menú de modos y 3 bosses

import pygame
import sys
from settings import *
from player import Player
from boss import Boss
from ai_brain import AIBrain
from core.input_handler import InputHandler
from core.sound_manager import SoundManager
from menu import MainMenu, SettingsMenu, IntroScreen


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("BOSS FIGHT - Leyendas de la Selva")
        self.clock = pygame.time.Clock()
        
        # Estados de juego
        self.current_state = "INTRO"  # Comienza con intro
        self.running = True
        self.config = GAME_CONFIG.copy()
        
        # Inicializar pantallas
        self.intro_screen = IntroScreen(self.screen)
        self.main_menu = MainMenu(self.screen)
        self.settings_menu = SettingsMenu(self.screen, self.config)
        
        # Componentes del juego
        self.player = None
        self.boss = None
        self.input_handler = None
        self.sound_manager = None
        self.ai_brain = None
        
        # Música
        try:
            pygame.mixer.music.load("assets/sounds/soundtrack_undertale.mp3")
            pygame.mixer.music.set_volume(0.1)
            if self.config["music_enabled"]:
                pygame.mixer.music.play(-1)
        except:
            print("No se pudo cargar la música de fondo")

    def start_game(self, game_mode):
        """Inicializa el juego con el modo seleccionado"""
        try:
            self.current_state = "GAME"
            self.config["game_mode"] = game_mode
            
            self.input_handler = InputHandler()
            self.sound_manager = SoundManager()
            self.ai_brain = AIBrain()
            
            # Aplicar modificadores del modo
            mod = GAME_MODE_MODIFIERS[game_mode]
            
            # Jugador
            base_hp = int(PLAYER_HP * mod["player_hp_mult"])
            self.player = Player(ARENA_X + ARENA_WIDTH // 2, ARENA_Y + ARENA_HEIGHT // 2)
            self.player.max_hp = base_hp
            self.player.hp = base_hp
            
            # Boss (Fase 1: Yacuruna)
            self.current_phase = 1
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
            
            self.transition_message = ""
            self.show_phase_message = False
            self.phase_message_timer = 0
            
            print(f"✓ Juego iniciado en modo: {game_mode.upper()}")
        except Exception as e:
            print(f"Error iniciando el juego: {e}")
            self.current_state = "MENU"
    
    def run(self):
        while self.running:
            try:
                dt = self.clock.tick(FPS) / 1000.0
                
                events = pygame.event.get()
                self.handle_common_events(events)
                
                if self.current_state == "INTRO":
                    self.intro_screen.update(dt)
                    self.intro_screen.draw()
                    
                    # Saltar intro con cualquier tecla
                    for event in events:
                        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                            self.intro_screen.skip()
                    
                    # Terminar intro
                    if self.intro_screen.finished:
                        self.current_state = "MENU"
                
                elif self.current_state == "MENU":
                    action = self.main_menu.handle_events(events)
                    if action == "practica":
                        self.start_game("practica")
                    elif action == "normal":
                        self.start_game("normal")
                    elif action == "genocida":
                        self.start_game("genocida")
                    elif action == "settings":
                        self.current_state = "SETTINGS"
                    elif action == "quit":
                        self.running = False
                    self.main_menu.draw()
                
                elif self.current_state == "SETTINGS":
                    action = self.settings_menu.handle_events(events)
                    if action == "back":
                        self.current_state = "MENU"
                    
                    # Actualizar música
                    if self.config["music_enabled"] and not pygame.mixer.music.get_busy():
                        try:
                            pygame.mixer.music.play(-1)
                        except:
                            pass
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
            
            except Exception as e:
                print(f"Error en el loop principal: {e}")
                import traceback
                traceback.print_exc()
                self.running = False
        
        pygame.quit()
        sys.exit()

    def handle_common_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.current_state == "GAME":
                        # Pausa o regreso al menú
                        self.current_state = "MENU"
                    elif self.current_state == "SETTINGS":
                        self.current_state = "MENU"
    
    def handle_events_game(self, events):
        if self.input_handler:
            self.input_handler.update()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    self.__init__()
                    
    def update(self, dt):
        if not self.input_handler or not self.player or not self.boss:
            return
            
        keys = self.input_handler.get_keys()
        
        prev_boss_hp = self.boss.hp
        prev_player_hp = self.player.hp
        
        # Actualizar jugador
        self.player.update(dt, keys)
        
        # Actualizar boss principal
        self.boss.update(dt, self.player)
        
        # Actualizar bosses revividos
        for revived_boss in self.revived_bosses[:]:
            revived_boss.update(dt, self.player)
            if revived_boss.hp <= 0:
                self.revived_bosses.remove(revived_boss)
                print(f"{revived_boss.name} eliminado")

        # Combinar balas de bosses revividos
        for revived_boss in self.revived_bosses:
            self.boss.bullets.extend(revived_boss.bullets)
            revived_boss.bullets.clear()
        
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
            self.ai_brain.analyze_movement_pattern(self.player, self.game_time)
            self.ai_analysis_timer = 0
        
        # Resurrección (solo Yacumama al 25% HP)
        if self.current_phase == 3 and self.boss.hp < self.boss.max_hp * 0.25:
            new_bosses = self.boss.revive_previous_bosses()
            if new_bosses:
                self.revived_bosses.extend(new_bosses)
                # Sonidos de resurrección
                if self.config["sound_enabled"]:
                    try:
                        revival_sound = pygame.mixer.Sound("assets/sounds/trueno.mp3")
                        revival_sound.play()
                    except:
                        pass
        
        # Verificar derrota del boss
        if self.boss.hp <= 0:
            if self.current_phase < 3:
                # Sonido de muerte del boss
                if self.config["sound_enabled"]:
                    try:
                        if self.current_phase == 1:
                            death_sound = pygame.mixer.Sound("assets/sounds/roar_boss_1.mp3")
                        elif self.current_phase == 2:
                            death_sound = pygame.mixer.Sound("assets/sounds/roar_muerte_chullachaqui.mp3")
                        death_sound.play()
                    except:
                        pass
                
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
                
                if self.config["sound_enabled"]:
                    try:
                        death_sound = pygame.mixer.Sound("assets/sounds/roar_muerte_yakumama.mp3")
                        death_sound.play()
                    except:
                        pass
        
        # Verificar derrota del jugador
        if self.player.hp <= 0:
            self.game_over = True
            self.victory = False
            self.stats["time"] = self.game_time
            self.stats["phases_completed"] = self.current_phase - 1

            if self.config["sound_enabled"]:
                try:
                    defeat_sound = pygame.mixer.Sound("assets/sounds/derrota.mp3")
                    defeat_sound.play()
                except:
                    pass
    
    def start_phase_transition(self):
        self.phase_transition = True
        self.transition_timer = 0
        self.stats["phases_completed"] = self.current_phase
        print(f"¡Fase {self.current_phase} completada! Preparando Fase {self.current_phase + 1}...")
    
    def update_transition(self, dt):
        self.transition_timer += dt
        
        if self.transition_timer >= self.transition_duration:
            self.advance_to_next_phase()
    
    def advance_to_next_phase(self):
        self.current_phase += 1
        self.phase_transition = False
        self.transition_timer = 0
        
        mod = GAME_MODE_MODIFIERS[self.config["game_mode"]]

        # Crear nuevo boss
        self.boss = Boss(WIDTH // 2, 100, self.ai_brain, phase=self.current_phase, difficulty_mod=mod)
        
        if self.config["sound_enabled"]:
            try:
                if self.current_phase == 2:
                    appear_sound = pygame.mixer.Sound("assets/sounds/roar_inicio_yakuruna.mp3")
                elif self.current_phase == 3:
                    appear_sound = pygame.mixer.Sound("assets/sounds/roar_inicio_yakuruna.mp3")
                appear_sound.play()
            except:
                pass
        
        # Resetear jugador
        self.player.reset_for_new_phase()
        
        # Limpiar bosses revividos
        self.revived_bosses.clear()
        
        print(f"¡FASE {self.current_phase} INICIADA: {self.boss.name}!")
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Arena
        pygame.draw.rect(self.screen, WHITE, 
                         (ARENA_X, ARENA_Y, ARENA_WIDTH, ARENA_HEIGHT), 3)
        
        if not self.phase_transition:
            # Dibujar entidades
            if self.player:
                self.player.draw(self.screen)
            if self.boss:
                self.boss.draw(self.screen)
            
            # Dibujar bosses revividos
            for revived_boss in self.revived_bosses:
                revived_boss.draw(self.screen)
            
            # UI
            self.draw_ui()
        else:
            self.draw_phase_transition()
        
        # Game Over
        if self.game_over:
            self.draw_game_over()
    
    def draw_ui(self):
        if not self.player or not self.boss:
            return
            
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
        
        # Modo de juego
        mode_text = small_font.render(f"Modo: {self.config['game_mode'].upper()}", True, GOLD)
        self.screen.blit(mode_text, (WIDTH - 200, 20))
        
        # Estado del boss
        phase_color = BOSS_PHASES[self.current_phase]["color"]
        phase_text = font.render(f"FASE {self.current_phase} - {self.boss.state.upper()}", 
                                 True, phase_color)
        self.screen.blit(phase_text, (WIDTH - 350, 50))
        
        # Contador de esquivos
        dodges_text = small_font.render(f"Esquivos: {self.player.dodges_for_special}/{SPECIAL_ATTACK_DODGES}", 
        True, CYAN if not self.player.attack_mode else GOLD)
        self.screen.blit(dodges_text, (20, 80))
        
        # Modo ataque
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
        
        # Bosses revividos
        if len(self.revived_bosses) > 0:
            revived_text = small_font.render(f"Espíritus: {len(self.revived_bosses)}", 
            True, PURPLE)
            self.screen.blit(revived_text, (WIDTH - 200, 80))
    
    def draw_phase_transition(self):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        font = pygame.font.Font(None, 72)
        small_font = pygame.font.Font(None, 36)
        
        completed_text = font.render(f"FASE {self.current_phase} COMPLETADA", True, GREEN)
        self.screen.blit(completed_text, 
                         (WIDTH // 2 - completed_text.get_width() // 2, HEIGHT // 2 - 100))
        
        next_phase = self.current_phase + 1
        next_name = BOSS_PHASES[next_phase]["name"]
        next_text = font.render(f"Siguiente: {next_name}", True, 
        BOSS_PHASES[next_phase]["color"])
        self.screen.blit(next_text, 
                         (WIDTH // 2 - next_text.get_width() // 2, HEIGHT // 2)) 
        
        time_left = self.transition_duration - self.transition_timer
        timer_text = small_font.render(f"Comenzando en: {int(time_left) + 1}", True, WHITE)
        self.screen.blit(timer_text, 
                         (WIDTH // 2 - timer_text.get_width() // 2, HEIGHT // 2 + 130))
    
    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        font = pygame.font.Font(None, 72)
        medium_font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 28)
        
        y_offset = HEIGHT // 2 - 200
        
        if self.victory:
            title = font.render("¡VICTORIA!", True, GOLD)
            subtitle = medium_font.render(f"Modo {self.config['game_mode'].upper()} completado 🎉", True, WHITE)
        else:
            title = font.render("DERROTA", True, RED)
            subtitle = medium_font.render(f"Fase alcanzada: {self.current_phase} 💀", True, WHITE)
        
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, y_offset))
        self.screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, y_offset + 80))
        
        y_offset += 150
        stats_title = medium_font.render("ESTADÍSTICAS:", True, YELLOW)
        self.screen.blit(stats_title, (WIDTH // 2 - stats_title.get_width() // 2, y_offset))
        
        y_offset += 50
        if self.player:
            stats_texts = [
                f"Tiempo: {int(self.stats['time'])} segundos",
                f"Fases: {self.stats['phases_completed']}/3",
                f"Daño infligido: {int(self.stats['damage_dealt'])}",
                f"Esquivos: {self.player.total_dodges}",
            ]
        else:
            stats_texts = [
                f"Tiempo: {int(self.stats['time'])} segundos",
                f"Fases: {self.stats['phases_completed']}/3",
            ]
        
        for text in stats_texts:
            stat_surf = small_font.render(text, True, WHITE)
            self.screen.blit(stat_surf, (WIDTH // 2 - stat_surf.get_width() // 2, y_offset))
            y_offset += 35
        
        restart = medium_font.render("R: Reiniciar | ESC: Menú", True, CYAN)
        self.screen.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT - 60))

if __name__ == "__main__":
    game = Game()
    game.run()