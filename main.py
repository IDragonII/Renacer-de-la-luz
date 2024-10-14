import pygame
import sys
from settings import *
from level import Level
from level2 import Level2
from player import Player
from weapon import Weapon
from enemy import Enemy
from magic import MagicPlayer
from particles import AnimationPlayer
import json



class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGTH))
        pygame.display.set_caption('El renacer de ka luz')
        self.clock = pygame.time.Clock()
        self.level = Level()
        self.visible_sprites = pygame.sprite.Group()
        self.attack_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()

        self.current_attack = None
        self.attackable_sprites = pygame.sprite.Group()

        self.animation_player = AnimationPlayer()
        self.magic_player = MagicPlayer(self.animation_player)

        x, y = WIDTH//2, HEIGTH//2
        self.player = Player(
            (x, y),
            [self.visible_sprites],
            self.obstacle_sprites,
            self.create_attack,
            self.destroy_attack,
            self.create_magic
        )


    def run(self):
        pygame.mixer.music.load('audio/Game.mp3')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(loops=-1)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        self.level.toggle_menu()

            self.screen.fill(WATER_COLOR)
            self.level.run()
            pygame.display.update()
            self.clock.tick(FPS)

    def show_start_screen(self):
        pygame.mixer.music.load('audio/inicio.mp3')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(loops=-1)

        background_image = pygame.image.load('fondo/fondoInicio.png').convert()

        title = (255, 38, 142)
        colorText = (59, 217, 124)
        grey_hover = (43, 160, 92)

        font = pygame.font.Font(None, 60)
        button_font = pygame.font.Font(None, 36)

        title_text = font.render("Fantasy World", True, title)

        new_game_button = pygame.Rect(WIDTH - 475, HEIGTH - 300, 200, 50)
        continue_button = pygame.Rect(WIDTH - 475, HEIGTH - 250, 200, 50)
        quit_button = pygame.Rect(WIDTH - 475, HEIGTH - 150, 200, 50)
        select_level_button = pygame.Rect(WIDTH - 475, HEIGTH - 200, 200, 50)

        running = True
        while running:
            self.screen.blit(background_image, (0, 0))

            self.screen.blit(title_text, (WIDTH - 410, HEIGTH - 360))

            mouse_pos = pygame.mouse.get_pos()
            for button, text in [(new_game_button, "Nuevo Juego"),
                                (continue_button, "Continuar"),
                                (quit_button, "Salir"),
                                (select_level_button, "Seleccionar Nivel")]:
                if button.collidepoint(mouse_pos):
                    text_color = grey_hover
                else:
                    text_color = colorText
                button_text = button_font.render(text, True, text_color)
                self.screen.blit(button_text, (button.x + 10, button.y + (button.height - button_text.get_height()) // 2))  # 10 píxeles de margen a la izquierda

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if new_game_button.collidepoint(event.pos):
                        pygame.mixer.music.stop()
                        running = False
                        self.show_story_screen_1()
                    if continue_button.collidepoint(event.pos):
                        pygame.mixer.music.stop()
                        running = False
                        self.run()
                    if quit_button.collidepoint(event.pos):
                        pygame.mixer.music.stop()
                        pygame.quit()
                        sys.exit()
                    if select_level_button.collidepoint(event.pos):
                        running = False
                        self.select_level()

    def select_level(self):
        black = (0, 0, 0)
        white = (255, 255, 255)
        grey = (100, 100, 100)
        hover_color = (150, 150, 150)
        font = pygame.font.Font(None, 36)

        background_image = pygame.image.load('fondo/fondoSeleccion.png')
        background_image = pygame.transform.scale(background_image, (WIDTH, HEIGTH))  

        level1_button = pygame.Rect(WIDTH-400, 150, 200, 50)
        level2_button = pygame.Rect(WIDTH-400, 200, 200, 50)

        Salir_button = pygame.Rect(WIDTH-310, 600, 200, 50)

        title_text = font.render("Seleccione un Nivel", True, white)
        title_rect = title_text.get_rect(center=(WIDTH-210, 100))

        running = True
        while running:
            self.screen.blit(background_image, (0, 0))

            mouse_pos = pygame.mouse.get_pos()

            button_surface1 = pygame.Surface((level1_button.width, level1_button.height), pygame.SRCALPHA)
            button_surface2 = pygame.Surface((level2_button.width, level2_button.height), pygame.SRCALPHA)
            button_surface3 = pygame.Surface((level2_button.width, level2_button.height), pygame.SRCALPHA)


            button_color = (grey[0], grey[1], grey[2], 150)
            pygame.draw.rect(button_surface1, button_color, (0, 0, level1_button.width, level1_button.height))
            pygame.draw.rect(button_surface2, button_color, (0, 0, level2_button.width, level2_button.height))
            pygame.draw.rect(button_surface3, button_color, (0, 0, Salir_button.width, Salir_button.height))

            if level1_button.collidepoint(mouse_pos):
                level1_text = font.render("Nivel 1", True, hover_color)
            else:
                level1_text = font.render("Nivel 1", True, white)

            if level2_button.collidepoint(mouse_pos):
                level2_text = font.render("Nivel 2", True, hover_color)
            else:
                level2_text = font.render("Nivel 2", True, white)

            if Salir_button.collidepoint(mouse_pos):
                salir_text = font.render("Regresar al menu", True, hover_color) 
            else:
                salir_text = font.render("Regresar al menu", True, white) 

            self.screen.blit(level1_text, (level1_button.x + (level1_button.width - level1_text.get_width()) // 2, level1_button.y + (level1_button.height - level1_text.get_height()) // 2))
            self.screen.blit(level2_text, (level2_button.x + (level2_button.width - level2_text.get_width()) // 2, level2_button.y + (level2_button.height - level2_text.get_height()) // 2))
            self.screen.blit(salir_text, (Salir_button.x + (Salir_button.width - salir_text.get_width()) // 2, Salir_button.y + (Salir_button.height - salir_text.get_height()) // 2))

            self.screen.blit(title_text, title_rect)

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if level1_button.collidepoint(event.pos):
                        pygame.mixer.music.stop()
                        self.level = Level()
                        running = False
                    if level2_button.collidepoint(event.pos):
                        pygame.mixer.music.stop()
                        self.level = Level2()
                        running = False
                    if Salir_button.collidepoint(event.pos):
                        self.show_start_screen()
                        running = False


    def create_attack(self):
        self.current_attack = Weapon(self.player, [self.visible_sprites, self.attack_sprites])
    def create_magic(self,style,strength,cost):
        if style == 'heal':
            self.magic_player.heal(self.player,strength,cost,[self.visible_sprites])
        if style == 'flame':
            self.magic_player.flame(self.player,cost,[self.visible_sprites,self.attack_sprites])
    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

    def ask_for_tutorial(self):
        background_image = pygame.image.load('fondo/questTutorial.png').convert()

        white = (255, 255, 255)
        grey = (100, 100, 100)
        hover_color = (59, 217, 124)

        font = pygame.font.Font(None, 36)

        full_question_text = "¿Deseas hacer el tutorial?"
        question_text = ""
        text_index = 0
        typing_timer = pygame.time.get_ticks()
        typing_interval = 50

        yes_button = pygame.Rect( 100, HEIGTH-100, 50, 50)
        no_button = pygame.Rect( 150, HEIGTH-100, 50, 50)

        running = True
        while running:
            self.screen.blit(background_image, (0, 0))

            if text_index < len(full_question_text):
                if pygame.time.get_ticks() - typing_timer > typing_interval:
                    question_text += full_question_text[text_index]
                    text_index += 1 
                    typing_timer = pygame.time.get_ticks()

            rendered_question_text = font.render(question_text, True, white)
            self.screen.blit(rendered_question_text, (80, HEIGTH-150))

            mouse_pos = pygame.mouse.get_pos()
            for button, text in [(yes_button, "Sí"), (no_button, "No")]:
                if button.collidepoint(mouse_pos):
                    text_color = hover_color 
                else:
                    text_color = white 

                button_text = font.render(text, True, text_color)
                self.screen.blit(button_text, (button.x + (button.width - button_text.get_width()) // 2, button.y + (button.height - button_text.get_height()) // 2))  # Centrar el texto en el botón

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if yes_button.collidepoint(event.pos) and text_index == len(full_question_text): 
                        running = False
                        self.show_tutorial()
                    if no_button.collidepoint(event.pos) and text_index == len(full_question_text):  
                        running = False
                        self.run() 


    def show_tutorial(self):
        pygame.mixer.music.load('audio/Game.mp3')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(loops=-1)

        background_image = pygame.image.load('fondo/tutorial.png').convert() 

        white = (255, 255, 255)

        font = pygame.font.Font(None, 25)
        fontPas = pygame.font.Font(None, 36)

        tutorial_lines = [
            "Usa las siguientes teclas para controlar a tu personaje:",
            "    ",
            "- Flechas para moverte",
            "- Espacio para atacar",
            "- M para abrir el menú",
            "- Ctrl para abrir usar magia",
            "- Q para cambiar de arma",
            "- E para cambiar de magia",
            "- S para guardar partida",
            "- L para cargar partida"
        ]

        blinking_message = "Presiona 'Enter' para avanzar"
        message_counter = 0
        message_show = True
        running = True
        self.create_attack()

        max_text_width = 330

        def wrap_text(text, max_width):
            words = text.split(' ')
            lines = []
            current_line = ""

            for word in words:
                test_line = current_line + word + " "
                if font.size(test_line)[0] <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word + " "

            if current_line:
                lines.append(current_line)

            return lines

        wrapped_tutorial_lines = []
        for line in tutorial_lines:
            wrapped_tutorial_lines.extend(wrap_text(line, max_text_width))
        
        self.destroy_attack()

        while running:
            self.screen.blit(background_image, (0, 0))

            text_x = WIDTH - max_text_width - 25
            text_y = 75  

            for line in wrapped_tutorial_lines:
                tutorial_text = font.render(line.strip(), True, white)
                self.screen.blit(tutorial_text, (text_x, text_y))
                text_y += 20 

            self.visible_sprites.draw(self.screen)

            self.player.stats['speed'] = 1
            self.player.update()
            if message_show:
                blinking_text = fontPas.render(blinking_message, True, white)
                self.screen.blit(blinking_text, (WIDTH // 2 - blinking_text.get_width() // 2, HEIGTH - 100))

            message_counter += 1
            if message_counter >= 100:
                message_show = not message_show
                message_counter = 0
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        pygame.mixer.music.stop()
                        running = False
                        self.run()

        self.player.stats['speed'] = 5


    def show_story_screen_1(self):
        pygame.mixer.music.load('audio/historia.mp3')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(loops=-1)

        background_image = pygame.image.load('fondo/historia.png').convert()

        white = (255, 255, 255)

        story_font = pygame.font.Font(None, 36)
        press_any_key_font = pygame.font.Font(None, 36)

        story_lines = [
            "Hace mucho tiempo, en una tierra lejana,",
            "un mundo vibrante y lleno de vida fue invadido",
            "por una oscura Corrupción que lo consume todo.",
            "Los habitantes, una vez felices, ahora viven",
            "en el miedo, mientras la oscuridad se apodera.",
            "Un joven guerrero, con el corazón valiente,",
            "se levanta con la misión de restaurar la paz.",
            "Armado con su espada y su determinación,",
            "deberás enfrentar peligrosos enemigos",
            "y desmantelar la Corrupción que asola tu hogar."
        ]

        current_line_index = 0 
        current_text = "" 
        typing_speed = 50
        last_update_time = pygame.time.get_ticks()

        completed_lines = []

        show_press_key = False
        blink_timer = 0
        blink_interval = 500
        start_press_key_timer = pygame.time.get_ticks()

        running = True
        while running:
            self.screen.blit(background_image, (0, 0))

            current_time = pygame.time.get_ticks()
            if current_time - last_update_time > typing_speed:
                if current_line_index < len(story_lines):
                    current_text += story_lines[current_line_index][len(current_text):len(current_text) + 1]  
                    if len(current_text) >= len(story_lines[current_line_index]):
                        completed_lines.append(current_text)
                        current_line_index += 1 
                        current_text = ""
                last_update_time = current_time

            for i, line in enumerate(completed_lines):
                story_text = story_font.render(line, True, white)
                self.screen.blit(story_text, (WIDTH//2 - story_text.get_width()//2, HEIGTH//4 + i * 40))

            if current_text:
                typing_text = story_font.render(current_text, True, white)
                self.screen.blit(typing_text, (WIDTH//2 - typing_text.get_width()//2, HEIGTH//4 + len(completed_lines) * 40))

            if current_line_index >= len(story_lines):
                if pygame.time.get_ticks() - blink_timer > blink_interval:
                    show_press_key = not show_press_key
                    blink_timer = pygame.time.get_ticks()

                if show_press_key:
                    press_any_key_text = press_any_key_font.render("Presione cualquier tecla para avanzar", True, white)
                    self.screen.blit(press_any_key_text, (WIDTH//2 - press_any_key_text.get_width()//2, HEIGTH - 100))

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if current_line_index >= len(story_lines):
                        running = False
                        self.show_story_screen_2()



    def show_story_screen_2(self):

        background_image = pygame.image.load('fondo/historia.png').convert()

        white = (255, 255, 255)

        story_font = pygame.font.Font(None, 36)
        press_any_key_font = pygame.font.Font(None, 36)

        story_lines = [
            "Con cada victoria sobre la Corrupción,",
            "la esperanza renace en el corazón de la gente.",
            "Sin embargo, los líderes de esta oscuridad",
            "son astutos y poderosos, ocultos en las sombras.",
            "Cada uno de ellos guarda un fragmento de luz,",
            "y deberás enfrentarte a temibles jefes",
            "que han dominado las tierras perdidas.",
            "A medida que avanzas, desvelarás secretos antiguos,",
            "y descubrirás el verdadero origen de la Corrupción.",
            "No estarás solo las almas de los caídos te guiarán en la batalla final.",
            "Tu destino está entrelazado con el futuro del mundo,",
            "y solo tú puedes devolver la luz y la paz."
        ]

        current_line_index = 0 
        current_text = ""
        typing_speed = 50
        last_update_time = pygame.time.get_ticks()

        completed_lines = []

        show_press_key = False
        blink_timer = 0
        blink_interval = 500
        start_press_key_timer = pygame.time.get_ticks()

        running = True
        while running:
            self.screen.blit(background_image, (0, 0))

            current_time = pygame.time.get_ticks()
            if current_time - last_update_time > typing_speed:
                if current_line_index < len(story_lines):
                    current_text += story_lines[current_line_index][len(current_text):len(current_text) + 1]  
                    if len(current_text) >= len(story_lines[current_line_index]):
                        completed_lines.append(current_text)
                        current_line_index += 1
                        current_text = ""
                last_update_time = current_time

            for i, line in enumerate(completed_lines):
                story_text = story_font.render(line, True, white)
                self.screen.blit(story_text, (WIDTH//2 - story_text.get_width()//2, HEIGTH//5.5 + i * 40))

            if current_text:
                typing_text = story_font.render(current_text, True, white)
                self.screen.blit(typing_text, (WIDTH//2 - typing_text.get_width()//2, HEIGTH//4 + len(completed_lines) * 40))

            if current_line_index >= len(story_lines):
                if pygame.time.get_ticks() - blink_timer > blink_interval:
                    show_press_key = not show_press_key
                    blink_timer = pygame.time.get_ticks()

                if show_press_key:
                    press_any_key_text = press_any_key_font.render("Presione cualquier tecla para avanzar", True, white)
                    self.screen.blit(press_any_key_text, (WIDTH//2 - press_any_key_text.get_width()//2, HEIGTH - 100))

            pygame.display.update()


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    pygame.mixer.music.stop()
                    running = False
                    self.ask_for_tutorial()

game_instance = Game()
if __name__ == '__main__':
    game = Game()
    game.show_start_screen()
    game.run()
