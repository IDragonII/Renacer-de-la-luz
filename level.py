import pygame 
from settings import *
from tile import Tile
from player import Player
from debug import debug
from support import *
from random import choice, randint
from weapon import Weapon
from ui import UI
import sys
from enemy import Enemy
from particles import AnimationPlayer
from magic import MagicPlayer
from upgrade import Upgrade
import json

class Level:
	def __init__(self):
		self.display_surface = pygame.display.get_surface()
		self.game_paused = False

		self.visible_sprites = YSortCameraGroup()
		self.obstacle_sprites = pygame.sprite.Group()

		self.current_attack = None
		self.attack_sprites = pygame.sprite.Group()
		self.attackable_sprites = pygame.sprite.Group()

		self.raccoon_count = 0
		self.create_map()

		self.ui = UI()
		self.upgrade = Upgrade(self.player)

		self.animation_player = AnimationPlayer()
		self.magic_player = MagicPlayer(self.animation_player)
	
	def save_game(self):
		game_state = {
			'player': {
				'position': (self.player.rect.x, self.player.rect.y),
				'health': self.player.health,
				'exp': self.player.exp
			},
			'enemies': []
		}

		for enemy in self.attackable_sprites:
			if hasattr(enemy, 'sprite_type') and enemy.sprite_type == 'enemy':
				enemy_data = {
					'type': enemy.monster_name,
					'position': (enemy.rect.x, enemy.rect.y),
				}
				game_state['enemies'].append(enemy_data)

		with open('save_file.json', 'w') as save_file:
			json.dump(game_state, save_file)
		print("Game saved successfully!")
	def load_game(self):
		try:
			with open('save_file.json', 'r') as f:
				data = json.load(f)
				self.player.rect.x, self.player.rect.y = data["player"]["position"]
				self.player.health = data["player"]["health"]
				self.player.exp = data["player"]["exp"]
				print(f"Juego cargado. Posición del jugador: {self.player.rect.x}, {self.player.rect.y}")  
				self.attackable_sprites.empty()
				for enemy_data in data["enemies"]:
					enemy_type = enemy_data["type"]
					enemy_position = enemy_data["position"] 
					enemy = Enemy(enemy_type, enemy_position,
								[self.visible_sprites, self.attackable_sprites],
								self.obstacle_sprites,
								self.damage_player,
								self.trigger_death_particles,
								self.add_exp)
					self.visible_sprites.add(enemy)
					print(f"Enemigo {enemy_type} cargado en la posición: {enemy_position}")
		except FileNotFoundError:
			print("Archivo de guardado no encontrado. Se establecerán valores por defecto.")
			self.player.rect.x, self.player.rect.y = 100, 100
			self.player.health = 100
			self.player.exp = 0
		except json.JSONDecodeError:
			print("Error al cargar el juego: archivo JSON está corrupto.")
		except Exception as e:
			print(f"Error inesperado al cargar el juego: {e}")
		self.run()



	def create_map(self):
		layouts = {
			'boundary': import_csv_layout('map/map_FloorBlocks.csv'),
			'grass': import_csv_layout('map/map_Grass.csv'),
			'object': import_csv_layout('map/map_Objects.csv'),
			'entities': import_csv_layout('map/map_Entities.csv')
		}
		graphics = {
			'grass': import_folder('graphics/Grass'),
			'objects': import_folder('graphics/objects')
		}

		for style,layout in layouts.items():
			for row_index,row in enumerate(layout):
				for col_index, col in enumerate(row):
					if col != '-1':
						x = col_index * TILESIZE
						y = row_index * TILESIZE
						if style == 'boundary':
							Tile((x,y),[self.obstacle_sprites],'invisible')
						if style == 'grass':
							random_grass_image = choice(graphics['grass'])
							Tile(
								(x,y),
								[self.visible_sprites,self.obstacle_sprites,self.attackable_sprites],
								'grass',
								random_grass_image)

						if style == 'object':
							surf = graphics['objects'][int(col)]
							Tile((x,y),[self.visible_sprites,self.obstacle_sprites],'object',surf)

						if style == 'entities':
							if col == '394':
								self.player = Player(
									(x,y),
									[self.visible_sprites],
									self.obstacle_sprites,
									self.create_attack,
									self.destroy_attack,
									self.create_magic)
							else:
								if col == '390': monster_name = 'bamboo'
								elif col == '391': monster_name = 'spirit'
								elif col == '392': 
									monster_name ='raccoon'
									self.raccoon_count += 1 
								else: monster_name = 'squid'
								Enemy(
									monster_name,
									(x,y),
									[self.visible_sprites,self.attackable_sprites],
									self.obstacle_sprites,
									self.damage_player,
									self.trigger_death_particles,
									self.add_exp)

	def create_attack(self):
		
		self.current_attack = Weapon(self.player,[self.visible_sprites,self.attack_sprites])
	def count_monsters(self):
		monster_count = 0
		for sprite in self.attackable_sprites:
			if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'enemy':
				monster_count += 1
		return monster_count

	def create_magic(self,style,strength,cost):
		if style == 'heal':
			self.magic_player.heal(self.player,strength,cost,[self.visible_sprites])

		if style == 'flame':
			self.magic_player.flame(self.player,cost,[self.visible_sprites,self.attack_sprites])

	def destroy_attack(self):
		if self.current_attack:
			self.current_attack.kill()
		self.current_attack = None

	def player_attack_logic(self):
		if self.attack_sprites:
			for attack_sprite in self.attack_sprites:
				collision_sprites = pygame.sprite.spritecollide(attack_sprite,self.attackable_sprites,False)
				if collision_sprites:
					for target_sprite in collision_sprites:
						if target_sprite.sprite_type == 'grass':
							pos = target_sprite.rect.center
							offset = pygame.math.Vector2(0,75)
							for leaf in range(randint(3,6)):
								self.animation_player.create_grass_particles(pos - offset,[self.visible_sprites])
							target_sprite.kill()
						else:
							target_sprite.get_damage(self.player,attack_sprite.sprite_type)

	def damage_player(self,amount,attack_type):
		if self.player.vulnerable:
			self.player.health -= amount
			self.player.vulnerable = False
			self.player.hurt_time = pygame.time.get_ticks()
			self.animation_player.create_particles(attack_type,self.player.rect.center,[self.visible_sprites])

	def trigger_death_particles(self,pos,particle_type):

		self.animation_player.create_particles(particle_type,pos,self.visible_sprites)

	def add_exp(self,amount):

		self.player.exp += amount

	def toggle_menu(self):

		self.game_paused = not self.game_paused 

	def run(self):
		self.visible_sprites.custom_draw(self.player)
		self.ui.display(self.player)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_s:
					self.save_game()
				if event.key == pygame.K_l:
					self.load_game()
		
		if self.game_paused:
			self.upgrade.display()
		else:
			self.visible_sprites.update()
			self.visible_sprites.enemy_update(self.player)
			self.player_attack_logic()
			self.check_victory()
	def check_victory(self):
		if self.count_monsters() == 0:
			
			self.display_victory_message()

	def display_victory_message(self):
		from main import game_instance
		pygame.mixer.music.stop()
		pygame.mixer.music.load('audio/win.mp3')
		pygame.mixer.music.set_volume(0.5)
		pygame.mixer.music.play(loops=-1)
		
		background_image = pygame.image.load('fondo/ganador.png')
		background_image = pygame.transform.scale(background_image, (WIDTH, HEIGTH))

		victory_font = pygame.font.Font(None, 74)
		victory_surface = victory_font.render('Tu historia continua', True, (255, 0, 0))
		victory_rect = victory_surface.get_rect(center=(WIDTH // 2, HEIGTH // 2-50))

		end_time = pygame.time.get_ticks() + 3000
		while True:
			self.screen.blit(background_image, (0, 0))

			self.screen.blit(victory_surface, victory_rect)

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
			if pygame.time.get_ticks() > end_time:
				break
			
			pygame.display.flip()
		self.health = 100
		game_instance.select_level()

		

class YSortCameraGroup(pygame.sprite.Group):
	def __init__(self):

		super().__init__()
		self.display_surface = pygame.display.get_surface()
		self.half_width = self.display_surface.get_size()[0] // 2
		self.half_height = self.display_surface.get_size()[1] // 2
		self.offset = pygame.math.Vector2()

		self.floor_surf = pygame.image.load('graphics/tilemap/ground.png').convert()
		self.floor_rect = self.floor_surf.get_rect(topleft = (0,0))
	
	def custom_draw(self,player):

		self.offset.x = player.rect.centerx - self.half_width
		self.offset.y = player.rect.centery - self.half_height

		floor_offset_pos = self.floor_rect.topleft - self.offset
		self.display_surface.blit(self.floor_surf,floor_offset_pos)

		for sprite in sorted(self.sprites(),key = lambda sprite: sprite.rect.centery):
			offset_pos = sprite.rect.topleft - self.offset
			self.display_surface.blit(sprite.image,offset_pos)

	def enemy_update(self,player):
		enemy_sprites = [sprite for sprite in self.sprites() if hasattr(sprite,'sprite_type') and sprite.sprite_type == 'enemy']
		for enemy in enemy_sprites:
			enemy.enemy_update(player)
