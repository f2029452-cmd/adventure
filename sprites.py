import pygame
from config import *
import math
import random

class Spritesheet:
    def __init__(self, file):
        self.sheet = pygame.image.load(file).convert()

    def get_sprite(self, x, y, width, height, color = WHITE):
        sprite = pygame.Surface([width, height])
        sprite.blit(self.sheet, (0, 0), (x, y, width, height))
        sprite.set_colorkey(color)
        return sprite

class Get_image:
    def __init__(self, file):
        self.image = pygame.image.load(file).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))

    def get_sprite(self, x, y, width, height, color = WHITE):
        sprite = pygame.Surface([width, height])
        sprite.blit(self.image, (0, 0), (x, y, width, height))
        sprite.set_colorkey(color)
        return sprite 

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.x_change = 0
        self.y_change = 0

        self.facing = 'down'
        self.animation_loop = 1

        self.image = self.game.character_spritesheet.get_sprite(0, 0, 32, 32).convert_alpha()
        self.image.set_colorkey(WHITE)
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.open_inventory = False
        self.open_inventory_cooldown = 0

        self.weapon_index = None
        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = None
        self.strength = 1
        self.sword_durability = DURABILITY
        self.axe_durability = DURABILITY
        self.lance_durability = DURABILITY
        self.rapier_durability = DURABILITY
        self.sai_durability = DURABILITY

        self.coin_count = 0
        self.food_bar_reduction_count = 'low'
        self.saturation_bar_reduction_count = 'low'

        self.down_animations = [pygame.transform.scale(self.game.character_spritesheet.get_sprite(0, 32, 32, 32), (TILESIZE, TILESIZE)).convert_alpha(),
                           pygame.transform.scale(self.game.character_spritesheet.get_sprite(0, 0, 32, 32), (TILESIZE, TILESIZE)).convert_alpha(),
                           pygame.transform.scale(self.game.character_spritesheet.get_sprite(0, 96, 32, 32), (TILESIZE, TILESIZE)).convert_alpha()]

        self.up_animations = [pygame.transform.scale(self.game.character_spritesheet.get_sprite(35, 32, 32, 32), (TILESIZE, TILESIZE)).convert_alpha(),
                         pygame.transform.scale(self.game.character_spritesheet.get_sprite(35, 64, 32, 32), (TILESIZE, TILESIZE)).convert_alpha(),
                         pygame.transform.scale(self.game.character_spritesheet.get_sprite(35, 96, 32, 32), (TILESIZE, TILESIZE)).convert_alpha()]

        self.left_animations = [pygame.transform.scale(self.game.character_spritesheet.get_sprite(67, 32, 32, 32), (TILESIZE, TILESIZE)).convert_alpha(),
                           pygame.transform.scale(self.game.character_spritesheet.get_sprite(67, 64, 32, 32), (TILESIZE, TILESIZE)).convert_alpha(),
                           pygame.transform.scale(self.game.character_spritesheet.get_sprite(67, 96, 32, 32), (TILESIZE, TILESIZE)).convert_alpha()]

        self.right_animations = [pygame.transform.scale(self.game.character_spritesheet.get_sprite(99, 32, 32, 32), (TILESIZE, TILESIZE)).convert_alpha(),
                            pygame.transform.scale(self.game.character_spritesheet.get_sprite(99, 64, 32, 32), (TILESIZE, TILESIZE)).convert_alpha(),
                            pygame.transform.scale(self.game.character_spritesheet.get_sprite(99, 96, 32, 32), (TILESIZE, TILESIZE)).convert_alpha()]

        self.stats = {'health': 200, 'energy': 60, 'attack':10, 'food_bar': 200, 'saturation_bar': 300}
        self.health = self.stats['health']
        self.food_bar = self.stats['food_bar']
        self.energy = self.stats['energy']
        self.attack = self.stats['attack'] * self.strength
        self.saturation_bar = self.stats['saturation_bar'] - 275
        self.exp = 0

    def update(self):
        self.movement()
        self.cooldowns()
        self.animate()
        self.collide_enemies()
        self.rect.x += self.x_change
        self.collide_blocks('x')
        self.rect.y += self.y_change
        self.collide_blocks('y')
        self.collide_coin()

        self.x_change = 0
        self.y_change = 0

    def movement(self):
        keys = pygame.key.get_pressed()

        if not self.open_inventory and not self.game.chest.open_storage and not self.game.smith.open_menu:
            if not self.attacking:
                if keys[pygame.K_w]:
                    for sprite in self.game.all_sprites:
                        sprite.rect.y += PLAYER_SPEED
                    self.y_change -= PLAYER_SPEED
                    self.facing = 'up'

                if keys[pygame.K_s]:
                    for sprite in self.game.all_sprites:
                        sprite.rect.y -= PLAYER_SPEED
                    self.y_change += PLAYER_SPEED
                    self.facing = 'down'

                if keys[pygame.K_a]:
                    for sprite in self.game.all_sprites:
                        sprite.rect.x += PLAYER_SPEED
                    self.x_change -= PLAYER_SPEED
                    self.facing = 'left'

                if keys[pygame.K_d]:
                    for sprite in self.game.all_sprites:
                        sprite.rect.x -= PLAYER_SPEED
                    self.x_change += PLAYER_SPEED
                    self.facing = 'right'

            if keys[pygame.K_SPACE] and self.weapon_index is not None:
                self.attacking = True
                self.food_bar_reduction_count = 'min'
                self.attack_time = pygame.time.get_ticks()
                if self.facing == 'up':
                    Attack(self.game, self.rect.x+6, self.rect.y - TILESIZE+18, self.weapon_index)
                if self.facing == 'down':
                    Attack(self.game, self.rect.x+6, self.rect.y + TILESIZE, self.weapon_index)
                if self.facing == 'left':
                    Attack(self.game, self.rect.x - TILESIZE+18, self.rect.y+22, self.weapon_index)
                if self.facing == 'right':
                    Attack(self.game, self.rect.x + TILESIZE, self.rect.y+22, self.weapon_index)
        
        if keys[pygame.K_e] and not self.open_inventory:
            self.open_inventory = True
        elif keys[pygame.K_r] and self.open_inventory:
            self.open_inventory = False
            if self.game.chest.open_storage:
                self.game.chest.open_storage = False
            
    def cooldowns(self):
        current_time = pygame.time.get_ticks()

        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.attacking = False

        if self.saturation_bar > 0:
            if self.saturation_bar_reduction_count == 'max':
                self.saturation_bar -= 0.02
            elif self.saturation_bar_reduction_count == 'low':
                self.saturation_bar -= 0.02/3

        if self.saturation_bar <= 0:
            if self.food_bar_reduction_count == 'max':
                self.food_bar -= 0.02
            elif self.food_bar_reduction_count == 'min':
                self.food_bar -= 0.001
            elif self.food_bar_reduction_count == 'low':
                self.food_bar -= 0

        if self.health < 200:
            if self.saturation_bar >= 1:
                self.health += 1
                self.saturation_bar -= 1

    def collide_enemies(self):
        hits = pygame.sprite.spritecollide(self, self.game.enemies, False)
        if hits:
            self.health -= 10
            if self.health <= 0:
                self.game.playing = False

    def collide_coin(self):
        hits = pygame.sprite.spritecollide(self, self.game.coins, True)
        if hits:
            self.coin_count += 1

    def collide_blocks(self, direction):
        if direction == 'x':
            hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
            if hits:
                if self.x_change > 0:
                    self.rect.x = hits[0].rect.left - self.rect.width
                    for sprite in self.game.all_sprites:
                        sprite.rect.x += PLAYER_SPEED
                if self.x_change < 0:
                    self.rect.x = hits[0].rect.right
                    for sprite in self.game.all_sprites:
                        sprite.rect.x -= PLAYER_SPEED

        if direction == 'y':
            hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
            if hits:
                if self.y_change > 0:
                    self.rect.y = hits[0].rect.top - self.rect.height
                    for sprite in self.game.all_sprites:
                        sprite.rect.y += PLAYER_SPEED
                if self.y_change < 0:
                    self.rect.y = hits[0].rect.bottom
                    for sprite in self.game.all_sprites:
                        sprite.rect.y -= PLAYER_SPEED

    def animate(self):
        if self.facing == 'down':
            if self.y_change == 0:
                self.image = self.game.character_spritesheet.get_sprite(0, 0, 32, 32)
                self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
                self.food_bar_reduction_count = 'low'
                self.saturation_bar_reduction_count = 'low'
            else:
                self.food_bar_reduction_count = 'max'
                self.saturation_bar_reduction_count = 'max'
                self.image = self.down_animations[math.floor(self.animation_loop)]
                self.animation_loop += ANIMATION_ITERATION
                if self.animation_loop > 3:
                    self.animation_loop = 1

        if self.facing == 'up':
            if self.y_change == 0:
                self.image = self.game.character_spritesheet.get_sprite(35, 0, 32, 32)
                self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
                self.food_bar_reduction_count = 'low'
                self.saturation_bar_reduction_count = 'low'
            else:
                self.food_bar_reduction_count = 'max'
                self.saturation_bar_reduction_count = 'max'
                self.image = self.up_animations[math.floor(self.animation_loop)]
                self.animation_loop += ANIMATION_ITERATION
                if self.animation_loop > 3:
                    self.animation_loop = 1

        if self.facing == 'left':
            if self.x_change == 0:
                self.image = self.game.character_spritesheet.get_sprite(67, 0, 32, 32)
                self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
                self.food_bar_reduction_count = 'low'
                self.saturation_bar_reduction_count = 'low'
            else:
                self.food_bar_reduction_count = 'max'
                self.saturation_bar_reduction_count = 'max'
                self.image = self.left_animations[math.floor(self.animation_loop)]
                self.animation_loop += ANIMATION_ITERATION
                if self.animation_loop > 3:
                    self.animation_loop = 1

        if self.facing == 'right':
            if self.x_change == 0:
                self.image = self.game.character_spritesheet.get_sprite(99, 0, 32, 32)
                self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
                self.food_bar_reduction_count = 'low'
                self.saturation_bar_reduction_count = 'low'
            else:
                self.food_bar_reduction_count = 'max'
                self.saturation_bar_reduction_count = 'max'
                self.image = self.right_animations[math.floor(self.animation_loop)]
                self.animation_loop += ANIMATION_ITERATION
                if self.animation_loop > 3:
                    self.animation_loop = 1

class Blue_fire_spirit(pygame.sprite.Sprite):
    def __init__(self, game, x, y, facing = 'random'):
        self.game = game
        self._layer =  ENEMY_LAYER
        self.groups = self.game.all_sprites, self.game.enemies
        self.facing = facing
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.x_change = 0
        self.y_change = 0

        self.health = 200

        if self.facing == 'random':
            self.facing = random.choice(['left', 'right', 'up', 'down'])
       
        self.animation_loop = 1
        self.movement_loop = 0
        self.max_travel_x = random.randint(7, 30)
        self.max_travel_y = random.randint(7, 30)

        self.image = self.game.enemy_spritesheet.get_sprite(0, 0, 32, 32).convert_alpha()
        self.image.set_colorkey(WHITE)
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.down_animations = [pygame.transform.scale(self.game.enemy_spritesheet.get_sprite(0, 32, 32, 32), (TILESIZE, TILESIZE)).convert_alpha(),
                           pygame.transform.scale(self.game.enemy_spritesheet.get_sprite(0, 64, 32, 32), (TILESIZE, TILESIZE)).convert_alpha(),
                           pygame.transform.scale(self.game.enemy_spritesheet.get_sprite(0, 96, 32, 32), (TILESIZE, TILESIZE)).convert_alpha()]

        self.up_animations = [pygame.transform.scale(self.game.enemy_spritesheet.get_sprite(32, 32, 32, 32), (TILESIZE, TILESIZE)).convert_alpha(),
                         pygame.transform.scale(self.game.enemy_spritesheet.get_sprite(32, 64, 32, 32), (TILESIZE, TILESIZE)).convert_alpha(),
                         pygame.transform.scale(self.game.enemy_spritesheet.get_sprite(32, 96, 32, 32), (TILESIZE, TILESIZE)).convert_alpha()]

        self.left_animations = [pygame.transform.scale(self.game.enemy_spritesheet.get_sprite(64, 32, 32, 32), (TILESIZE, TILESIZE)).convert_alpha(),
                           pygame.transform.scale(self.game.enemy_spritesheet.get_sprite(64, 64, 32, 32), (TILESIZE, TILESIZE)).convert_alpha(),
                           pygame.transform.scale(self.game.enemy_spritesheet.get_sprite(64, 96, 32, 32), (TILESIZE, TILESIZE)).convert_alpha()]

        self.right_animations = [pygame.transform.scale(self.game.enemy_spritesheet.get_sprite(96, 32, 32, 32), (TILESIZE, TILESIZE)).convert_alpha(),
                            pygame.transform.scale(self.game.enemy_spritesheet.get_sprite(96, 64, 32, 32), (TILESIZE, TILESIZE)).convert_alpha(),
                            pygame.transform.scale(self.game.enemy_spritesheet.get_sprite(96, 96, 32, 32), (TILESIZE, TILESIZE)).convert_alpha()]

    def update(self):
        self.movement()
        self.animate()
        self.rect.x += self.x_change
        self.rect.y += self.y_change

        self.x_change = 0
        self.y_change = 0

    def movement(self):
        if self.facing == 'up':
            self.y_change  -= BLUE_FIRE_ENEMY_SPEED
            self.movement_loop -= 1
            if self.movement_loop <= -self.max_travel_y:
                self.facing = 'down'
        
        if self.facing == 'down':
            self.y_change += BLUE_FIRE_ENEMY_SPEED
            self.movement_loop += 1
            if self.movement_loop >= self.max_travel_y:
                self.facing = 'up'

        if self.facing == 'left':
            self.x_change -= BLUE_FIRE_ENEMY_SPEED
            self.movement_loop -= 1
            if self.movement_loop <= -self.max_travel_x:
                self.facing = 'right'

        if self.facing == 'right':
            self.x_change += BLUE_FIRE_ENEMY_SPEED
            self.movement_loop += 1
            if self.movement_loop >= self.max_travel_x:
                self.facing = 'left'

    def animate(self):
        if self.facing == 'down':
            if self.y_change == 0:
                self.image = self.game.enemy_spritesheet.get_sprite(0, 0, 32, 32)
            else:
                self.image = self.down_animations[math.floor(self.animation_loop)]
                self.animation_loop += ANIMATION_ITERATION
                if self.animation_loop > 3:
                    self.animation_loop = 1

        if self.facing == 'up':
            if self.y_change == 0:
                self.image = self.game.enemy_spritesheet.get_sprite(32, 0, 32, 32)
            else:
                self.image = self.up_animations[math.floor(self.animation_loop)]
                self.animation_loop += ANIMATION_ITERATION
                if self.animation_loop > 3:
                    self.animation_loop = 1

        if self.facing == 'left':
            if self.x_change == 0:
                self.image = self.game.enemy_spritesheet.get_sprite(64, 0, 32, 32)
            else:
                self.image = self.left_animations[math.floor(self.animation_loop)]
                self.animation_loop += ANIMATION_ITERATION
                if self.animation_loop > 3:
                    self.animation_loop = 1

        if self.facing == 'right':
            if self.x_change == 0:
                self.image = self.game.character_spritesheet.get_sprite(96, 0, 32, 32)
            else:
                self.image = self.right_animations[math.floor(self.animation_loop)]
                self.animation_loop += ANIMATION_ITERATION
                if self.animation_loop > 3:
                    self.animation_loop = 1 

class Master_blacksmith(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer =  ENEMY_LAYER
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font('fonts/JetBrainsMono-Regular.ttf', 22)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.x_change = 0
        self.y_change = 0

        self.open_menu = False
        self.no_coins = False

        self.image = pygame.transform.scale(self.game.blacksmith_spritesheet.get_sprite(0, 0, 16, 16), (64, 64)).convert_alpha()
        self.image.set_colorkey(WHITE)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.axe_image = pygame.transform.scale(AXE_FULL, (64, 64))
        self.axe_rect = self.axe_image.get_rect()
        self.sword_image = pygame.transform.scale(SWORD_FULL, (25, 64))
        self.sword_rect = self.sword_image.get_rect()
        self.lance_image = LANCE_FULL
        self.lance_rect = self.lance_image.get_rect()
        self.rapier_image = pygame.transform.scale(RAPIER_FULL, (42, 64))
        self.rapier_rect = self.rapier_image.get_rect()
        self.sai_image = pygame.transform.scale(SAI_FULL, (33, 64))
        self.sai_rect = self.sai_image.get_rect()

        self.coin_image = pygame.transform.scale(self.game.coin_spritesheet.get_sprite(0, 0, 10, 10, BLACK), (60, 60)).convert_alpha()
        self.coin_rect = self.coin_image.get_rect()

    def display(self):
        display_rect_x = WIDTH//2 - 350
        display_rect_y = HEIGHT//2 - 350

        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_pressed = pygame.mouse.get_pressed()
        self.button = Button(self.rect.x, self.rect.y, 64, 64, WHITE, WHITE, '', 12, WHITE)

        display_rect = pygame.Rect(display_rect_x, display_rect_y, 700, 700)
        coin_text = self.font.render('5', True, BLACK)
        coin_text_rect = coin_text.get_rect()
        self.axe_text = self.font.render('Axe', True, BLACK)
        self.axe_text_rect = self.axe_text.get_rect()
        self.sword_text = self.font.render('Sword', True, BLACK)
        self.sword_text_rect = self.sword_text.get_rect()
        self.lance_text = self.font.render('Lance', True, BLACK)
        self.lance_text_rect = self.lance_text.get_rect()
        self.rapier_text = self.font.render('Rapier', True, BLACK)
        self.rapier_text_rect = self.rapier_text.get_rect()
        self.sai_text = self.font.render('Sai', True, BLACK)
        self.sai_text_rect = self.sai_text.get_rect()

        if self.button.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.open_menu = True

        if self.open_menu:
            pygame.draw.rect(self.display_surface, WHITE, display_rect)
            self.quit_button = Button(display_rect_x+710, display_rect_y, 64, 64, BLACK, RED, "QUIT", 20)
            self.display_surface.blit(self.quit_button.image, self.quit_button.rect)

            text = self.font.render("Master Blacksmith: ", True, BLACK)
            text_rect = text.get_rect()
            text2 = self.font.render("You can trade coins for my weapons", True, BLACK)
            text2_rect = text2.get_rect()
            text3 = self.font.render('You can get coins from chests and by killing enemies', True, BLACK)
            text3_rect = text2.get_rect()
            text_rect.x = display_rect_x + 10
            text_rect.y = display_rect_y + 530
            text2_rect.x = display_rect_x + 10
            text2_rect.y = display_rect_y + 560
            text3_rect.x = display_rect_x + 10
            text3_rect.y = display_rect_y + 590

            self.coin_rect.x = display_rect_x + 20
            self.coin_rect.y = display_rect_y + 15
            coin_text_rect.x = self.coin_rect.x + 60
            coin_text_rect.y = self.coin_rect.y + 60
            self.display_surface.blit(self.coin_image, self.coin_rect)
            self.display_surface.blit(coin_text, coin_text_rect)
            self.coin_rect.y = display_rect_y + 115
            coin_text_rect.y = self.coin_rect.y + 60
            self.display_surface.blit(self.coin_image, self.coin_rect)
            self.display_surface.blit(coin_text, coin_text_rect)
            self.coin_rect.y = display_rect_y + 215
            coin_text_rect.y = self.coin_rect.y + 60
            self.display_surface.blit(self.coin_image, self.coin_rect)
            self.display_surface.blit(coin_text, coin_text_rect)
            self.coin_rect.y = display_rect_y + 315
            coin_text_rect.y = self.coin_rect.y + 60
            self.display_surface.blit(self.coin_image, self.coin_rect)
            self.display_surface.blit(coin_text, coin_text_rect)
            self.coin_rect.y = display_rect_y + 415
            coin_text_rect.y = self.coin_rect.y + 60
            self.display_surface.blit(self.coin_image, self.coin_rect)
            self.display_surface.blit(coin_text, coin_text_rect)

            self.axe_rect.x = display_rect_x + 165
            self.axe_rect.y = display_rect_y + 15
            self.sword_rect.x = display_rect_x + 183
            self.sword_rect.y = display_rect_y + 115
            self.lance_rect.x = display_rect_x + 189
            self.lance_rect.y = display_rect_y + 215
            self.rapier_rect.x = display_rect_x + 183
            self.rapier_rect.y = display_rect_y + 315
            self.sai_rect.x = display_rect_x + 190
            self.sai_rect.y = display_rect_y + 415

            self.axe_text_rect.x = display_rect_x + 300
            self.axe_text_rect.y = display_rect_y + 30
            self.sword_text_rect.x = display_rect_x + 300
            self.sword_text_rect.y = display_rect_y + 130
            self.lance_text_rect.x = display_rect_x + 300
            self.lance_text_rect.y = display_rect_y + 230
            self.rapier_text_rect.x = display_rect_x + 300
            self.rapier_text_rect.y = display_rect_y + 330
            self.sai_text_rect.x = display_rect_x + 300
            self.sai_text_rect.y = display_rect_y + 430

            button1 = Button(display_rect_x + 465, display_rect_y + 15, 100, 64, WHITE, BLACK, "BUY", 25)
            button2 = Button(display_rect_x + 465, display_rect_y + 115, 100, 64, WHITE, BLACK, "BUY", 25)
            button3 = Button(display_rect_x + 465, display_rect_y + 215, 100, 64, WHITE, BLACK, "BUY", 25)
            button4 = Button(display_rect_x + 465, display_rect_y + 315, 100, 64, WHITE, BLACK, "BUY", 25)
            button5 = Button(display_rect_x + 465, display_rect_y + 415, 100, 64, WHITE, BLACK, "BUY", 25)

            self.display_surface.blit(self.axe_image, self.axe_rect)
            self.display_surface.blit(self.sword_image, self.sword_rect)
            self.display_surface.blit(self.lance_image, self.lance_rect)
            self.display_surface.blit(self.rapier_image, self.rapier_rect)
            self.display_surface.blit(self.sai_image, self.sai_rect)

            self.display_surface.blit(self.axe_text, self.axe_text_rect)
            self.display_surface.blit(self.sword_text, self.sword_text_rect)
            self.display_surface.blit(self.lance_text, self.lance_text_rect)
            self.display_surface.blit(self.rapier_text, self.rapier_text_rect)
            self.display_surface.blit(self.sai_text, self.sai_text_rect)

            self.display_surface.blit(button1.image, button1.rect)
            self.display_surface.blit(button2.image, button2.rect)
            self.display_surface.blit(button3.image, button3.rect)
            self.display_surface.blit(button4.image, button4.rect)
            self.display_surface.blit(button5.image, button5.rect)

            self.display_surface.blit(text, text_rect)
            self.display_surface.blit(text2, text2_rect)
            self.display_surface.blit(text3, text3_rect)

            if self.game.player.coin_count >= 5:
                if button1.is_pressed(self.mouse_pos, self.mouse_pressed):
                    self.game.player.coin_count -= 5
                    for m, row in enumerate(self.game.inventory.storage_count):
                        for n, i in enumerate(row):
                            if i == 0:
                                self.game.inventory.inventory_storage[m][n] = 12
                                self.game.inventory.storage_count[m][n] = 1
                                break
                            break
                        break
                if button2.is_pressed(self.mouse_pos, self.mouse_pressed):
                    self.game.player.coin_count -= 5
                    for m, row in enumerate(self.game.inventory.storage_count):
                        for n, i in enumerate(row):
                            if i == 0:
                                self.game.inventory.inventory_storage[m][n] = 11
                                self.game.inventory.storage_count[m][n] = 1
                                break
                            break
                        break
                if button3.is_pressed(self.mouse_pos, self.mouse_pressed):
                    self.game.player.coin_count -= 5
                    for m, row in enumerate(self.game.inventory.storage_count):
                        for n, i in enumerate(row):
                            if i == 0:
                                self.game.inventory.inventory_storage[m][n] = 13
                                self.game.inventory.storage_count[m][n] = 1
                                break
                            break
                        break
                if button4.is_pressed(self.mouse_pos, self.mouse_pressed):
                    self.game.player.coin_count -= 5
                    for m, row in enumerate(self.game.inventory.storage_count):
                        for n, i in enumerate(row):
                            if i == 0:
                                self.game.inventory.inventory_storage[m][n] = 14
                                self.game.inventory.storage_count[m][n] = 1
                                break
                            break
                        break
                if button5.is_pressed(self.mouse_pos, self.mouse_pressed):
                    self.game.player.coin_count -= 5
                    for m, row in enumerate(self.game.inventory.storage_count):
                        for n, i in enumerate(row):
                            if i == 0:
                                self.game.inventory.inventory_storage[m][n] = 15
                                self.game.inventory.storage_count[m][n] = 1
                                break
                            break
                        break

        if self.open_menu and self.quit_button.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.open_menu = False

class Cook(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer =  ENEMY_LAYER
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font('fonts/JetBrainsMono-Regular.ttf', 22)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.x_change = 0
        self.y_change = 0

        self.open_menu = False

        self.image = pygame.transform.scale(self.game.cook_spritesheet.get_sprite(0, 0, 16, 16), (64, 64)).convert_alpha()
        self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.beef_image = pygame.transform.scale(BEEF_IMAGE, (60, 60))
        self.beef_rect = self.beef_image.get_rect()
        self.calamari_image = pygame.transform.scale(CALAMARI_IMAGE, (60, 60))
        self.calamari_rect = self.calamari_image.get_rect()
        self.fish_image = pygame.transform.scale(FISH_IMAGE, (60, 60))
        self.fish_rect = self.fish_image.get_rect()
        self.honey_image = pygame.transform.scale(HONEY_IMAGE, (60, 60))
        self.honey_rect = self.honey_image.get_rect()
        self.noodle_image = pygame.transform.scale(NOODLE_IMAGE, (60, 60))
        self.noodle_rect = self.noodle_image.get_rect()
        self.shrimp_image = pygame.transform.scale(SHRIMP_IMAGE, (60, 60))
        self.shrimp_rect = self.shrimp_image.get_rect()
        self.sushi_image = pygame.transform.scale(SUSHI_IMAGE, (60, 60))
        self.sushi_rect = self.sushi_image.get_rect()
        self.sushi_image_2 = pygame.transform.scale(SUSHI_IMAGE_2, (60, 60))
        self.sushi_rect_2 = self.sushi_image_2.get_rect()
        self.yakitori_image = pygame.transform.scale(YAKITORI_IMAGE, (60, 60))
        self.yakitori_rect = self.yakitori_image.get_rect()

        self.coin_image = pygame.transform.scale(self.game.coin_spritesheet.get_sprite(0, 0, 10, 10, BLACK).convert_alpha(), (60, 60))
        self.coin_rect = self.coin_image.get_rect()
        self.coin_list = [5, 7, 6, 6, 5, 8, 4, 4, 9]

    def display(self):
        display_rect_x = WIDTH//2 - 350
        display_rect_y = HEIGHT//2 - 350

        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_pressed = pygame.mouse.get_pressed()
        self.button = Button(self.rect.x, self.rect.y, 64, 64, WHITE, WHITE, '', 12, WHITE)

        display_rect = pygame.Rect(display_rect_x, display_rect_y, 700, 700)

        self.beef_text = self.font.render('Beef', True, BLACK)
        self.beef_text_rect = self.beef_text.get_rect()
        self.calamari_text = self.font.render('Calamari', True, BLACK)
        self.calamari_text_rect = self.calamari_text.get_rect()
        self.fish_text = self.font.render('Fish', True, BLACK)
        self.fish_text_rect = self.fish_text.get_rect()
        self.honey_text = self.font.render('Honey', True, BLACK)
        self.honey_text_rect = self.honey_text.get_rect()
        self.noodle_text = self.font.render('Noodle', True, BLACK)
        self.noodle_text_rect = self.noodle_text.get_rect()
        self.shrimp_text = self.font.render('Shrimp', True, BLACK)
        self.shrimp_text_rect = self.shrimp_text.get_rect()
        self.sushi_text = self.font.render('Sushi', True, BLACK)
        self.sushi_text_rect = self.sushi_text.get_rect()
        self.sushi_text_2 = self.font.render('Sushi', True, BLACK)
        self.sushi_text_rect_2 = self.sushi_text_2.get_rect()
        self.yakitori_text = self.font.render('Yakitori', True, BLACK)
        self.yakitori_text_rect = self.yakitori_text.get_rect()

        if self.button.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.open_menu = True

        if self.open_menu:
            pygame.draw.rect(self.display_surface, WHITE, display_rect)
            self.quit_button = Button(display_rect_x+710, display_rect_y, 64, 64, BLACK, RED, "QUIT", 20)
            self.display_surface.blit(self.quit_button.image, self.quit_button.rect)

            for i in range(9):
                self.coin_rect.x = display_rect_x + 20
                self.coin_rect.y = display_rect_y + 15 + i*70
                self.display_surface.blit(self.coin_image, self.coin_rect)
                coin_text = self.font.render(str(self.coin_list[i]), True, BLACK)
                coin_text_rect = coin_text.get_rect()
                coin_text_rect.x = self.coin_rect.x + 60
                coin_text_rect.y = self.coin_rect.y + 50
                self.display_surface.blit(coin_text, coin_text_rect)

            self.beef_rect.x = display_rect_x + 165
            self.beef_rect.y = display_rect_y + 15 
            self.calamari_rect.x = display_rect_x + 165
            self.calamari_rect.y = display_rect_y + 85 
            self.fish_rect.x = display_rect_x + 165
            self.fish_rect.y = display_rect_y + 155 
            self.honey_rect.x = display_rect_x + 165
            self.honey_rect.y = display_rect_y + 225 
            self.noodle_rect.x = display_rect_x + 165
            self.noodle_rect.y = display_rect_y + 295 
            self.shrimp_rect.x = display_rect_x + 165
            self.shrimp_rect.y = display_rect_y + 365 
            self.sushi_rect.x = display_rect_x + 165
            self.sushi_rect.y = display_rect_y + 435 
            self.sushi_rect_2.x = display_rect_x + 165
            self.sushi_rect_2.y = display_rect_y + 505 
            self.yakitori_rect.x = display_rect_x + 165
            self.yakitori_rect.y = display_rect_y + 575 

            self.beef_text_rect.x = display_rect_x + 300
            self.beef_text_rect.y = display_rect_y + 30
            self.calamari_text_rect.x = display_rect_x + 300
            self.calamari_text_rect.y = display_rect_y + 100
            self.fish_text_rect.x = display_rect_x + 300
            self.fish_text_rect.y = display_rect_y + 170
            self.honey_text_rect.x = display_rect_x + 300
            self.honey_text_rect.y = display_rect_y + 240
            self.noodle_text_rect.x = display_rect_x + 300
            self.noodle_text_rect.y = display_rect_y + 310
            self.shrimp_text_rect.x = display_rect_x + 300
            self.shrimp_text_rect.y = display_rect_y + 380
            self.sushi_text_rect.x = display_rect_x + 300
            self.sushi_text_rect.y = display_rect_y + 450
            self.sushi_text_rect_2.x = display_rect_x + 300
            self.sushi_text_rect_2.y = display_rect_y + 520
            self.yakitori_text_rect.x = display_rect_x + 300
            self.yakitori_text_rect.y = display_rect_y + 590

            button1 = Button(display_rect_x + 465, display_rect_y + 15, 100, 60, WHITE, BLACK, "BUY", 25)
            button2 = Button(display_rect_x + 465, display_rect_y + 85, 100, 60, WHITE, BLACK, "BUY", 25)
            button3 = Button(display_rect_x + 465, display_rect_y + 155, 100, 60, WHITE, BLACK, "BUY", 25)
            button4 = Button(display_rect_x + 465, display_rect_y + 225, 100, 60, WHITE, BLACK, "BUY", 25)
            button5 = Button(display_rect_x + 465, display_rect_y + 295, 100, 60, WHITE, BLACK, "BUY", 25)
            button6 = Button(display_rect_x + 465, display_rect_y + 365, 100, 60, WHITE, BLACK, "BUY", 25)
            button7 = Button(display_rect_x + 465, display_rect_y + 435, 100, 60, WHITE, BLACK, "BUY", 25)
            button8 = Button(display_rect_x + 465, display_rect_y + 505, 100, 60, WHITE, BLACK, "BUY", 25)
            button9 = Button(display_rect_x + 465, display_rect_y + 575, 100, 60, WHITE, BLACK, "BUY", 25)

            self.display_surface.blit(self.beef_image, self.beef_rect)
            self.display_surface.blit(self.calamari_image, self.calamari_rect)
            self.display_surface.blit(self.fish_image, self.fish_rect)
            self.display_surface.blit(self.honey_image, self.honey_rect)
            self.display_surface.blit(self.noodle_image, self.noodle_rect)
            self.display_surface.blit(self.shrimp_image, self.shrimp_rect)
            self.display_surface.blit(self.sushi_image, self.sushi_rect)
            self.display_surface.blit(self.sushi_image_2, self.sushi_rect_2)
            self.display_surface.blit(self.yakitori_image, self.yakitori_rect)

            self.display_surface.blit(self.beef_text, self.beef_text_rect)
            self.display_surface.blit(self.calamari_text, self.calamari_text_rect)
            self.display_surface.blit(self.fish_text, self.fish_text_rect)
            self.display_surface.blit(self.honey_text, self.honey_text_rect)
            self.display_surface.blit(self.noodle_text, self.noodle_text_rect)
            self.display_surface.blit(self.shrimp_text, self.shrimp_text_rect)
            self.display_surface.blit(self.sushi_text, self.sushi_text_rect)
            self.display_surface.blit(self.sushi_text_2, self.sushi_text_rect_2)
            self.display_surface.blit(self.yakitori_text, self.yakitori_text_rect)

            self.display_surface.blit(button1.image, button1.rect)
            self.display_surface.blit(button2.image, button2.rect)
            self.display_surface.blit(button3.image, button3.rect)
            self.display_surface.blit(button4.image, button4.rect)
            self.display_surface.blit(button5.image, button5.rect)
            self.display_surface.blit(button6.image, button6.rect)
            self.display_surface.blit(button7.image, button7.rect)
            self.display_surface.blit(button8.image, button8.rect)
            self.display_surface.blit(button9.image, button9.rect)

            if button1.is_pressed(self.mouse_pos, self.mouse_pressed):
                if self.game.player.coin_count >= 5:
                    self.game.player.coin_count -= 5
                    for m, row in enumerate(self.game.inventory.storage_count):
                        for n, i in enumerate(row):
                            if i == 0:
                                self.game.inventory.inventory_storage[m][n] = 1
                                self.game.inventory.storage_count[m][n] = 1
                                break
                            break
                        break
            if button2.is_pressed(self.mouse_pos, self.mouse_pressed): #7
                if self.game.player.coin_count >= 7:
                    self.game.player.coin_count -= 7
                    for m, row in enumerate(self.game.inventory.storage_count):
                        for n, i in enumerate(row):
                            if i == 0:
                                self.game.inventory.inventory_storage[m][n] = 2
                                self.game.inventory.storage_count[m][n] = 1
                                break
                            break
                        break
            if button3.is_pressed(self.mouse_pos, self.mouse_pressed):#6
                if self.game.player.coin_count >= 6:
                    self.game.player.coin_count -= 6
                    for m, row in enumerate(self.game.inventory.storage_count):
                        for n, i in enumerate(row):
                            if i == 0:
                                self.game.inventory.inventory_storage[m][n] = 3
                                self.game.inventory.storage_count[m][n] = 1
                                break
                            break
                        break
            if button4.is_pressed(self.mouse_pos, self.mouse_pressed):#6
                if self.game.player.coin_count >= 6:
                    self.game.player.coin_count -= 6
                    for m, row in enumerate(self.game.inventory.storage_count):
                        for n, i in enumerate(row):
                            if i == 0:
                                self.game.inventory.inventory_storage[m][n] = 4
                                self.game.inventory.storage_count[m][n] = 1
                                break
                            break
                        break
            if button5.is_pressed(self.mouse_pos, self.mouse_pressed):#5
                if self.game.player.coin_count >= 5:
                    self.game.player.coin_count -= 5
                    for m, row in enumerate(self.game.inventory.storage_count):
                        for n, i in enumerate(row):
                            if i == 0:
                                self.game.inventory.inventory_storage[m][n] = 5
                                self.game.inventory.storage_count[m][n] = 1
                                break
                            break
                        break
            if button6.is_pressed(self.mouse_pos, self.mouse_pressed): #8
                if self.game.player.coin_count >= 8:
                    self.game.player.coin_count -= 8
                    for m, row in enumerate(self.game.inventory.storage_count):
                        for n, i in enumerate(row):
                            if i == 0:
                                self.game.inventory.inventory_storage[m][n] = 6
                                self.game.inventory.storage_count[m][n] = 1
                                break
                            break
                        break
            if button7.is_pressed(self.mouse_pos, self.mouse_pressed):#4
                if self.game.player.coin_count >= 4:
                    self.game.player.coin_count -= 4
                    for m, row in enumerate(self.game.inventory.storage_count):
                        for n, i in enumerate(row):
                            if i == 0:
                                self.game.inventory.inventory_storage[m][n] = 7
                                self.game.inventory.storage_count[m][n] = 1
                                break
                            break
                        break
            if button8.is_pressed(self.mouse_pos, self.mouse_pressed):#4
                if self.game.player.coin_count >= 4:
                    self.game.player.coin_count -= 4
                    for m, row in enumerate(self.game.inventory.storage_count):
                        for n, i in enumerate(row):
                            if i == 0:
                                self.game.inventory.inventory_storage[m][n] = 8
                                self.game.inventory.storage_count[m][n] = 1
                                break
                            break
                        break
            if button9.is_pressed(self.mouse_pos, self.mouse_pressed):#9
                if self.game.player.coin_count >= 9:
                    self.game.player.coin_count -= 9
                    for m, row in enumerate(self.game.inventory.storage_count):
                        for n, i in enumerate(row):
                            if i == 0:
                                self.game.inventory.inventory_storage[m][n] = 9
                                self.game.inventory.storage_count[m][n] = 1
                                break
                            break
                        break

        if self.open_menu and self.quit_button.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.open_menu = False

class Potion_Maker(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer =  ENEMY_LAYER
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font('fonts/JetBrainsMono-Regular.ttf', 22)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.x_change = 0
        self.y_change = 0

        self.open_menu = False

        self.image = pygame.transform.scale(self.game.potion_maker_spritesheet_2.get_sprite(0, 0, 16, 16), (64, 64)).convert_alpha()
        self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.health_drink_image = pygame.transform.scale(self.game.house_spritesheet.get_sprite(336, 192, 16, 16, BLACK).convert_alpha(), (60, 60))
        self.health_drink_rect = self.health_drink_image.get_rect()
        self.poison_drink_image = pygame.transform.scale(self.game.house_spritesheet.get_sprite(336, 208, 16, 16, BLACK).convert_alpha(), (60, 60))
        self.poison_drink_rect = self.poison_drink_image.get_rect()
        self.lettuce_juice_image = pygame.transform.scale(self.game.house_spritesheet.get_sprite(336, 224, 16, 16, BLACK).convert_alpha(), (60, 60))
        self.lettuce_juice_rect = self.lettuce_juice_image.get_rect()
        self.empty_bottle_image = pygame.transform.scale(self.game.house_spritesheet.get_sprite(336, 240, 16, 16, BLACK).convert_alpha(), (60, 60))
        self.empty_bottle_rect = self.empty_bottle_image.get_rect()

        self.coin_image = pygame.transform.scale(self.game.coin_spritesheet.get_sprite(0, 0, 10, 10, BLACK).convert_alpha(), (60, 60))
        self.coin_rect = self.coin_image.get_rect()
        self.coin_list = [10, 2, 8]

    def display(self):
        display_rect_x = WIDTH//2 - 350
        display_rect_y = HEIGHT//2 - 350

        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_pressed = pygame.mouse.get_pressed()
        self.button = Button(self.rect.x, self.rect.y, 64, 64, WHITE, WHITE, '', 12, WHITE)

        display_rect = pygame.Rect(display_rect_x, display_rect_y, 700, 700)

        self.health_drink_text = self.font.render('Health potion', True, BLACK)
        self.health_drink_text_rect = self.health_drink_text.get_rect()
        self.poison_drink_text = self.font.render('Poison potion', True, BLACK)
        self.poison_drink_text_rect = self.poison_drink_text.get_rect()
        self.lettuce_juice_text = self.font.render('Lettuce juice', True, BLACK)
        self.lettuce_juice_text_rect = self.lettuce_juice_text.get_rect()

        if self.button.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.open_menu = True

        if self.open_menu:
            pygame.draw.rect(self.display_surface, WHITE, display_rect)
            self.quit_button = Button(display_rect_x+710, display_rect_y, 64, 64, BLACK, RED, "QUIT", 20)
            self.display_surface.blit(self.quit_button.image, self.quit_button.rect)

            for i in range(3):
                self.coin_rect.x = display_rect_x + 20
                self.coin_rect.y = display_rect_y + 15 + i*100
                self.display_surface.blit(self.coin_image, self.coin_rect)
                coin_text = self.font.render(str(self.coin_list[i]), True, BLACK)
                coin_text_rect = coin_text.get_rect()
                coin_text_rect.x = self.coin_rect.x + 60
                coin_text_rect.y = self.coin_rect.y + 60
                self.display_surface.blit(coin_text, coin_text_rect)

            self.health_drink_rect.x = display_rect_x + 165
            self.health_drink_rect.y = display_rect_y + 15
            self.poison_drink_rect.x = display_rect_x + 165
            self.poison_drink_rect.y = display_rect_y + 115
            self.lettuce_juice_rect.x = display_rect_x + 165
            self.lettuce_juice_rect.y = display_rect_y + 215

            self.health_drink_text_rect.x = display_rect_x + 250
            self.health_drink_text_rect.y = display_rect_y + 30
            self.poison_drink_text_rect.x = display_rect_x + 250
            self.poison_drink_text_rect.y = display_rect_y + 130
            self.lettuce_juice_text_rect.x = display_rect_x + 250
            self.lettuce_juice_text_rect.y = display_rect_y + 230

            button1 = Button(display_rect_x + 465, display_rect_y + 15, 100, 64, WHITE, BLACK, "BUY", 25)
            button2 = Button(display_rect_x + 465, display_rect_y + 115, 100, 64, WHITE, BLACK, "BUY", 25)
            button3 = Button(display_rect_x + 465, display_rect_y + 215, 100, 64, WHITE, BLACK, "BUY", 25)

            self.display_surface.blit(self.health_drink_image, self.health_drink_rect)
            self.display_surface.blit(self.poison_drink_image, self.poison_drink_rect)
            self.display_surface.blit(self.lettuce_juice_image, self.lettuce_juice_rect)

            self.display_surface.blit(self.health_drink_text, self.health_drink_text_rect)
            self.display_surface.blit(self.poison_drink_text, self.poison_drink_text_rect)
            self.display_surface.blit(self.lettuce_juice_text, self.lettuce_juice_text_rect)

            self.display_surface.blit(button1.image, button1.rect)
            self.display_surface.blit(button2.image, button2.rect)
            self.display_surface.blit(button3.image, button3.rect)

            if button1.is_pressed(self.mouse_pos, self.mouse_pressed):
                if self.game.player.coin_count >= 10:
                    self.game.player.coin_count -= 10
                    for m, row in enumerate(self.game.inventory.storage_count):
                        for n, i in enumerate(row):
                            if i == 0:
                                self.game.inventory.inventory_storage[m][n] = 17
                                self.game.inventory.storage_count[m][n] = 1
                                break
                            break
                        break
            if button2.is_pressed(self.mouse_pos, self.mouse_pressed):
                if self.game.player.coin_count >= 2:
                    self.game.player.coin_count -= 2
                    for m, row in enumerate(self.game.inventory.storage_count):
                        for n, i in enumerate(row):
                            if i == 0:
                                self.game.inventory.inventory_storage[m][n] = 18
                                self.game.inventory.storage_count[m][n] = 1
                                break
                            break
                        break
            if button3.is_pressed(self.mouse_pos, self.mouse_pressed):
                if self.game.player.coin_count >= 8:
                    self.game.player.coin_count -= 8
                    for m, row in enumerate(self.game.inventory.storage_count):
                        for n, i in enumerate(row):
                            if i == 0:
                                self.game.inventory.inventory_storage[m][n] = 19
                                self.game.inventory.storage_count[m][n] = 1
                                break
                            break
                        break

        if self.open_menu and self.quit_button.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.open_menu = False

class Block(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = BLOCK_LAYER
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.image = self.game.terrain_spritesheet.get_sprite(0, 192, 32, 32).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

class Tree(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = BLOCK_LAYER
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.image_list = [self.game.terrain_spritesheet.get_sprite(0, 0, 32, 32, BLACK).convert_alpha(), 
                        self.game.terrain_spritesheet.get_sprite(32, 0, 32, 32, BLACK).convert_alpha(),
                        self.game.terrain_spritesheet.get_sprite(32*3, 0, 32, 32, BLACK).convert_alpha()]

        self.image = random.choice(self.image_list)
        self.image = pygame.transform.scale(self.image, (TILESIZE_LARGE, TILESIZE_LARGE))

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

class ForestTree(pygame.sprite.Sprite):
    def __init__(self, game, x, y, layer = FOREST_LAYER_1):
        self.game = game
        self._layer = layer
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.image = self.game.terrain_spritesheet.get_sprite(0, 32, 64, 47, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (256, 192))

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

class PineTree(pygame.sprite.Sprite):
    def __init__(self, game, x, y, layer = FOREST_LAYER_2):
        self.game = game
        self._layer = layer
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.image = self.game.terrain_spritesheet.get_sprite(32, 0, 32, 32, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE_LARGE, TILESIZE_LARGE))

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

class Ground(pygame.sprite.Sprite):
    def __init__(self, game):
        self.game = game
        self._layer = GROUND_LAYER
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.width = TILESIZE
        self.height = TILESIZE

    def grass_ground(self, x, y):
        self.image_list = [self.game.floor_spritesheet.get_sprite(0, 192, 16, 16), self.game.floor_spritesheet.get_sprite(16, 192, 16, 16).convert_alpha(),
                           self.game.floor_spritesheet.get_sprite(32, 192, 16, 16), self.game.floor_spritesheet.get_sprite(48, 192, 16, 16).convert_alpha(),
                           self.game.floor_spritesheet.get_sprite(64, 192, 16, 16), self.game.floor_spritesheet.get_sprite(0, 192, 16, 16).convert_alpha(),
                           self.game.floor_spritesheet.get_sprite(0, 192, 16, 16),self.game.floor_spritesheet.get_sprite(0, 192, 16, 16).convert_alpha(),
                           self.game.floor_spritesheet.get_sprite(0, 192, 16, 16),self.game.floor_spritesheet.get_sprite(0, 192, 16, 16).convert_alpha(),
                           self.game.floor_spritesheet.get_sprite(0, 192, 16, 16),self.game.floor_spritesheet.get_sprite(0, 192, 16, 16).convert_alpha()]
        self.image = random.choice(self.image_list)
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def dirt_ground(self, x, y):
        self.image_list = [self.game.floor_spritesheet.get_sprite(0, 80, 16, 16), self.game.floor_spritesheet.get_sprite(16, 80, 16, 16).convert_alpha(),
                           self.game.floor_spritesheet.get_sprite(32, 80, 16, 16), self.game.floor_spritesheet.get_sprite(48, 80, 16, 16).convert_alpha(),
                           self.game.floor_spritesheet.get_sprite(64, 80, 16, 16), self.game.floor_spritesheet.get_sprite(0, 80, 16, 16).convert_alpha(),
                           self.game.floor_spritesheet.get_sprite(0, 80, 16, 16),self.game.floor_spritesheet.get_sprite(0, 80, 16, 16).convert_alpha(),
                           self.game.floor_spritesheet.get_sprite(0, 80, 16, 16),self.game.floor_spritesheet.get_sprite(0, 80, 16, 16).convert_alpha(),
                           self.game.floor_spritesheet.get_sprite(0, 80, 16, 16),self.game.floor_spritesheet.get_sprite(0, 80, 16, 16).convert_alpha()]
        self.image = random.choice(self.image_list)
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def dirt_path(self, x, y):
        self.image = self.game.floor_spritesheet.get_sprite(16, 16, 16, 16).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def flower_bush(self, x, y):
        self.image = self.game.terrain_spritesheet.get_sprite(80, 176, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

class Fence(pygame.sprite.Sprite):
    def __init__(self, game):
        self.game = game
        self._layer = BLOCK_LAYER
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)

    def fence_horizontal(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(160, 160, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (64, 64))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def fence_vertical(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(208, 176, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (64, 64))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def stone_wall_horizontal(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(176, 128, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (64, 64))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def stone_wall_vertical(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(176, 144, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (64, 64))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

class Light_Brick_Road(pygame.sprite.Sprite):
    def __init__(self, game):
        self.game = game
        self._layer = GROUND_LAYER + 1
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

    def road_plain(self, x, y):
        self.image = self.game.path_spritesheet.get_sprite(16, 16, 16, 16).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def road_upper_border(self, x, y):
        self.image = self.game.path_spritesheet.get_sprite(16, 0, 16, 16).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def road_lower_border(self, x, y):
        self.image = self.game.path_spritesheet.get_sprite(16, 32, 16, 16).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def road_left_border(self, x, y):
        self.image = self.game.path_spritesheet.get_sprite(0, 16, 16, 16).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def road_right_border(self, x, y):
        self.image = self.game.path_spritesheet.get_sprite(32, 16, 16, 16).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def road_left_up_border(self, x, y):
        self.image = self.game.path_spritesheet.get_sprite(0, 0, 16, 16).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def road_left_down_border(self, x, y):
        self.image = self.game.path_spritesheet.get_sprite(0, 32, 16, 16).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def road_right_up_border(self, x, y):
        self.image = self.game.path_spritesheet.get_sprite(32, 0, 16, 16).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def road_right_down_border(self, x, y):
        self.image = self.game.path_spritesheet.get_sprite(32, 32, 16, 16).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def road_left_down_corner(self, x, y):
        self.image = self.game.path_spritesheet.get_sprite(96, 16, 16, 16).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def road_left_up_corner(self, x, y):
        self.image = self.game.path_spritesheet.get_sprite(96, 32, 16, 16).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def road_right_down_corner(self, x, y):
        self.image = self.game.path_spritesheet.get_sprite(80, 16, 16, 16).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def road_right_up_corner(self, x, y):
        self.image = self.game.path_spritesheet.get_sprite(80, 32, 16, 16).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

class Stairs(pygame.sprite.Sprite):
    def __init__(self, game):
        self.game = game
        self._layer = GROUND_LAYER + 2
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

    def stone_stairs_small(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(144, 240, 16, 48, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (64, 192))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def stone_stairs_large(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(160, 240, 48, 48, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (192*2, 192*2))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def deepslate_stairs_small(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(144, 304, 16, 48, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (64, 192))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def deepslate_stairs_large(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(160, 304, 48, 48, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (192, 192))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

class Buildings(pygame.sprite.Sprite):
    def __init__(self, game):
        self.game = game
        self._layer = BLOCK_LAYER
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)

    def render(self, image):
        return pygame.transform.scale(image, (256, 192))
    def render_big(self, image):
        return pygame.transform.scale(image, (256, 256))
    def render_v_big(self, image):
        return pygame.transform.scale(image, (256, 320))
    def render_large(self, image):
        return pygame.transform.scale(image, (256, 512))

    def house1(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(0, 0, 64, 48, BLACK).convert_alpha()
        self.image = self.render(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def house2(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(64, 0, 64, 48, BLACK).convert_alpha()
        self.image = self.render(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def house3(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(128, 0, 64, 48, BLACK).convert_alpha()
        self.image = self.render(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def house4(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(192, 0, 64, 48, BLACK).convert_alpha()
        self.image = self.render(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def mini_house(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(416, 0, 48, 48, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (192, 192))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def food_shop(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(256, 0, 48, 48, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (192, 192))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def armory(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(304, 0, 64, 48, BLACK).convert_alpha()
        self.image = self.render(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def garrison(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(368, 0, 48, 48, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (192, 192))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def lumber_camp(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(256, 48, 48, 48, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (192, 192))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def military_watchtower(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(256, 96, 48, 80, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (192, 320))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def military_camp(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(0, 120, 48, 40, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (288, 240))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def post_office(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(464, 0, 64, 64, BLACK).convert_alpha()
        self.image = self.render_big(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def mill(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(464, 64, 48, 64, BLACK).convert_alpha()
        self.image = self.render_v_big(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def warehouse(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(400, 224, 64, 80, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (256, 320))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def stone_statue(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(16, 240, 32, 48, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (128, 192))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def stone_budda(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(80, 240, 32, 32, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (128, 128))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def stone_budda_powered(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(48, 240, 32, 32, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (128, 128))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def stone_woman(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(112, 240, 16, 32, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (64, 128))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def stone_pillar(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(112, 272, 16, 32, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (64, 128))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def stone_ninja(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(80, 272, 32, 32, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (128, 128))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def stone_frog(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(48, 272, 32, 32, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (128, 128))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
    
    def stone_brick(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(32, 288, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (64, 64))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def deepslate_statue(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(16, 304, 32, 48, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (128, 192))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def deepslate_budda(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(80, 304, 32, 32, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (128, 128))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def deepslate_budda_powered(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(48, 304, 32, 32, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (128, 128))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def deepslate_woman(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(112, 304, 16, 32, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (64, 128))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def deepslate_pillar(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(112, 336, 16, 32, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (64, 128))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def deepslate_ninja(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(80, 336, 32, 32, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (128, 128))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def deepslate_frog(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(48, 336, 32, 32, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (128, 128))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
    
    def deepslate_brick(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(32, 352, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (64, 64))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

class Element(pygame.sprite.Sprite):
    def __init__(self, game):
        self.game = game
        self._layer = DOOR_LAYER
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)

    def door1(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(0, 48, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def door2(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(16, 48, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def door3(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(32, 48, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def window1(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(48, 48, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def window2(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(64, 48, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def smokestack(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(112, 48, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def board1(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(64, 64, 32, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE*2, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def board2(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(96, 64, 32, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (128, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def board3(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(0, 64, 32, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (128, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def board4(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(32, 64, 32, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (128, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def woodworking_bench(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(464, 128, 32, 32, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (128, 128))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def handle_workbench(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(496, 240, 32, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (128, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def stove(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(464, 160, 32, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (128, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def cooker(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(496, 128, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
    
    def cooker_and_pan(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(496, 144, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def meat_basket(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(512, 128, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def closed_basket(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(512, 144, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def empty_cauldron(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(512, 160, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def filled_cauldron(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(496, 160, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def empty_open_cooker(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(512, 176, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def filled_open_cooker(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(496, 176, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def furnace(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(464, 176, 32, 32, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (128, 128))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def blast_furnace(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(464, 208, 32, 32, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (128, 128))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def steel_foundry(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(496, 200, 32, 40, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (128, 160))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def anvil(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(464, 240, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE 

    def wood_pile(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(496, 288, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def weapon_stand_1(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(224, 200, 32, 24, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (128, 96))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def weapon_stand_2(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(224, 168, 32, 24, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (128, 96))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def knife_barrel(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(224, 288, 16, 32, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, 128))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def quiver(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(224, 192, 16, 32, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, 128))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def post_box(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(480, 272, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def closed_small_basket(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(288, 176, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def open_small_basket(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(288, 192, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def tomato_small_basket(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(288, 208, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def lettuce_small_basket(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(272, 208, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def fish_small_basket(self, x, y):
        self.image = self.game.house_spritesheet.get_sprite(256, 208, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def chest(self, x, y):
        self.image = self.game.element_spritesheet.get_sprite(0, 0, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def pot(self, x, y):
        self.image = self.game.element_spritesheet.get_sprite(16, 0, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def fence(self, x, y):
        self.image = self.game.element_spritesheet.get_sprite(32, 0, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def red_pot(self, x, y):
        self.image = self.game.element_spritesheet.get_sprite(48, 0, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def inscription_long(self, x, y):
        self.image = self.game.element_spritesheet.get_sprite(80, 32, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def inscription_big(self, x, y):
        self.image = self.game.element_spritesheet.get_sprite(64, 32, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def well(self, x, y):
        self.image = self.game.element_spritesheet.get_sprite(96, 16, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def well_with_bucket(self, x, y):
        self.image = self.game.element_spritesheet.get_sprite(96, 32, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def roofed_well_with_bucket(self, x, y):
        self.image = self.game.element_spritesheet.get_sprite(112, 24, 16, 24, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, 96))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def wheelbarrow(self, x, y):
        self.image = self.game.element_spritesheet.get_sprite(0, 48, 32, 32, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (128, 128))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def wheelbarrow_with_stone(self, x, y):
        self.image = self.game.element_spritesheet.get_sprite(32, 48, 32, 32, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (128, 128))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def paddy_field(self, x, y):
        self.image = self.game.element_spritesheet.get_sprite(208, 64, 48, 48, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (192, 192))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

class Water(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = GROUND_LAYER
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.image_list = [self.game.water_spritesheet.get_sprite(176, 32, 16, 16).convert_alpha(), self.game.water_spritesheet.get_sprite(16, 16, 8, 8).convert_alpha(),
                    self.game.water_spritesheet.get_sprite(16, 16, 8, 8).convert_alpha(), self.game.water_spritesheet.get_sprite(16, 16, 8, 8).convert_alpha(),
                    self.game.water_spritesheet.get_sprite(16, 16, 8, 8).convert_alpha(), self.game.water_spritesheet.get_sprite(176, 64, 16, 16).convert_alpha(),
                    self.game.water_spritesheet.get_sprite(176, 16, 16, 16).convert_alpha(), self.game.water_spritesheet.get_sprite(176, 48, 16, 16).convert_alpha()]
        
        self.water_sprite_1 = self.game.water_animation.get_sprite(0, 0, 16, 16).convert_alpha()
        self.water_sprite_2 = self.game.water_animation.get_sprite(16, 0, 16, 16).convert_alpha()
        self.water_sprite_3 = self.game.water_animation.get_sprite(32, 0, 16, 16).convert_alpha()
        self.water_sprite_4 = self.game.water_animation.get_sprite(48, 0, 16, 16).convert_alpha()

        self.animation_list = [pygame.transform.scale(self.water_sprite_1, (64, 64)),
            pygame.transform.scale(self.water_sprite_2, (64, 64)), pygame.transform.scale(self.water_sprite_3, (64, 64)),
            pygame.transform.scale(self.water_sprite_4, (64, 64))]

        self.image = random.choice(self.image_list)
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))

        self.animation_loop = 1

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def animate(self):
        self.image = self.animation_list[math.floor(self.animation_loop)]
        self.image.set_colorkey(BLACK)
        self.animation_loop += ANIMATION_ITERATION
        if self.animation_loop > 4:
            self.animation_loop = 1

class Button:
    def __init__(self, x, y, width,  height, font_color, background_color, content, fontsize, colorkey = None):
        self.font = pygame.font.Font('fonts/JetBrainsMono-Regular.ttf', fontsize)
        self.content = content
        
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.fg = font_color
        self.bg = background_color

        self.image = pygame.Surface((self.width, self.height)).convert_alpha()
        self.image.fill(self.bg)
        self.rect = self.image.get_rect()

        self.rect.x = self.x
        self.rect.y = self.y
        
        self.text = self.font.render(self.content, True, self.fg)
        self.text_rect = self.text.get_rect(center = (self.width/2, self.height/2))
        self.image.blit(self.text, self.text_rect)

        if colorkey != None:
            self.image.set_colorkey(colorkey)

    def is_pressed(self, pos, pressed):
        if self.rect.collidepoint(pos):
            if pressed[0]:
                return True
            return False
        return False

    def is_right_pressed(self, pos, pressed):
        if self.rect.collidepoint(pos):
            if pressed[2]:
                return True
            return False
        return False

    def is_scroll_pressed(self, pos, pressed):
        if self.rect.collidepoint(pos):
            if pressed[1]:
                return True
            return False
        return False

    def is_hovering(self, pos, hover_color):
        if pos[0] in range(self.rect.left, self.rect.right) and pos[1] in range(self.rect.top, self.rect.bottom):
            self.text = self.font.render(self.content, True, hover_color)
            self.image.blit(self.text, self.text_rect)
        else:
            self.text = self.font.render(self.content, True, self.fg)
            self.image.blit(self.text, self.text_rect)

    def is_hovering_bool(self, pos):
        if self.rect.collidepoint(pos):
            return True
        return False

class Attack(pygame.sprite.Sprite):
    def __init__(self, game, x, y, weapon_index):
        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = self.game.all_sprites, self.game.attacks
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.direction = self.game.player.facing
        self.weapon_index = weapon_index

        self.axe_list = [AXE_UP, AXE_DOWN, AXE_LEFT, AXE_RIGHT]
        self.sword_list = [SWORD_UP, SWORD_DOWN, SWORD_LEFT, SWORD_RIGHT]
        self.lance_list = [LANCE_UP, LANCE_DOWN, LANCE_LEFT, LANCE_RIGHT]
        self.rapier_list = [RAPIER_UP, RAPIER_DOWN, RAPIER_LEFT, RAPIER_RIGHT]
        self.sai_list = [SAI_UP, SAI_DOWN, SAI_LEFT, SAI_RIGHT]

        self.x = x
        self.y = y
        self.width = TILESIZE
        self.height = TILESIZE

        self.animation_loop = 0

        if self.weapon_index == 0:
            self.weapon = self.sword_list
        elif self.weapon_index == 1:
            self.weapon = self.axe_list
        elif self.weapon_index == 2:
            self.weapon = self.lance_list
        elif self.weapon_index == 3:
            self.weapon = self.rapier_list
        elif self.weapon_index == 4:
            self.weapon = self.sai_list

        if self.direction == 'up':
            self.image = self.weapon[0]
        if self.direction == 'down':
            self.image = self.weapon[1]
        if self.direction == 'left':
            self.image = self.weapon[2]
        if self.direction == 'right':
            self.image = self.weapon[3]

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def update(self):
        self.animate()
        self.collide()

    def collide(self):
        hits = pygame.sprite.spritecollide(self, self.game.enemies, True)
        if hits:
            self.game.player.exp += 10
            if self.game.player.weapon_index == 0:
                self.game.player.sword_durability -= 1
            if self.game.player.weapon_index == 1:
                self.game.player.axe_durability -= 1
            if self.game.player.weapon_index == 2:
                self.game.player.lance_durability -= 1
            if self.game.player.weapon_index == 3:
                self.game.player.rapier_durability -= 1
            if self.game.player.weapon_index == 4:           
                self.game.player.sai_durability -= 1

    def animate(self):
        if self.direction == 'up':
            self.image = self.weapon[0]
            self.animation_loop += ANIMATION_ITERATION
            if self.animation_loop >= 1:
                self.kill()

        if self.direction == 'down':
            self.image = self.weapon[1]
            self.animation_loop += ANIMATION_ITERATION
            if self.animation_loop >= 1:
                self.kill()

        if self.direction == 'left':
            self.image = self.weapon[2]
            self.animation_loop += ANIMATION_ITERATION
            if self.animation_loop >= 1:
                self.kill()

        if self.direction == 'right':
            self.image = self.weapon[3]
            self.animation_loop += ANIMATION_ITERATION
            if self.animation_loop >= 1:
                self.kill()

class UI:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

        self.health_bar_rect = pygame.Rect(277.5, 660, BAR_WIDTH, BAR_HEIGHT)
        self.food_bar_rect = pygame.Rect(HEIGHT, 660, BAR_WIDTH, BAR_HEIGHT)

        self.coin_image = GOLD_COIN_IMAGE
        self.coin_image = pygame.transform.scale(self.coin_image, (30, 30))
        self.coin_image_rect = self.coin_image.get_rect()
        self.coin_image_rect.x = WIDTH - 45
        self.coin_image_rect.y = 15

    def show_bar(self, current, max_amount, bg_rect, color):
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)

        ratio = current / max_amount
        current_width = bg_rect.width * ratio
        current_rect = bg_rect.copy()
        current_rect.width = current_width

        pygame.draw.rect(self.display_surface, color, current_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)

    def show_exp(self, exp):
        text_surf = self.font.render(str(int(exp)), False, TEXT_COLOR)
        x = 655
        y = 675
        text_rect = text_surf.get_rect(bottomright = (x, y))

        pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(15, 15))
        self.display_surface.blit(text_surf, text_rect)
        self.display_surface.blit(self.coin_image, self.coin_image_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(15, 15), 3)

    def show_coin_count(self, coin_count):
        text_surf = self.font.render(str(int(coin_count)), False, GOLD)
        x = WIDTH - 75
        y = 40
        text_rect = text_surf.get_rect(bottomright = (x, y))

        pygame.draw.rect(self.display_surface, BLACK, text_rect.inflate(50, 10))
        self.display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.display_surface, WHITE, text_rect.inflate(50, 10), 3)

    def display(self, player):
        self.show_bar(player.health, player.stats['health'], self.health_bar_rect, HEALTH_COLOR)
        self.show_bar(player.food_bar, player.stats['food_bar'], self.food_bar_rect, YELLOW)
        self.show_exp(player.exp)
        self.show_coin_count(player.coin_count)

class Inventory:
    def __init__(self, game):
        self.game = game
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font('fonts/JetBrainsMono-Regular.ttf', 22)

        self.move_items_bool = True
        self.split_items_bool = True
        self.coin_pressed = False
        self.hovering = False
        self.ihi = [0, 0]                   # inventory hover index

        self.iterator = 0
        self.add_value = 80

        self.eaten = False
        self.saturation = False
        self.potion_drunk = False
        self.potion_drunk_time = 0
        self.lettuce_drunk = False

        self.gap = 277.5
        self.inv_y = 350 # 400 original
        self.box_width = 75
        self.box_height = 75

        self.inventory_index = 0
        self.isi = [0, 0]                   # inventory selection index
        self.inventory_storage = [[+0, +0, +0, +0, +0, +0, +0, +0, +0], [+0, +0, +0, +0, +0, +0, +0, +0, +0], 
                                  [+0, +0, +0, +0, +0, +0, +0, +0, +0], [+0, +0, +0, +0, +0, +0, +0, +0, +0]]
        self.storage_count = [    [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], 
                                  [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0]]
        self.item_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]

        self.top_inv_rect = pygame.Rect(self.gap, self.inv_y, WIDTH-2*self.gap, 245)
        self.bottom_inv_rect = pygame.Rect(self.gap, HEIGHT-110, WIDTH-2*self.gap, self.box_height+10)

        self.name_rect = pygame.Rect(self.gap, self.inv_y-40, 150, 50)
        self.name_text = self.font.render("Inventory", True, BLACK)
        self.name_text_rect = self.name_text.get_rect()
        self.name_text_rect.x = self.gap + 10
        self.name_text_rect.y = self.inv_y - 30

        self.beef_image = self.enlarge(BEEF_IMAGE)
        self.beef_rect = self.beef_image.get_rect()
        self.calamari_image = self.enlarge(CALAMARI_IMAGE)
        self.calamari_rect = self.calamari_image.get_rect()
        self.fish_image = self.enlarge(FISH_IMAGE)
        self.fish_rect = self.fish_image.get_rect()
        self.honey_image = self.enlarge(HONEY_IMAGE)
        self.honey_rect = self.honey_image.get_rect()
        self.noodle_image = self.enlarge(NOODLE_IMAGE)
        self.noodle_rect = self.noodle_image.get_rect()
        self.shrimp_image = self.enlarge(SHRIMP_IMAGE)
        self.shrimp_rect = self.shrimp_image.get_rect()
        self.sushi_image = self.enlarge(SUSHI_IMAGE)
        self.sushi_rect = self.sushi_image.get_rect()
        self.sushi_image_2 = self.enlarge(SUSHI_IMAGE_2)
        self.sushi_rect_2 = self.sushi_image_2.get_rect()
        self.yakitori_image = self.enlarge(YAKITORI_IMAGE)
        self.yakitori_rect = self.yakitori_image.get_rect()

        self.sword_image = self.enlarge_2(SWORD_FULL)
        self.sword_rect = self.sword_image.get_rect()
        self.axe_image = self.enlarge(AXE_FULL)
        self.axe_rect = self.axe_image.get_rect()
        self.lance_image = pygame.transform.rotate(LANCE_FULL, -45)
        self.lance_rect = self.lance_image.get_rect()
        self.rapier_image = self.enlarge_3(RAPIER_FULL)
        self.rapier_rect = self.rapier_image.get_rect()
        self.sai_image = self.enlarge_4(SAI_FULL)
        self.sai_rect = self.sai_image.get_rect()

        self.coin_image = pygame.transform.scale(self.game.coin_spritesheet.get_sprite(0, 0, 10, 10, BLACK).convert_alpha(), (60, 60))
        self.coin_rect = self.coin_image.get_rect()

        self.wood_image = pygame.transform.scale(self.game.house_spritesheet.get_sprite(496, 288, 16, 16, BLACK).convert_alpha(), (70, 70))
        self.wood_rect = self.wood_image.get_rect()
        self.health_drink_image = pygame.transform.scale(self.game.house_spritesheet.get_sprite(336, 192, 16, 16, BLACK).convert_alpha(), (65, 65))
        self.health_drink_rect = self.health_drink_image.get_rect()
        self.poison_drink_image = pygame.transform.scale(self.game.house_spritesheet.get_sprite(336, 208, 16, 16, BLACK).convert_alpha(), (65, 65))
        self.poison_drink_rect = self.poison_drink_image.get_rect()
        self.lettuce_juice_image = pygame.transform.scale(self.game.house_spritesheet.get_sprite(336, 224, 16, 16, BLACK).convert_alpha(), (65, 65))
        self.lettuce_juice_rect = self.lettuce_juice_image.get_rect()
        self.empty_bottle_image = pygame.transform.scale(self.game.house_spritesheet.get_sprite(336, 240, 16, 16, BLACK).convert_alpha(), (65, 65))
        self.empty_bottle_rect = self.empty_bottle_image.get_rect()

        self.raw_iron_ore_image = pygame.transform.scale(self.game.terrain_spritesheet.get_sprite(0, 224, 16, 16, BLACK).convert_alpha(), (70, 70))
        self.raw_iron_ore_rect = self.raw_iron_ore_image.get_rect()
        self.iron_gem_image = pygame.transform.scale(self.game.terrain_spritesheet.get_sprite(0, 240, 16, 16, BLACK).convert_alpha(), (70, 70))
        self.iron_gem_rect = self.iron_gem_image.get_rect()
        self.iron_block_image = pygame.transform.scale(self.game.terrain_spritesheet.get_sprite(0, 256, 16, 16, BLACK).convert_alpha(), (65, 65))
        self.iron_block_rect = self.iron_block_image.get_rect()

        self.raw_mythril_ore_image = pygame.transform.scale(self.game.terrain_spritesheet.get_sprite(16, 224, 16, 16, BLACK).convert_alpha(), (70, 70))
        self.raw_mythril_ore_rect = self.raw_mythril_ore_image.get_rect()
        self.mythril_gem_image = pygame.transform.scale(self.game.terrain_spritesheet.get_sprite(16, 240, 16, 16, BLACK).convert_alpha(), (70, 70))
        self.mythril_gem_rect = self.mythril_gem_image.get_rect()
        self.mythril_block_image = pygame.transform.scale(self.game.terrain_spritesheet.get_sprite(16, 256, 16, 16, BLACK).convert_alpha(), (65, 65))
        self.mythril_block_rect = self.mythril_block_image.get_rect()

        self.raw_amethyst_ore_image = pygame.transform.scale(self.game.terrain_spritesheet.get_sprite(32, 224, 16, 16, BLACK).convert_alpha(), (70, 70))
        self.raw_amethyst_ore_rect = self.raw_amethyst_ore_image.get_rect()
        self.amethyst_gem_image = pygame.transform.scale(self.game.terrain_spritesheet.get_sprite(32, 240, 16, 16, BLACK).convert_alpha(), (70, 70))
        self.amethyst_gem_rect = self.amethyst_gem_image.get_rect()
        self.amethyst_block_image = pygame.transform.scale(self.game.terrain_spritesheet.get_sprite(32, 256, 16, 16, BLACK).convert_alpha(), (65, 65))
        self.amethyst_block_rect = self.amethyst_block_image.get_rect()

        self.raw_adamantite_ore_image = pygame.transform.scale(self.game.terrain_spritesheet.get_sprite(48, 224, 16, 16, BLACK).convert_alpha(), (70, 70))
        self.raw_adamantite_ore_rect = self.raw_adamantite_ore_image.get_rect()
        self.adamantite_gem_image = pygame.transform.scale(self.game.terrain_spritesheet.get_sprite(48, 240, 16, 16, BLACK).convert_alpha(), (70, 70))
        self.adamantite_gem_rect = self.adamantite_gem_image.get_rect()
        self.adamantite_block_image = pygame.transform.scale(self.game.terrain_spritesheet.get_sprite(48, 256, 16, 16, BLACK).convert_alpha(), (65, 65))
        self.adamantite_block_rect = self.adamantite_block_image.get_rect()

    def input(self, player):
        self.player = player
        keys = pygame.key.get_pressed()

        if keys[pygame.K_1]:
            self.inventory_index = 1
            self.isi = [3, 1]
        if keys[pygame.K_2]:
            self.inventory_index = 2
            self.isi = [3, 2]
        if keys[pygame.K_3]:
            self.inventory_index = 3
            self.isi = [3, 3]
        if keys[pygame.K_4]:
            self.inventory_index = 4
            self.isi = [3, 4]
        if keys[pygame.K_5]:
            self.inventory_index = 5
            self.isi = [3, 5]
        if keys[pygame.K_6]:
            self.inventory_index = 6
            self.isi = [3, 6]
        if keys[pygame.K_7]:
            self.inventory_index = 7
            self.isi = [3, 7]
        if keys[pygame.K_8]:
            self.inventory_index = 8
            self.isi = [3, 8]
        if keys[pygame.K_8]:
            self.inventory_index = 9
            self.isi = [3, 9]

        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_pressed = pygame.mouse.get_pressed()

        self.button_1_1 = self.button_def(5, 0, 5, 0)
        if self.button_1_1.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.inventory_index = 11
            self.isi = [0, 1]
        if self.button_1_1.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.ihi = [0, 1]
        self.button_1_2 = self.button_def(10, 1, 5, 0)
        if self.button_1_2.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.inventory_index = 12
            self.isi = [0, 2]
        if self.button_1_2.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.ihi = [0, 2]
        self.button_1_3 = self.button_def(15, 2, 5, 0)
        if self.button_1_3.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.inventory_index = 13
            self.isi = [0, 3]
        if self.button_1_3.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.ihi = [0, 3]
        self.button_1_4 = self.button_def(20, 3, 5, 0)
        if self.button_1_4.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.inventory_index = 14
            self.isi = [0, 4]
        if self.button_1_4.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.ihi = [0, 4]
        self.button_1_5 = self.button_def(25, 4, 5, 0)
        if self.button_1_5.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.inventory_index = 15
            self.isi = [0, 5]
        if self.button_1_5.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.ihi = [0, 5]
        self.button_1_6 = self.button_def(30, 5, 5, 0)
        if self.button_1_6.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.inventory_index = 16
            self.isi = [0, 6]
        if self.button_1_6.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.ihi = [0, 6]
        self.button_1_7 = self.button_def(35, 6, 5, 0)
        if self.button_1_7.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.inventory_index = 17
            self.isi = [0, 7]
        if self.button_1_7.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.ihi = [0, 7]
        self.button_1_8 = self.button_def(40, 7, 5, 0)
        if self.button_1_8.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.inventory_index = 18
            self.isi = [0, 8]
        if self.button_1_8.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.ihi = [0, 8]
        self.button_1_9 = self.button_def(45, 8, 5, 0)
        if self.button_1_9.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.inventory_index = 19
            self.isi = [0, 9]
        if self.button_1_9.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.ihi = [0, 9]

        self.button_2_1 = self.button_def(5, 0, 5, 1)
        if self.button_2_1.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.inventory_index = 21
            self.isi = [1, 1]
        if self.button_2_1.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.ihi = [1, 1]
        self.button_2_2 = self.button_def(10, 1, 5, 1)
        if self.button_2_2.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.inventory_index = 22
            self.isi = [1, 2]
        if self.button_2_2.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.ihi = [1, 2]
        self.button_2_3 = self.button_def(15, 2, 5, 1)
        if self.button_2_3.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.inventory_index = 23
            self.isi = [1, 3]
        if self.button_2_3.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.ihi = [1, 3]
        self.button_2_4 = self.button_def(20, 3, 5, 1)
        if self.button_2_4.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.inventory_index = 24
            self.isi = [1, 4]
        if self.button_2_4.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.ihi = [1, 4]
        self.button_2_5 = self.button_def(25, 4, 5, 1)
        if self.button_2_5.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.inventory_index = 25
            self.isi = [1, 5]
        if self.button_2_5.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.ihi = [1, 5]
        self.button_2_6 = self.button_def(30, 5, 5, 1)
        if self.button_2_6.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.inventory_index = 26
            self.isi = [1, 6]
        if self.button_2_6.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.ihi = [1, 6]
        self.button_2_7 = self.button_def(35, 6, 5, 1)
        if self.button_2_7.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.inventory_index = 27
            self.isi = [1, 7]
        if self.button_2_7.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.ihi = [1, 7]
        self.button_2_8 = self.button_def(40, 7, 5, 1)
        if self.button_2_8.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.inventory_index = 28
            self.isi = [1, 8]
        if self.button_2_8.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.ihi = [1, 8]
        self.button_2_9 = self.button_def(45, 8, 5, 1)
        if self.button_2_9.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.inventory_index = 29
            self.isi = [1, 9]
        if self.button_2_9.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.ihi = [1, 9]

        self.button_3_1 = self.button_def(5, 0, 5, 2)
        if self.button_3_1.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.inventory_index = 31
            self.isi = [2, 1]
        if self.button_3_1.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.ihi = [2, 1]
        self.button_3_2 = self.button_def(10, 1, 5, 2)
        if self.button_3_2.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.inventory_index = 32
            self.isi = [2, 2]
        if self.button_3_2.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.ihi = [2, 2]
        self.button_3_3 = self.button_def(15, 2, 5, 2)
        if self.button_3_3.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.inventory_index = 33
            self.isi = [2, 3]
        if self.button_3_3.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.ihi = [2, 3]
        self.button_3_4 = self.button_def(20, 3, 5, 2)
        if self.button_3_4.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.inventory_index = 34
            self.isi = [2, 4]
        if self.button_3_4.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.ihi = [2, 4]
        self.button_3_5 = self.button_def(25, 4, 5, 2)
        if self.button_3_5.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.inventory_index = 35
            self.isi = [2, 5]
        if self.button_3_5.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.ihi = [2, 5]
        self.button_3_6 = self.button_def(30, 5, 5, 2)
        if self.button_3_6.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.inventory_index = 36
            self.isi = [2, 6]
        if self.button_3_6.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.ihi = [2, 6]
        self.button_3_7 = self.button_def(35, 6, 5, 2)
        if self.button_3_7.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.inventory_index = 37
            self.isi = [2, 7]
        if self.button_3_7.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.ihi = [2, 7]
        self.button_3_8 = self.button_def(40, 7, 5, 2)
        if self.button_3_8.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.inventory_index = 38
            self.isi = [2, 8]
        if self.button_3_8.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.ihi = [2, 8]
        self.button_3_9 = self.button_def(45, 8, 5, 2)
        if self.button_3_9.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.inventory_index = 39
            self.isi = [2, 9]
        if self.button_3_9.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.ihi = [2, 9]

        con1 = self.inventory_storage[self.isi[0]][self.isi[1]-1] in FOOD_LIST and self.storage_count[self.isi[0]][self.isi[1]-1] > 0
        con2 = not self.game.chest.open_storage
        con3 = not self.eaten

        self.button_4_1 = self.button_def(5, 0, 70, 3)
        if self.button_4_1.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.inventory_index = 1
            self.isi = [3, 1]
        if self.button_4_1.is_right_pressed(self.mouse_pos, self.mouse_pressed):
            if self.isi[1] == 1:
                if con1 and con2 and con3:
                    self.eaten = True
                if self.inventory_storage[self.isi[0]][self.isi[1]-1] == 10:
                    self.coin_pressed = True
                if self.inventory_storage[self.isi[0]][self.isi[1]-1] in [17, 18, 19]:
                    self.potion_drunk = True
        if self.button_4_1.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.ihi = [3, 1]

        self.button_4_2 = self.button_def(10, 1, 70, 3)
        if self.button_4_2.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.inventory_index = 2
            self.isi = [3, 2]
        if self.button_4_2.is_right_pressed(self.mouse_pos, self.mouse_pressed):
            if self.isi[1] == 2:
                if con1 and con2 and con3:
                    self.eaten = True
                if self.inventory_storage[self.isi[0]][self.isi[1]-1] == 10:
                    self.coin_pressed = True
                if self.inventory_storage[self.isi[0]][self.isi[1]-1] in [17, 18, 19]:
                    self.potion_drunk = True
        if self.button_4_2.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.ihi = [3, 2]

        self.button_4_3 = self.button_def(15, 2, 70, 3)
        if self.button_4_3.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.inventory_index = 3
            self.isi = [3, 3]
        if self.button_4_3.is_right_pressed(self.mouse_pos, self.mouse_pressed):
            if self.isi[1] == 3:
                if con1 and con2 and con3:
                    self.eaten = True
                if self.inventory_storage[self.isi[0]][self.isi[1]-1] == 10:
                    self.coin_pressed = True
                if self.inventory_storage[self.isi[0]][self.isi[1]-1] in [17, 18, 19]:
                    self.potion_drunk = True
        if self.button_4_1.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.ihi = [3, 3]

        self.button_4_4 = self.button_def(20, 3, 70, 3)
        if self.button_4_4.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.inventory_index = 4
            self.isi = [3, 4]
        if self.button_4_4.is_right_pressed(self.mouse_pos, self.mouse_pressed):
            if self.isi[1] == 4:
                if con1 and con2 and con3:
                    self.eaten = True
                if self.inventory_storage[self.isi[0]][self.isi[1]-1] == 10:
                    self.coin_pressed = True
                if self.inventory_storage[self.isi[0]][self.isi[1]-1] in [17, 18, 19]:
                    self.potion_drunk = True
        if self.button_4_1.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.ihi = [3, 4]

        self.button_4_5 = self.button_def(25, 4, 70, 3)
        if self.button_4_5.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.inventory_index = 5
            self.isi = [3, 5]
        if self.button_4_5.is_right_pressed(self.mouse_pos, self.mouse_pressed):
            if self.isi[1] == 5:
                if con1 and con2 and con3:
                    self.eaten = True
                if self.inventory_storage[self.isi[0]][self.isi[1]-1] == 10:
                    self.coin_pressed = True
                if self.inventory_storage[self.isi[0]][self.isi[1]-1] in [17, 18, 19]:
                    self.potion_drunk = True
        if self.button_4_1.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.ihi = [3, 5]

        self.button_4_6 = self.button_def(30, 5, 70, 3)
        if self.button_4_6.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.inventory_index = 6
            self.isi = [3, 6]
        if self.button_4_6.is_right_pressed(self.mouse_pos, self.mouse_pressed):
            if self.isi[1] == 6:
                if con1 and con2 and con3:
                    self.eaten = True
                if self.inventory_storage[self.isi[0]][self.isi[1]-1] == 10:
                    self.coin_pressed = True
                if self.inventory_storage[self.isi[0]][self.isi[1]-1] in [17, 18, 19]:
                    self.potion_drunk = True
        if self.button_4_1.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.ihi = [3, 6]

        self.button_4_7 = self.button_def(35, 6, 70, 3)
        if self.button_4_7.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.inventory_index = 7
            self.isi = [3, 7]
        if self.button_4_7.is_right_pressed(self.mouse_pos, self.mouse_pressed):
            if self.isi[1] == 7:
                if con1 and con2 and con3:
                    self.eaten = True
                if self.inventory_storage[self.isi[0]][self.isi[1]-1] == 10:
                    self.coin_pressed = True
                if self.inventory_storage[self.isi[0]][self.isi[1]-1] in [17, 18, 19]:
                    self.potion_drunk = True
        if self.button_4_1.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.ihi = [3, 7]

        self.button_4_8 = self.button_def(40, 7, 70, 3)
        if self.button_4_8.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.inventory_index = 8
            self.isi = [3, 8]
        if self.button_4_8.is_right_pressed(self.mouse_pos, self.mouse_pressed):
            if self.isi[1] == 8:
                if con1 and con2 and con3:
                    self.eaten = True
                if self.inventory_storage[self.isi[0]][self.isi[1]-1] == 10:
                    self.coin_pressed = True
                if self.inventory_storage[self.isi[0]][self.isi[1]-1] in [17, 18, 19]:
                    self.potion_drunk = True
        if self.button_4_1.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.ihi = [3, 8]

        self.button_4_9 = self.button_def(45, 8, 70, 3)
        if self.button_4_9.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.inventory_index = 9
            self.isi = [3, 9]
        if self.button_4_9.is_right_pressed(self.mouse_pos, self.mouse_pressed):
            if self.isi[1] == 9:
                if con1 and con2 and con3:
                    self.eaten = True
                if self.inventory_storage[self.isi[0]][self.isi[1]-1] == 10:
                    self.coin_pressed = True
                if self.inventory_storage[self.isi[0]][self.isi[1]-1] in [17, 18, 19]:
                    self.potion_drunk = True
        if self.button_4_1.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.ihi = [3, 9]

        if self.eaten:
            if self.inventory_storage[self.isi[0]][self.isi[1]-1] == 1:
                if self.game.player.food_bar <= 200 - FOOD_REGEN_DICT['beef']:
                    self.game.player.food_bar += FOOD_REGEN_DICT['beef']
                    self.storage_count[3][self.isi[1]-1] -= 1
                    self.saturation = True
                elif self.game.player.food_bar < 190:
                    self.game.player.food_bar = 200
                    self.storage_count[3][self.isi[1]-1] -= 1
                    self.saturation = True
                if self.saturation:
                    if self.game.player.saturation_bar <= 300 - FOOD_SATURATION['beef']:
                        self.game.player.saturation_bar += FOOD_SATURATION['beef']
                    elif self.game.player.saturation_bar > 300 - FOOD_SATURATION['beef']:
                        self.game.player.saturation_bar = 300
                self.saturation = False

            if self.inventory_storage[self.isi[0]][self.isi[1]-1] == 2:
                if self.game.player.food_bar < 200 - FOOD_REGEN_DICT['calamari']:
                    self.game.player.food_bar += FOOD_REGEN_DICT['calamari']
                    self.storage_count[3][self.isi[1]-1] -= 1
                    self.saturation = True
                elif self.game.player.food_bar < 190:
                    self.game.player.food_bar = 200
                    self.storage_count[3][self.isi[1]-1] -= 1
                    self.saturation = True
                if self.saturation:
                    if self.game.player.saturation_bar <= 300 - FOOD_SATURATION['calamari']:
                        self.game.player.saturation_bar += FOOD_SATURATION['calamari']
                    elif self.game.player.saturation_bar > 300 - FOOD_SATURATION['calamari']:
                        self.game.player.saturation_bar = 300

            if self.inventory_storage[self.isi[0]][self.isi[1]-1] == 3:
                if self.game.player.food_bar < 200 - FOOD_REGEN_DICT['fish']:
                    self.game.player.food_bar += FOOD_REGEN_DICT['fish']
                    self.storage_count[3][self.isi[1]-1] -= 1
                    self.saturation = True
                elif self.game.player.food_bar < 190:
                    self.game.player.food_bar = 200
                    self.storage_count[3][self.isi[1]-1] -= 1
                    self.saturation = True
                if self.saturation:
                    if self.game.player.saturation_bar <= 300 - FOOD_SATURATION['fish']:
                        self.game.player.saturation_bar += FOOD_SATURATION['fish']
                    elif self.game.player.saturation_bar > 300 - FOOD_SATURATION['fish']:
                        self.game.player.saturation_bar = 300

            if self.inventory_storage[self.isi[0]][self.isi[1]-1] == 4:
                if self.game.player.food_bar < 200 - FOOD_REGEN_DICT['honey']:
                    self.game.player.food_bar += FOOD_REGEN_DICT['honey']
                    self.storage_count[3][self.isi[1]-1] -= 1
                    self.saturation = True
                elif self.game.player.food_bar < 190:
                    self.game.player.food_bar = 200
                    self.storage_count[3][self.isi[1]-1] -= 1
                    self.saturation = True
                if self.saturation:
                    if self.game.player.saturation_bar <= 300 - FOOD_SATURATION['honey']:
                        self.game.player.saturation_bar += FOOD_SATURATION['honey']
                    elif self.game.player.saturation_bar > 300 - FOOD_SATURATION['honey']:
                        self.game.player.saturation_bar = 300

            if self.inventory_storage[self.isi[0]][self.isi[1]-1] == 5:
                if self.game.player.food_bar < 200 - FOOD_REGEN_DICT['noodle']:
                    self.game.player.food_bar += FOOD_REGEN_DICT['noodle']
                    self.storage_count[3][self.isi[1]-1] -= 1
                    self.saturation = True
                elif self.game.player.food_bar < 190:
                    self.game.player.food_bar = 200
                    self.storage_count[3][self.isi[1]-1] -= 1
                    self.saturation = True
                if self.saturation:
                    if self.game.player.saturation_bar <= 300 - FOOD_SATURATION['noodle']:
                        self.game.player.saturation_bar += FOOD_SATURATION['noodle']
                    elif self.game.player.saturation_bar > 300 - FOOD_SATURATION['noodle']:
                        self.game.player.saturation_bar = 300

            if self.inventory_storage[self.isi[0]][self.isi[1]-1] == 6:
                if self.game.player.food_bar < 200 - FOOD_REGEN_DICT['shrimp']:
                    self.game.player.food_bar += FOOD_REGEN_DICT['shrimp']
                    self.storage_count[3][self.isi[1]-1] -= 1
                    self.saturation = True
                elif self.game.player.food_bar < 190:
                    self.game.player.food_bar = 200
                    self.storage_count[3][self.isi[1]-1] -= 1
                    self.saturation = True
                if self.saturation:
                    if self.game.player.saturation_bar <= 300 - FOOD_SATURATION['shrimp']:
                        self.game.player.saturation_bar += FOOD_SATURATION['shrimp']
                    elif self.game.player.saturation_bar > 300 - FOOD_SATURATION['shrimp']:
                        self.game.player.saturation_bar = 300

            if self.inventory_storage[self.isi[0]][self.isi[1]-1] == 7:
                if self.game.player.food_bar < 200 - FOOD_REGEN_DICT['sushi']:
                    self.game.player.food_bar += FOOD_REGEN_DICT['sushi']
                    self.storage_count[3][self.isi[1]-1] -= 1
                    self.saturation = True
                elif self.game.player.food_bar < 190:
                    self.game.player.food_bar = 200
                    self.storage_count[3][self.isi[1]-1] -= 1
                    self.saturation = True
                if self.saturation:
                    if self.game.player.saturation_bar <= 300 - FOOD_SATURATION['sushi']:
                        self.game.player.saturation_bar += FOOD_SATURATION['sushi']
                    elif self.game.player.saturation_bar > 300 - FOOD_SATURATION['sushi']:
                        self.game.player.saturation_bar = 300

            if self.inventory_storage[self.isi[0]][self.isi[1]-1] == 8:
                if self.game.player.food_bar < 200 - FOOD_REGEN_DICT['sushi2']:
                    self.game.player.food_bar += FOOD_REGEN_DICT['sushi2']
                    self.storage_count[3][self.isi[1]-1] -= 1
                    self.saturation = True
                elif self.game.player.food_bar < 190:
                    self.game.player.food_bar = 200
                    self.storage_count[3][self.isi[1]-1] -= 1
                    self.saturation = True
                if self.saturation:
                    if self.game.player.saturation_bar <= 300 - FOOD_SATURATION['sushi2']:
                        self.game.player.saturation_bar += FOOD_SATURATION['sushi2']
                    elif self.game.player.saturation_bar > 300 - FOOD_SATURATION['sushi2']:
                        self.game.player.saturation_bar = 300

            if self.inventory_storage[self.isi[0]][self.isi[1]-1] == 9:
                if self.game.player.food_bar < 200 - FOOD_REGEN_DICT['yakitori']:
                    self.game.player.food_bar += FOOD_REGEN_DICT['yakitori']
                    self.storage_count[3][self.isi[1]-1] -= 1
                    self.saturation = True
                elif self.game.player.food_bar < 190:
                    self.game.player.food_bar = 200
                    self.storage_count[3][self.isi[1]-1] -= 1
                    self.saturation = True
                if self.saturation:
                    if self.game.player.saturation_bar <= 300 - FOOD_SATURATION['yakitori']:
                        self.game.player.saturation_bar += FOOD_SATURATION['yakitori']
                    elif self.game.player.saturation_bar > 300 - FOOD_SATURATION['yakitori']:
                        self.game.player.saturation_bar = 300         
        self.eaten = False

        if self.coin_pressed:
            if self.inventory_storage[self.isi[0]][self.isi[1]-1] == 10 and self.storage_count[self.isi[0]][self.isi[1]-1] > 0:
                self.storage_count[self.isi[0]][self.isi[1]-1] -= 1
                self.game.player.coin_count += 1
        self.coin_pressed = False

        if self.potion_drunk:
            found = False
            for m, row in enumerate(self.storage_count):
                for n, i in enumerate(row):
                    if self.inventory_storage[m][n] == 20:
                        found = True
                        list1 = [m, n]
                        break
            if self.inventory_storage[self.isi[0]][self.isi[1]-1] == 17:
                if self.game.player.health <= 50:
                    self.storage_count[self.isi[0]][self.isi[1]-1] -= 1 
                    self.game.player.health += 150
                elif self.game.player.health > 50:
                    self.storage_count[self.isi[0]][self.isi[1]-1] -= 1
                    self.game.player.health = 200
            if self.inventory_storage[self.isi[0]][self.isi[1]-1] == 18:
                self.storage_count[self.isi[0]][self.isi[1]-1] -= 1
                self.game.player.health -= 100
            if self.inventory_storage[self.isi[0]][self.isi[1]-1] == 19:
                if self.game.player.health <= 100:
                    self.storage_count[self.isi[0]][self.isi[1]-1] -= 1 
                    self.game.player.health += 100
                elif self.game.player.health > 100:
                    self.storage_count[self.isi[0]][self.isi[1]-1] -= 1
                    self.game.player.health = 200
            if found:
                self.storage_count[list1[0]][list1[1]] += 1
            elif not found:
                self.storage_count[self.isi[0]][self.isi[1]-1] = 1
                self.inventory_storage[self.isi[0]][self.isi[1]-1] = 20
        self.potion_drunk = False

        self.iterator += 1
        if self.iterator > 59:
            self.iterator = -1
        elif self.iterator == 0:
            self.move_items_bool = True
            self.split_items_bool = True
            self.eaten = False
            self.coin_pressed = False

        self.chest_spawn(self.game.chest, self.game.chest.storage, self.game.chest.storage_count, keys)
        self.chest_spawn(self.game.chest_1, self.game.chest_1.storage, self.game.chest_1.storage_count, keys)
        self.chest_spawn(self.game.chest_2, self.game.chest_2.storage, self.game.chest_2.storage_count, keys)
        self.chest_spawn(self.game.chest_3, self.game.chest_3.storage, self.game.chest_3.storage_count, keys)

        for i, row in enumerate(self.storage_count):
            for j, col in enumerate(row):
                if col <= 0:
                    if self.inventory_storage[i][j] != 0:
                        self.inventory_storage[i][j] = 0
    
    def chest_spawn(self, object, chest_storage, chest_count, keys):
        condition_1 = self.inventory_storage[self.isi[0]][self.isi[1]-1] not in [11, 12, 13, 14, 15, 17, 18, 19]
        condition_2 = chest_storage[object.csi[0]-1][object.csi[1]-1] not in [11, 12, 13, 14, 15, 17, 18, 19]  

        if keys[pygame.K_t]:
            if object.open_storage and self.game.player.open_inventory and self.move_items_bool:
                temporary_value = self.inventory_storage[self.isi[0]][self.isi[1]-1]
                self.inventory_storage[self.isi[0]][self.isi[1]-1] = chest_storage[object.csi[0]-1][object.csi[1]-1]
                chest_storage[object.csi[0]-1][object.csi[1]-1] = temporary_value

                count_temp_value = self.storage_count[self.isi[0]][self.isi[1]-1]
                self.storage_count[self.isi[0]][self.isi[1]-1] = chest_count[object.csi[0]-1][object.csi[1]-1]
                chest_count[object.csi[0]-1][object.csi[1]-1] = count_temp_value

                if condition_1 and condition_2:
                    if self.inventory_storage[self.isi[0]][self.isi[1]-1] == chest_storage[object.csi[0]-1][object.csi[1]-1]:
                        if self.storage_count[self.isi[0]][self.isi[1]-1]+self.game.storage_count[object.csi[0]-1][object.csi[1]-1] < 17:
                            chest_storage[object.csi[0]-1][object.csi[1]-1] = 0
                            self.storage_count[self.isi[0]][self.isi[1]-1] += chest_count[object.csi[0]-1][object.csi[1]-1]
                            chest_count[object.csi[0]-1][object.csi[1]-1] = 0
                        elif self.storage_count[self.isi[0]][self.isi[1]-1]+chest_count[object.csi[0]-1][object.csi[1]-1] > 16:
                            holding_value = 16-self.storage_count[self.isi[0]][self.isi[1]-1]
                            self.storage_count[self.isi[0]][self.isi[1]-1] += holding_value
                            chest_count[object.csi[0]-1][object.csi[1]-1] -= holding_value

                self.move_items_bool = False

        if keys[pygame.K_y] and condition_1 and condition_2:
            if self.game.player.open_inventory and self.split_items_bool and self.storage_count[self.isi[0]][self.isi[1]-1] > 1:
                val1 = self.inventory_storage[self.isi[0]][self.isi[1]-1]
                val = self.storage_count[self.isi[0]][self.isi[1]-1]
                val //= 2
                new_val = self.storage_count[self.isi[0]][self.isi[1]-1] - val
                self.storage_count[self.isi[0]][self.isi[1]-1] = val
                for m, row in enumerate(self.storage_count):
                    for n, i in enumerate(row):
                        if i == 0:
                            self.inventory_storage[m][n] = val1
                            self.storage_count[m][n] = new_val
                            break
                        else:
                            print("no space")
                    break
            self.split_items_bool = False

    def button_def(self, add_to_x, mul_to_x, add_to_y, mul_to_y):
        return Button(self.gap+add_to_x+self.box_width*mul_to_x, self.inv_y+add_to_y+self.box_height*mul_to_y, self.box_width, self.box_height, BLACK, WHITE, '', 14)

    def draw_selection_rect(self, mul_to_x, add_to_y, mul_to_y):
        self.border_rect = pygame.Rect(self.gap+self.add_value*mul_to_x, self.inv_y+add_to_y+self.box_height*mul_to_y, self.box_width+10, self.box_height+10)
        pygame.draw.rect(self.display_surface, BLACK, self.border_rect)

    def enlarge(self, image):
        return pygame.transform.scale(image, (75, 75))
    def enlarge_2(self, image):
        img = pygame.transform.scale(image, (28, 70))
        return pygame.transform.rotate(img, -45)
    def enlarge_3(self, image):
        img = pygame.transform.scale(image, (46, 70))
        return pygame.transform.rotate(img, 45)
    def enlarge_4(self, image):
        img = pygame.transform.scale(image, (37, 70))
        return pygame.transform.rotate(img, -45)

    def draw_inventory(self):
        pygame.draw.rect(self.display_surface, GREY, self.name_rect)
        pygame.draw.rect(self.display_surface, GREY, self.top_inv_rect)

        self.display_surface.blit(self.name_text, self.name_text_rect)

        if self.inventory_index == 11:
            self.draw_selection_rect(0, 0, 0)
        elif self.inventory_index == 12:
            self.draw_selection_rect(1, 0, 0)
        elif self.inventory_index == 13:
            self.draw_selection_rect(2, 0, 0)
        elif self.inventory_index == 14:
            self.draw_selection_rect(3, 0, 0)
        elif self.inventory_index == 15:
            self.draw_selection_rect(4, 0, 0)
        elif self.inventory_index == 16:
            self.draw_selection_rect(5, 0, 0)
        elif self.inventory_index == 17:
            self.draw_selection_rect(6, 0, 0)
        elif self.inventory_index == 18:
            self.draw_selection_rect(7, 0, 0)
        elif self.inventory_index == 19:
            self.draw_selection_rect(8, 0, 0)

        if self.inventory_index == 21:
            self.draw_selection_rect(0, 5, 1)
        elif self.inventory_index == 22:
            self.draw_selection_rect(1, 5, 1)
        elif self.inventory_index == 23:
            self.draw_selection_rect(2, 5, 1)
        elif self.inventory_index == 24:
            self.draw_selection_rect(3, 5, 1)
        elif self.inventory_index == 25:
            self.draw_selection_rect(4, 5, 1)
        elif self.inventory_index == 26:
            self.draw_selection_rect(5, 5, 1)
        elif self.inventory_index == 27:
            self.draw_selection_rect(6, 5, 1)
        elif self.inventory_index == 28:
            self.draw_selection_rect(7, 5, 1)
        elif self.inventory_index == 29:
            self.draw_selection_rect(8, 5, 1)

        if self.inventory_index == 31:
            self.draw_selection_rect(0, 10, 2)
        elif self.inventory_index == 32:
            self.draw_selection_rect(1, 10, 2)
        elif self.inventory_index == 33:
            self.draw_selection_rect(2, 10, 2)
        elif self.inventory_index == 34:
            self.draw_selection_rect(3, 10, 2)
        elif self.inventory_index == 35:
            self.draw_selection_rect(4, 10, 2)
        elif self.inventory_index == 36:
            self.draw_selection_rect(5, 10, 2)
        elif self.inventory_index == 37:
            self.draw_selection_rect(6, 10, 2)
        elif self.inventory_index == 38:
            self.draw_selection_rect(7, 10, 2)
        elif self.inventory_index == 39:
            self.draw_selection_rect(8, 10, 2)

        for j in range(3):
            width_gap = 5*(j+1)
            for i in range(9):
                space = 5*(i+1)
                small_rect_x = self.box_width*i
                width = self.box_width
                height = self.box_height
                self.small_rect = pygame.Rect(self.gap+space+small_rect_x, self.inv_y+width_gap+self.box_height*j, width, height)
                pygame.draw.rect(self.display_surface, WHITE, self.small_rect)

        if self.game.player.open_inventory:
            for i, row in enumerate(self.inventory_storage):
                for j, column in enumerate(row):
                    if i != 3 and self.storage_count[i][j] > 0:
                        if column == 1:
                            self.beef_rect.x = self.gap+self.box_width*j+5*(j+1)-2.5
                            self.beef_rect.y = self.box_width*i+5*i+self.inv_y
                            self.display_surface.blit(self.beef_image, self.beef_rect)
                        if column == 2:
                            self.calamari_rect.x = self.gap+self.box_width*j+5*(j+1)-3
                            self.calamari_rect.y = self.box_width*i+5*i+self.inv_y
                            self.display_surface.blit(self.calamari_image, self.calamari_rect)
                        if column == 3:
                            self.fish_rect.x = self.gap+self.box_width*j+5*(j+1)
                            self.fish_rect.y = self.box_width*i+5*i+self.inv_y
                            self.display_surface.blit(self.fish_image, self.fish_rect)
                        if column == 4:
                            self.honey_rect.x = self.gap+self.box_width*j+5*(j+1)
                            self.honey_rect.y = self.box_width*i+5*i+self.inv_y
                            self.display_surface.blit(self.honey_image, self.honey_rect)
                        if column == 5:
                            self.noodle_rect.x = self.gap+self.box_width*j+5*(j+1)
                            self.noodle_rect.y = self.box_width*i+5*i+self.inv_y
                            self.display_surface.blit(self.noodle_image, self.noodle_rect)
                        if column == 6:
                            self.shrimp_rect.x = self.gap+self.box_width*j+5*(j+1)
                            self.shrimp_rect.y = self.box_width*i+5*i+self.inv_y
                            self.display_surface.blit(self.shrimp_image, self.shrimp_rect)
                        if column == 7:
                            self.sushi_rect.x = self.gap+self.box_width*j+5*(j+1)
                            self.sushi_rect.y = self.box_width*i+5*i+self.inv_y
                            self.display_surface.blit(self.sushi_image, self.sushi_rect)
                        if column == 8:
                            self.sushi_rect_2.x = self.gap+self.box_width*j+5*(j+1)
                            self.sushi_rect_2.y = self.box_width*i+5*i+self.inv_y
                            self.display_surface.blit(self.sushi_image_2, self.sushi_rect_2)
                        if column == 9:
                            self.yakitori_rect.x = self.gap+self.box_width*j+5*(j+1)
                            self.yakitori_rect.y = self.box_width*i+5*i+self.inv_y
                            self.display_surface.blit(self.yakitori_image, self.yakitori_rect)

                        if column == 10:
                            self.coin_rect.x = self.gap+self.box_width*j+5*(j+1)+8
                            self.coin_rect.y = self.box_width*i+5*i+self.inv_y+8
                            self.display_surface.blit(self.coin_image, self.coin_rect)
                            
                        if column == 11:
                            self.sword_rect.x = self.gap+self.box_width*j+5*(j+1)
                            self.sword_rect.y = self.box_width*i+5*i+self.inv_y
                            self.display_surface.blit(self.sword_image, self.sword_rect)
                        if column == 12:
                            self.axe_rect.x = self.gap+self.box_width*j+5*(j+1)
                            self.axe_rect.y = self.box_width*i+5*i+self.inv_y
                            self.display_surface.blit(self.axe_image, self.axe_rect)
                        if column == 13:
                            self.lance_rect.x = self.gap+self.box_width*j+5*(j+1)
                            self.lance_rect.y = self.box_width*i+5*i+self.inv_y
                            self.display_surface.blit(self.lance_image, self.lance_rect)
                        if column == 14:
                            self.rapier_rect.x = self.gap+self.box_width*j+5*(j+1)
                            self.rapier_rect.y = self.box_width*i+5*i+self.inv_y
                            self.display_surface.blit(self.rapier_image, self.rapier_rect)
                        if column == 15:
                            self.sai_rect.x = self.gap+self.box_width*j+5*(j+1)
                            self.sai_rect.y = self.box_width*i+5*i+self.inv_y
                            self.display_surface.blit(self.sai_image, self.sai_rect)
                        
                        if column == 16:
                            self.wood_rect.x = self.gap+self.box_width*j+5*(j+1)
                            self.wood_rect.y = self.box_width*i+5*i+self.inv_y+5
                            self.display_surface.blit(self.wood_image, self.wood_rect)
                        if column == 17:
                            self.health_drink_rect.x = self.gap+self.box_width*j+5*(j+1)+3
                            self.health_drink_rect.y = self.box_width*i+5*i+self.inv_y+5
                            self.display_surface.blit(self.health_drink_image, self.health_drink_rect)
                        if column == 18:
                            self.poison_drink_rect.x = self.gap+self.box_width*j+5*(j+1)+3
                            self.poison_drink_rect.y = self.box_width*i+5*i+self.inv_y+5
                            self.display_surface.blit(self.poison_drink_image, self.poison_drink_rect)
                        if column == 19:
                            self.lettuce_juice_rect.x = self.gap+self.box_width*j+5*(j+1)+3
                            self.lettuce_juice_rect.y = self.box_width*i+5*i+self.inv_y+5
                            self.display_surface.blit(self.lettuce_juice_image, self.lettuce_juice_rect)
                        if column == 20:
                            self.empty_bottle_rect.x = self.gap+self.box_width*j+5*(j+1)+3
                            self.empty_bottle_rect.y = self.box_width*i+5*i+self.inv_y+5
                            self.display_surface.blit(self.empty_bottle_image, self.empty_bottle_rect)

                        if column == 21:
                            self.raw_iron_ore_rect.x = self.gap+self.box_width*j+5*(j+1)+2
                            self.raw_iron_ore_rect.y = self.box_width*i+5*i+self.inv_y+2
                            self.display_surface.blit(self.raw_iron_ore_image, self.raw_iron_ore_rect)
                        if column == 22:
                            self.iron_gem_rect.x = self.gap+self.box_width*j+5*(j+1)+2
                            self.iron_gem_rect.y = self.box_width*i+5*i+self.inv_y+2
                            self.display_surface.blit(self.iron_gem_image, self.iron_gem_rect)
                        if column == 23:
                            self.iron_block_rect.x = self.gap+self.box_width*j+5*(j+1)+4
                            self.iron_block_rect.y = self.box_width*i+5*i+self.inv_y+4
                            self.display_surface.blit(self.iron_block_image, self.iron_block_rect)
                        if column == 24:
                            self.raw_mythril_ore_rect.x = self.gap+self.box_width*j+5*(j+1)+2
                            self.raw_mythril_ore_rect.y = self.box_width*i+5*i+self.inv_y+2
                            self.display_surface.blit(self.raw_mythril_ore_image, self.raw_mythril_ore_rect)
                        if column == 25:
                            self.mythril_gem_rect.x = self.gap+self.box_width*j+5*(j+1)+2
                            self.mythril_gem_rect.y = self.box_width*i+5*i+self.inv_y+2
                            self.display_surface.blit(self.mythril_gem_image, self.mythril_gem_rect)
                        if column == 26:
                            self.mythril_block_rect.x = self.gap+self.box_width*j+5*(j+1)+4
                            self.mythril_block_rect.y = self.box_width*i+5*i+self.inv_y+4
                            self.display_surface.blit(self.mythril_block_image, self.mythril_block_rect)
                        if column == 27:
                            self.raw_amethyst_ore_rect.x = self.gap+self.box_width*j+5*(j+1)+2
                            self.raw_amethyst_ore_rect.y = self.box_width*i+5*i+self.inv_y+2
                            self.display_surface.blit(self.raw_amethyst_ore_image, self.raw_amethyst_ore_rect)
                        if column == 28:
                            self.amethyst_gem_rect.x = self.gap+self.box_width*j+5*(j+1)+2
                            self.amethyst_gem_rect.y = self.box_width*i+5*i+self.inv_y+2
                            self.display_surface.blit(self.amethyst_gem_image, self.amethyst_gem_rect)
                        if column == 29:
                            self.amethyst_block_rect.x = self.gap+self.box_width*j+5*(j+1)+4
                            self.amethyst_block_rect.y = self.box_width*i+5*i+self.inv_y+4
                            self.display_surface.blit(self.amethyst_block_image, self.amethyst_block_rect)
                        if column == 30:
                            self.raw_adamantite_ore_rect.x = self.gap+self.box_width*j+5*(j+1)+2
                            self.raw_adamantite_ore_rect.y = self.box_width*i+5*i+self.inv_y+2
                            self.display_surface.blit(self.raw_adamantite_ore_image, self.raw_adamantite_ore_rect)
                        if column == 31:
                            self.adamantite_gem_rect.x = self.gap+self.box_width*j+5*(j+1)+2
                            self.adamantite_gem_rect.y = self.box_width*i+5*i+self.inv_y+2
                            self.display_surface.blit(self.adamantite_gem_image, self.adamantite_gem_rect)
                        if column == 32:
                            self.adamantite_block_rect.x = self.gap+self.box_width*j+5*(j+1)+4
                            self.adamantite_block_rect.y = self.box_width*i+5*i+self.inv_y+4
                            self.display_surface.blit(self.adamantite_block_image, self.adamantite_block_rect)

            for i2, row in enumerate(self.storage_count):
                for j2, column in enumerate(row):
                    if i2 != 3:
                        self.text = self.font.render(str(column), True, BLACK)
                        self.text_rect = self.text.get_rect()
                        if column < 10:
                            self.text_rect.x = self.gap+self.box_width*(j2+1)+5*(j2-2)
                        if column > 9 and column < 17:
                            self.text_rect.x = self.gap+self.box_width*(j2+1)+5*(j2-2)-9
                        self.text_rect.y = self.inv_y+80*(i2+1)-22
                        if column != 0:
                            self.display_surface.blit(self.text, self.text_rect)

        if self.hovering and self.game.player.open_inventory:
            if self.inventory_storage[self.ihi[0]][self.ihi[1]-1] == 1:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 86, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 80, 40)
                info_word = self.font.render("Beef", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+15
                info_word_rect.y = self.mouse_pos[1]+6
            if self.inventory_storage[self.ihi[0]][self.ihi[1]-1] == 2:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 116, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 110, 40)
                info_word = self.font.render("Calamari", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+6
                info_word_rect.y = self.mouse_pos[1]+6
            if self.inventory_storage[self.ihi[0]][self.ihi[1]-1] == 3:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 86, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 80, 40)
                info_word = self.font.render("Fish", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+15
                info_word_rect.y = self.mouse_pos[1]+6
            if self.inventory_storage[self.ihi[0]][self.ihi[1]-1] == 4:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 86, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 80, 40)
                info_word = self.font.render("Honey", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.inventory_storage[self.ihi[0]][self.ihi[1]-1] == 5:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 96, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 90, 40)
                info_word = self.font.render("Noodle", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.inventory_storage[self.ihi[0]][self.ihi[1]-1] == 6:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 96, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 90, 40)
                info_word = self.font.render("Shrimp", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.inventory_storage[self.ihi[0]][self.ihi[1]-1] == 7:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 86, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 80, 40)
                info_word = self.font.render("Sushi", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.inventory_storage[self.ihi[0]][self.ihi[1]-1] == 8:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 86, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 80, 40)
                info_word = self.font.render("Sushi", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.inventory_storage[self.ihi[0]][self.ihi[1]-1] == 9:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 116, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 110, 40)
                info_word = self.font.render("Yakitori", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+6
                info_word_rect.y = self.mouse_pos[1]+6
            if self.inventory_storage[self.ihi[0]][self.ihi[1]-1] == 10:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 86, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 80, 40)
                info_word = self.font.render("Coin", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+15
                info_word_rect.y = self.mouse_pos[1]+6
            if self.inventory_storage[self.ihi[0]][self.ihi[1]-1] == 11:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 96, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 90, 40)
                info_word = self.font.render("Sword", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.inventory_storage[self.ihi[0]][self.ihi[1]-1] == 12:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 86, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 80, 40)
                info_word = self.font.render("Axe", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+15
                info_word_rect.y = self.mouse_pos[1]+6
            if self.inventory_storage[self.ihi[0]][self.ihi[1]-1] == 13:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 96, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 90, 40)
                info_word = self.font.render("Lance", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.inventory_storage[self.ihi[0]][self.ihi[1]-1] == 14:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 96, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 90, 40)
                info_word = self.font.render("Rapier", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.inventory_storage[self.ihi[0]][self.ihi[1]-1] == 15:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 86, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 80, 40)
                info_word = self.font.render("Sai", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+15
                info_word_rect.y = self.mouse_pos[1]+6
            if self.inventory_storage[self.ihi[0]][self.ihi[1]-1] == 16:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 121, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 115, 40)
                info_word = self.font.render("Log Pile", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.inventory_storage[self.ihi[0]][self.ihi[1]-1] == 17:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 186, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 180, 40)
                info_word = self.font.render("Health Potion", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.inventory_storage[self.ihi[0]][self.ihi[1]-1] == 18:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 186, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 180, 40)
                info_word = self.font.render("Poison Potion", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.inventory_storage[self.ihi[0]][self.ihi[1]-1] == 19:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 186, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 180, 40)
                info_word = self.font.render("Lettuce Juice", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.inventory_storage[self.ihi[0]][self.ihi[1]-1] == 20:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 176, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 170, 40)
                info_word = self.font.render("Empty Bottle", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.inventory_storage[self.ihi[0]][self.ihi[1]-1] == 21:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 186, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 180, 40)
                info_word = self.font.render("Raw Iron Ore", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.inventory_storage[self.ihi[0]][self.ihi[1]-1] == 22:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 166, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 160, 40)
                info_word = self.font.render("Iron Gem", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.inventory_storage[self.ihi[0]][self.ihi[1]-1] == 23:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 176, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 170, 40)
                info_word = self.font.render("Iron Block", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.inventory_storage[self.ihi[0]][self.ihi[1]-1] == 24:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 216, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 210, 40)
                info_word = self.font.render("Raw Mythril Ore", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.inventory_storage[self.ihi[0]][self.ihi[1]-1] == 25:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 186, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 180, 40)
                info_word = self.font.render("Mythril Gem", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.inventory_storage[self.ihi[0]][self.ihi[1]-1] == 26:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 186, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 180, 40)
                info_word = self.font.render("Mythril Block", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.inventory_storage[self.ihi[0]][self.ihi[1]-1] == 27:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 226, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 220, 40)
                info_word = self.font.render("Raw Amethyst Ore", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.inventory_storage[self.ihi[0]][self.ihi[1]-1] == 28:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 186, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 180, 40)
                info_word = self.font.render("Amethyst Gem", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.inventory_storage[self.ihi[0]][self.ihi[1]-1] == 29:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 206, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 200, 40)
                info_word = self.font.render("Amethyst Block", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.inventory_storage[self.ihi[0]][self.ihi[1]-1] == 30:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 256, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 250, 40)
                info_word = self.font.render("Raw Adamantite Ore", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.inventory_storage[self.ihi[0]][self.ihi[1]-1] == 31:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 196, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 190, 40)
                info_word = self.font.render("Adamantite Gem", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.inventory_storage[self.ihi[0]][self.ihi[1]-1] == 32:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 216, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 210, 40)
                info_word = self.font.render("Adamantite Block", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.inventory_storage[self.ihi[0]][self.ihi[1]-1] in self.item_list:
                pygame.draw.rect(self.display_surface, VIOLET, info_rect_border)
                pygame.draw.rect(self.display_surface, BLACK, info_rect)
                self.display_surface.blit(info_word, info_word_rect)
        self.hovering = False

    def display(self, player):
        pygame.draw.rect(self.display_surface, GREY, self.bottom_inv_rect)

        if self.inventory_index == 1:
            self.draw_selection_rect(0, 65, 3)
        elif self.inventory_index == 2:
            self.draw_selection_rect(1, 65, 3)
        elif self.inventory_index == 3:
            self.draw_selection_rect(2, 65, 3)
        elif self.inventory_index == 4:
            self.draw_selection_rect(3, 65, 3)
        elif self.inventory_index == 5:
            self.draw_selection_rect(4, 65, 3)
        elif self.inventory_index == 6:
            self.draw_selection_rect(5, 65, 3)
        elif self.inventory_index == 7:
            self.draw_selection_rect(6, 65, 3)
        elif self.inventory_index == 8:
            self.draw_selection_rect(7, 65, 3)
        elif self.inventory_index == 9:
            self.draw_selection_rect(8, 65, 3)

        for i in range(9):
            space = 5*(i+1)
            small_rect_x = self.box_width*i
            width = self.box_width
            height = self.box_height
            self.small_rect = pygame.Rect(self.gap+space+small_rect_x, HEIGHT-105, width, height)
            pygame.draw.rect(self.display_surface, WHITE, self.small_rect)

        for i, row in enumerate(self.inventory_storage):
            for j, column in enumerate(row):
                if i == 3 and self.storage_count[i][j] > 0:
                    if column == 1:
                        self.beef_rect.x = self.gap+self.box_width*j+5*(j+1)-2.5
                        self.beef_rect.y = self.inv_y+70+self.box_height*3
                        self.display_surface.blit(self.beef_image, self.beef_rect)
                    if column == 2:
                        self.calamari_rect.x = self.gap+self.box_width*j+5*(j+1)-3
                        self.calamari_rect.y = self.inv_y+70+self.box_height*3
                        self.display_surface.blit(self.calamari_image, self.calamari_rect)
                    if column == 3:
                        self.fish_rect.x = self.gap+self.box_width*j+5*(j+1)
                        self.fish_rect.y = self.inv_y+70+self.box_height*3
                        self.display_surface.blit(self.fish_image, self.fish_rect)
                    if column == 4:
                        self.honey_rect.x = self.gap+self.box_width*j+5*(j+1)
                        self.honey_rect.y = self.inv_y+70+self.box_height*3
                        self.display_surface.blit(self.honey_image, self.honey_rect)
                    if column == 5:
                        self.noodle_rect.x = self.gap+self.box_width*j+5*(j+1)
                        self.noodle_rect.y = self.inv_y+70+self.box_height*3
                        self.display_surface.blit(self.noodle_image, self.noodle_rect)
                    if column == 6:
                        self.shrimp_rect.x = self.gap+self.box_width*j+5*(j+1)
                        self.shrimp_rect.y = self.inv_y+70+self.box_height*3
                        self.display_surface.blit(self.shrimp_image, self.shrimp_rect)
                    if column == 7:
                        self.sushi_rect.x = self.gap+self.box_width*j+5*(j+1)
                        self.sushi_rect.y = self.inv_y+70+self.box_height*3
                        self.display_surface.blit(self.sushi_image, self.sushi_rect)
                    if column == 8:
                        self.sushi_rect_2.x = self.gap+self.box_width*j+5*(j+1)
                        self.sushi_rect_2.y = self.inv_y+70+self.box_height*3
                        self.display_surface.blit(self.sushi_image_2, self.sushi_rect_2)
                    if column == 9:
                        self.yakitori_rect.x = self.gap+self.box_width*j+5*(j+1)
                        self.yakitori_rect.y = self.inv_y+70+self.box_height*3
                        self.display_surface.blit(self.yakitori_image, self.yakitori_rect)

                    if column == 10:
                        self.coin_rect.x = self.gap+self.box_width*j+5*(j+1)+8
                        self.coin_rect.y = self.inv_y+70+self.box_height*3+8
                        self.display_surface.blit(self.coin_image, self.coin_rect)

                    if column == 11:
                        self.sword_rect.x = self.gap+self.box_width*j+5*(j+1)
                        self.sword_rect.y = self.inv_y+70+self.box_height*3
                        self.display_surface.blit(self.sword_image, self.sword_rect)
                        background_rect_sword = pygame.Rect(self.gap+self.box_width*j+5*(j+1), self.inv_y+70+self.box_height*3+70, self.game.player.sword_durability, 5)
                        pygame.draw.rect(self.display_surface, GREEN, background_rect_sword)
                    if column == 12:
                        self.axe_rect.x = self.gap+self.box_width*j+5*(j+1)
                        self.axe_rect.y = self.inv_y+70+self.box_height*3
                        self.display_surface.blit(self.axe_image, self.axe_rect)
                        background_rect_sword = pygame.Rect(self.gap+self.box_width*j+5*(j+1), self.inv_y+70+self.box_height*3+70, self.game.player.axe_durability, 5)
                        pygame.draw.rect(self.display_surface, GREEN, background_rect_sword)
                    if column == 13:
                        self.lance_rect.x = self.gap+self.box_width*j+5*(j+1)
                        self.lance_rect.y = self.inv_y+70+self.box_height*3
                        self.display_surface.blit(self.lance_image, self.lance_rect)
                        background_rect_sword = pygame.Rect(self.gap+self.box_width*j+5*(j+1), self.inv_y+70+self.box_height*3+70, self.game.player.lance_durability, 5)
                        pygame.draw.rect(self.display_surface, GREEN, background_rect_sword)
                    if column == 14:
                        self.rapier_rect.x = self.gap+self.box_width*j+5*(j+1)
                        self.rapier_rect.y = self.inv_y+70+self.box_height*3
                        self.display_surface.blit(self.rapier_image, self.rapier_rect)
                        background_rect_sword = pygame.Rect(self.gap+self.box_width*j+5*(j+1), self.inv_y+70+self.box_height*3+70, self.game.player.rapier_durability, 5)
                        pygame.draw.rect(self.display_surface, GREEN, background_rect_sword)
                    if column == 15:
                        self.sai_rect.x = self.gap+self.box_width*j+5*(j+1)
                        self.sai_rect.y = self.inv_y+70+self.box_height*3
                        self.display_surface.blit(self.sai_image, self.sai_rect)
                        background_rect_sword = pygame.Rect(self.gap+self.box_width*j+5*(j+1), self.inv_y+70+self.box_height*3+70, self.game.player.sai_durability, 5)
                        pygame.draw.rect(self.display_surface, GREEN, background_rect_sword)

                    if column == 16:
                        self.wood_rect.x = self.gap+self.box_width*j+5*(j+1)
                        self.wood_rect.y = self.inv_y+70+self.box_height*3+5
                        self.display_surface.blit(self.wood_image, self.wood_rect)
                    if column == 17:
                        self.health_drink_rect.x = self.gap+self.box_width*j+5*(j+1)+3
                        self.health_drink_rect.y = self.inv_y+70+self.box_height*3+5
                        self.display_surface.blit(self.health_drink_image, self.health_drink_rect)
                    if column == 18:
                        self.poison_drink_rect.x = self.gap+self.box_width*j+5*(j+1)+3
                        self.poison_drink_rect.y = self.inv_y+70+self.box_height*3+5
                        self.display_surface.blit(self.poison_drink_image, self.poison_drink_rect)
                    if column == 19:
                        self.lettuce_juice_rect.x = self.gap+self.box_width*j+5*(j+1)+3
                        self.lettuce_juice_rect.y = self.inv_y+70+self.box_height*3+5
                        self.display_surface.blit(self.lettuce_juice_image, self.lettuce_juice_rect)
                    if column == 20:
                        self.empty_bottle_rect.x = self.gap+self.box_width*j+5*(j+1)+3
                        self.empty_bottle_rect.y = self.inv_y+70+self.box_height*3+5
                        self.display_surface.blit(self.empty_bottle_image, self.empty_bottle_rect)

                    if column == 21:
                        self.raw_iron_ore_rect.x = self.gap+self.box_width*j+5*(j+1)+2
                        self.raw_iron_ore_rect.y = self.inv_y+70+self.box_height*3+2
                        self.display_surface.blit(self.raw_iron_ore_image, self.raw_iron_ore_rect)
                    if column == 22:
                        self.iron_gem_rect.x = self.gap+self.box_width*j+5*(j+1)+2
                        self.iron_gem_rect.y = self.inv_y+70+self.box_height*3+2
                        self.display_surface.blit(self.iron_gem_image, self.iron_gem_rect)
                    if column == 23:
                        self.iron_block_rect.x = self.gap+self.box_width*j+5*(j+1)+4
                        self.iron_block_rect.y = self.inv_y+70+self.box_height*3+4
                        self.display_surface.blit(self.iron_block_image, self.iron_block_rect)
                    if column == 24:
                        self.raw_mythril_ore_rect.x = self.gap+self.box_width*j+5*(j+1)+2
                        self.raw_mythril_ore_rect.y = self.inv_y+70+self.box_height*3+2
                        self.display_surface.blit(self.raw_mythril_ore_image, self.raw_mythril_ore_rect)
                    if column == 25:
                        self.mythril_gem_rect.x = self.gap+self.box_width*j+5*(j+1)+2
                        self.mythril_gem_rect.y = self.inv_y+70+self.box_height*3+2
                        self.display_surface.blit(self.mythril_gem_image, self.mythril_gem_rect)
                    if column == 26:
                        self.mythril_block_rect.x = self.gap+self.box_width*j+5*(j+1)+4
                        self.mythril_block_rect.y = self.inv_y+70+self.box_height*3+4
                        self.display_surface.blit(self.mythril_block_image, self.mythril_block_rect)
                    if column == 27:
                        self.raw_amethyst_ore_rect.x = self.gap+self.box_width*j+5*(j+1)+2
                        self.raw_amethyst_ore_rect.y = self.inv_y+70+self.box_height*3+2
                        self.display_surface.blit(self.raw_amethyst_ore_image, self.raw_amethyst_ore_rect)
                    if column == 28:
                        self.amethyst_gem_rect.x = self.gap+self.box_width*j+5*(j+1)+2
                        self.amethyst_gem_rect.y = self.inv_y+70+self.box_height*3+2
                        self.display_surface.blit(self.amethyst_gem_image, self.amethyst_gem_rect)
                    if column == 29:
                        self.amethyst_block_rect.x = self.gap+self.box_width*j+5*(j+1)+4
                        self.amethyst_block_rect.y = self.inv_y+70+self.box_height*3+4
                        self.display_surface.blit(self.amethyst_block_image, self.amethyst_block_rect)
                    if column == 30:
                        self.raw_adamantite_ore_rect.x = self.gap+self.box_width*j+5*(j+1)+2
                        self.raw_adamantite_ore_rect.y = self.inv_y+70+self.box_height*3+2
                        self.display_surface.blit(self.raw_adamantite_ore_image, self.raw_adamantite_ore_rect)
                    if column == 31:
                        self.adamantite_gem_rect.x = self.gap+self.box_width*j+5*(j+1)+2
                        self.adamantite_gem_rect.y = self.inv_y+70+self.box_height*3+2
                        self.display_surface.blit(self.adamantite_gem_image, self.adamantite_gem_rect)
                    if column == 32:
                        self.adamantite_block_rect.x = self.gap+self.box_width*j+5*(j+1)+4
                        self.adamantite_block_rect.y = self.inv_y+70+self.box_height*3+4
                        self.display_surface.blit(self.adamantite_block_image, self.adamantite_block_rect)

        if self.inventory_storage[self.isi[0]][self.isi[1]-1] == 11:
            self.game.player.weapon_index = 0
        elif self.inventory_storage[self.isi[0]][self.isi[1]-1] == 12:
            self.game.player.weapon_index = 1
        elif self.inventory_storage[self.isi[0]][self.isi[1]-1] == 13:
            self.game.player.weapon_index = 2
        elif self.inventory_storage[self.isi[0]][self.isi[1]-1] == 14:
            self.game.player.weapon_index = 3
        elif self.inventory_storage[self.isi[0]][self.isi[1]-1] == 15:
            self.game.player.weapon_index = 4
        else:
            self.game.player.weapon_index = None

        for i2, row in enumerate(self.storage_count):
            for j2, column in enumerate(row):
                if i2 == 3:
                    self.text = self.font.render(str(column), True, BLACK)
                    self.text_rect = self.text.get_rect()
                    if column < 10:
                        self.text_rect.x = self.gap+self.box_width*(j2+1)+5*(j2-2)
                    if column > 9 and column < 17:
                        self.text_rect.x = self.gap+self.box_width*(j2+1)+5*(j2-2)-9
                    self.text_rect.y = self.inv_y+80*4+27
                    if column != 0:
                        self.display_surface.blit(self.text, self.text_rect)

        self.input(player) 
        if player.open_inventory:
            self.draw_inventory()

class Coin(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = BLOCK_LAYER
        self.groups = self.game.all_sprites, self.game.coins
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.display_surface = pygame.display.get_surface()

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.animation_loop = 1

        self.coin_sprite_1 = self.game.coin_spritesheet.get_sprite(0, 0, 10, 10).convert_alpha()
        self.coin_sprite_2 = self.game.coin_spritesheet.get_sprite(10, 0, 10, 10).convert_alpha()
        self.coin_sprite_3 = self.game.coin_spritesheet.get_sprite(20, 0, 10, 10).convert_alpha()
        self.coin_sprite_4 = self.game.coin_spritesheet.get_sprite(30, 0, 10, 10).convert_alpha()

        self.image_list = [pygame.transform.scale(self.coin_sprite_1, (25, 25)), pygame.transform.scale(self.coin_sprite_2, (25, 25)), 
                    pygame.transform.scale(self.coin_sprite_3, (25, 25)), pygame.transform.scale(self.coin_sprite_4, (25, 25))]

        self.image = GOLD_COIN_IMAGE
        self.image = pygame.transform.scale(self.image, (25, 25))

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def animate(self):
        self.image = self.image_list[math.floor(self.animation_loop)]
        self.image.set_colorkey(BLACK)
        self.animation_loop += ANIMATION_ITERATION
        if self.animation_loop > 4:
            self.animation_loop = 1

class Chest(pygame.sprite.Sprite):
    def __init__(self, game, x, y, storage, storage_count):
        self.game = game
        self._layer = BLOCK_LAYER
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font('fonts/JetBrainsMono-Regular.ttf', 22)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.gap = 277.5
        self.inv_y = 400
        self.box_width = 75
        self.box_height = 75
        self.add_value = 80
        self.csi = [0, 0]               # chest selection index
        self.chi = [0, 0]               # chest hover index
        self.hovering = False
        self.selected = True
        
        self.image = self.game.element_spritesheet.get_sprite(0, 0, 16, 16, BLACK).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.name_rect = pygame.Rect(self.gap, 10, 150, 50)
        self.name_text = self.font.render("Chest", True, BLACK)
        self.name_text_rect = self.name_text.get_rect()
        self.name_text_rect.x = self.gap + 10
        self.name_text_rect.y = 20

        self.beef_image = self.enlarge(BEEF_IMAGE)
        self.beef_rect = self.beef_image.get_rect()
        self.calamari_image = self.enlarge(CALAMARI_IMAGE)
        self.calamari_rect = self.calamari_image.get_rect()
        self.fish_image = self.enlarge(FISH_IMAGE)
        self.fish_rect = self.fish_image.get_rect()
        self.honey_image = self.enlarge(HONEY_IMAGE)
        self.honey_rect = self.honey_image.get_rect()
        self.noodle_image = self.enlarge(NOODLE_IMAGE)
        self.noodle_rect = self.noodle_image.get_rect()
        self.shrimp_image = self.enlarge(SHRIMP_IMAGE)
        self.shrimp_rect = self.shrimp_image.get_rect()
        self.sushi_image = self.enlarge(SUSHI_IMAGE)
        self.sushi_rect = self.sushi_image.get_rect()
        self.sushi_image_2 = self.enlarge(SUSHI_IMAGE_2)
        self.sushi_rect_2 = self.sushi_image_2.get_rect()
        self.yakitori_image = self.enlarge(YAKITORI_IMAGE)
        self.yakitori_rect = self.yakitori_image.get_rect()

        self.sword_image = self.enlarge_2(SWORD_FULL)
        self.sword_rect = self.sword_image.get_rect()
        self.axe_image = self.enlarge(AXE_FULL)
        self.axe_rect = self.axe_image.get_rect()
        self.lance_image = pygame.transform.rotate(LANCE_FULL, -45)
        self.lance_rect = self.lance_image.get_rect()
        self.rapier_image = self.enlarge_3(RAPIER_FULL)
        self.rapier_rect = self.rapier_image.get_rect()
        self.sai_image = self.enlarge_4(SAI_FULL)
        self.sai_rect = self.sai_image.get_rect()

        self.coin_image = pygame.transform.scale(self.game.coin_spritesheet.get_sprite(0, 0, 10, 10, BLACK).convert_alpha(), (60, 60))
        self.coin_rect = self.coin_image.get_rect()

        self.wood_image = pygame.transform.scale(self.game.house_spritesheet.get_sprite(496, 288, 16, 16, BLACK).convert_alpha(), (70, 70))
        self.wood_rect = self.wood_image.get_rect()
        self.health_drink_image = pygame.transform.scale(self.game.house_spritesheet.get_sprite(336, 192, 16, 16, BLACK).convert_alpha(), (65, 65))
        self.health_drink_rect = self.health_drink_image.get_rect()
        self.poison_drink_image = pygame.transform.scale(self.game.house_spritesheet.get_sprite(336, 208, 16, 16, BLACK).convert_alpha(), (65, 65))
        self.poison_drink_rect = self.poison_drink_image.get_rect()
        self.lettuce_juice_image = pygame.transform.scale(self.game.house_spritesheet.get_sprite(336, 224, 16, 16, BLACK).convert_alpha(), (65, 65))
        self.lettuce_juice_rect = self.lettuce_juice_image.get_rect()
        self.empty_bottle_image = pygame.transform.scale(self.game.house_spritesheet.get_sprite(336, 240, 16, 16, BLACK).convert_alpha(), (65, 65))
        self.empty_bottle_rect = self.empty_bottle_image.get_rect()

        self.raw_iron_ore_image = pygame.transform.scale(self.game.terrain_spritesheet.get_sprite(0, 224, 16, 16, BLACK).convert_alpha(), (70, 70))
        self.raw_iron_ore_rect = self.raw_iron_ore_image.get_rect()
        self.iron_gem_image = pygame.transform.scale(self.game.terrain_spritesheet.get_sprite(0, 240, 16, 16, BLACK).convert_alpha(), (70, 70))
        self.iron_gem_rect = self.iron_gem_image.get_rect()
        self.iron_block_image = pygame.transform.scale(self.game.terrain_spritesheet.get_sprite(0, 256, 16, 16, BLACK).convert_alpha(), (65, 65))
        self.iron_block_rect = self.iron_block_image.get_rect()

        self.raw_mythril_ore_image = pygame.transform.scale(self.game.terrain_spritesheet.get_sprite(16, 224, 16, 16, BLACK).convert_alpha(), (70, 70))
        self.raw_mythril_ore_rect = self.raw_mythril_ore_image.get_rect()
        self.mythril_gem_image = pygame.transform.scale(self.game.terrain_spritesheet.get_sprite(16, 240, 16, 16, BLACK).convert_alpha(), (70, 70))
        self.mythril_gem_rect = self.mythril_gem_image.get_rect()
        self.mythril_block_image = pygame.transform.scale(self.game.terrain_spritesheet.get_sprite(16, 256, 16, 16, BLACK).convert_alpha(), (65, 65))
        self.mythril_block_rect = self.mythril_block_image.get_rect()

        self.raw_amethyst_ore_image = pygame.transform.scale(self.game.terrain_spritesheet.get_sprite(32, 224, 16, 16, BLACK).convert_alpha(), (70, 70))
        self.raw_amethyst_ore_rect = self.raw_amethyst_ore_image.get_rect()
        self.amethyst_gem_image = pygame.transform.scale(self.game.terrain_spritesheet.get_sprite(32, 240, 16, 16, BLACK).convert_alpha(), (70, 70))
        self.amethyst_gem_rect = self.amethyst_gem_image.get_rect()
        self.amethyst_block_image = pygame.transform.scale(self.game.terrain_spritesheet.get_sprite(32, 256, 16, 16, BLACK).convert_alpha(), (65, 65))
        self.amethyst_block_rect = self.amethyst_block_image.get_rect()

        self.raw_adamantite_ore_image = pygame.transform.scale(self.game.terrain_spritesheet.get_sprite(48, 224, 16, 16, BLACK).convert_alpha(), (70, 70))
        self.raw_adamantite_ore_rect = self.raw_adamantite_ore_image.get_rect()
        self.adamantite_gem_image = pygame.transform.scale(self.game.terrain_spritesheet.get_sprite(48, 240, 16, 16, BLACK).convert_alpha(), (70, 70))
        self.adamantite_gem_rect = self.adamantite_gem_image.get_rect()
        self.adamantite_block_image = pygame.transform.scale(self.game.terrain_spritesheet.get_sprite(48, 256, 16, 16, BLACK).convert_alpha(), (65, 65))
        self.adamantite_block_rect = self.adamantite_block_image.get_rect()

        self.storage_index = 0
        self.open_storage = False
        self.storage = storage
        self.storage_count = storage_count
        self.item_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]

        self.inv_rect = pygame.Rect(self.gap, 50, WIDTH-2*self.gap, self.box_height*2+15)

    def enlarge(self, image):
        return pygame.transform.scale(image, (75, 75))
    def enlarge_2(self, image):
        img = pygame.transform.scale(image, (28, 70))
        return pygame.transform.rotate(img, -45)
    def enlarge_3(self, image):
        img = pygame.transform.scale(image, (46, 70))
        return pygame.transform.rotate(img, 45)
    def enlarge_4(self, image):
        img = pygame.transform.scale(image, (37, 70))
        return pygame.transform.rotate(img, -45)

    def input(self):
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_pressed = pygame.mouse.get_pressed()
        self.chest_button = Button(self.rect.x, self.rect.y, TILESIZE, TILESIZE, BLACK, WHITE, '', 14)

        if self.chest_button.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.open_storage = True
            self.game.player.open_inventory = True
        
        self.button_1_1 = self.button_def(5, 0, 5, 0)
        if self.button_1_1.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.storage_index = 1
            self.csi = [1, 1]
        if self.button_1_1.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.chi = [1, 1]
        self.button_1_2 = self.button_def(10, 1, 5, 0)
        if self.button_1_2.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.storage_index = 2
            self.csi = [1, 2]
        if self.button_1_2.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.chi = [1, 2]
        self.button_1_3 = self.button_def(15, 2, 5, 0)
        if self.button_1_3.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.storage_index = 3
            self.csi = [1, 3]
        if self.button_1_3.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.chi = [1, 3]
        self.button_1_4 = self.button_def(20, 3, 5, 0)
        if self.button_1_4.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.storage_index = 4
            self.csi = [1, 4]
        if self.button_1_4.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.chi = [1, 4]
        self.button_1_5 = self.button_def(25, 4, 5, 0)
        if self.button_1_5.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.storage_index = 5
            self.csi = [1, 5]
        if self.button_1_5.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.chi = [1, 5]
        self.button_1_6 = self.button_def(30, 5, 5, 0)
        if self.button_1_6.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.storage_index = 6
            self.csi = [1, 6]
        if self.button_1_6.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.chi = [1, 6]
        self.button_1_7 = self.button_def(35, 6, 5, 0)
        if self.button_1_7.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.storage_index = 7
            self.csi = [1, 7]
        if self.button_1_7.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.chi = [1, 7]
        self.button_1_8 = self.button_def(40, 7, 5, 0)
        if self.button_1_8.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.storage_index = 8
            self.csi = [1, 8]
        if self.button_1_8.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.chi = [1, 8]
        self.button_1_9 = self.button_def(45, 8, 5, 0)
        if self.button_1_9.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.storage_index = 9
            self.csi = [1, 9]
        if self.button_1_9.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.chi = [1, 9]

        self.button_2_1 = self.button_def(5, 0, 10, 1)
        if self.button_2_1.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.storage_index = 11
            self.csi = [2, 1]
        if self.button_2_1.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.chi = [2, 1]
        self.button_2_2 = self.button_def(10, 1, 10, 1)
        if self.button_2_2.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.storage_index = 12
            self.csi = [2, 2]
        if self.button_2_2.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.chi = [2, 2]
        self.button_2_3 = self.button_def(15, 2, 10, 1)
        if self.button_2_3.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.storage_index = 13
            self.csi = [2, 3]
        if self.button_2_3.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.chi = [2, 3]
        self.button_2_4 = self.button_def(20, 3, 10, 1)
        if self.button_2_4.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.storage_index = 14
            self.csi = [2, 4]
        if self.button_2_4.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.chi = [2, 4]
        self.button_2_5 = self.button_def(25, 4, 10, 1)
        if self.button_2_5.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.storage_index = 15
            self.csi = [2, 5]
        if self.button_2_5.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.chi = [2, 5]
        self.button_2_6 = self.button_def(30, 5, 10, 1)
        if self.button_2_6.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.storage_index = 16
            self.csi = [2, 6]
        if self.button_2_6.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.chi = [2, 6]
        self.button_2_7 = self.button_def(35, 6, 10, 1)
        if self.button_2_7.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.storage_index = 17
            self.csi = [2, 7]
        if self.button_2_7.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.chi = [2, 7]
        self.button_2_8 = self.button_def(40, 7, 10, 1)
        if self.button_2_8.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.storage_index = 18
            self.csi = [2, 8]
        if self.button_2_8.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.chi = [2, 8]
        self.button_2_9 = self.button_def(45, 8, 10, 1)
        if self.button_2_9.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.storage_index = 19
            self.csi = [2, 9]
        if self.button_2_9.is_hovering_bool(self.mouse_pos):
            self.hovering = True
            self.chi = [2, 9]

    def generate_loot(self):
        if self.open_storage:
            for i, row in enumerate(self.storage):
                for j, column in enumerate(row):
                    if self.storage_count[i][j] > 0:
                        if column == 1:
                            self.beef_rect.x = self.gap+self.box_width*j+5*(j+1)-2.5
                            self.beef_rect.y = 55+80*i-2.5
                            self.display_surface.blit(self.beef_image, self.beef_rect)
                        if column == 2:
                            self.calamari_rect.x = self.gap+self.box_width*j+5*(j+1)-3
                            self.calamari_rect.y = 55+80*i
                            self.display_surface.blit(self.calamari_image, self.calamari_rect)
                        if column == 3:
                            self.fish_rect.x = self.gap+self.box_width*j+5*(j+1)
                            self.fish_rect.y = 55+80*i
                            self.display_surface.blit(self.fish_image, self.fish_rect)
                        if column == 4:
                            self.honey_rect.x = self.gap+self.box_width*j+5*(j+1)
                            self.honey_rect.y = 55+80*i
                            self.display_surface.blit(self.honey_image, self.honey_rect)
                        if column == 5:
                            self.noodle_rect.x = self.gap+self.box_width*j+5*(j+1)
                            self.noodle_rect.y = 55+80*i
                            self.display_surface.blit(self.noodle_image, self.noodle_rect)
                        if column == 6:
                            self.shrimp_rect.x = self.gap+self.box_width*j+5*(j+1)
                            self.shrimp_rect.y = 55+80*i
                            self.display_surface.blit(self.shrimp_image, self.shrimp_rect)
                        if column == 7:
                            self.sushi_rect.x = self.gap+self.box_width*j+5*(j+1)
                            self.sushi_rect.y = 55+80*i
                            self.display_surface.blit(self.sushi_image, self.sushi_rect)
                        if column == 8:
                            self.sushi_rect_2.x = self.gap+self.box_width*j+5*(j+1)
                            self.sushi_rect_2.y = 55+80*i
                            self.display_surface.blit(self.sushi_image_2, self.sushi_rect_2)
                        if column == 9:
                            self.yakitori_rect.x = self.gap+self.box_width*j+5*(j+1)
                            self.yakitori_rect.y = 55+80*i
                            self.display_surface.blit(self.yakitori_image, self.yakitori_rect)

                        if column == 10:
                            self.coin_rect.x = self.gap+self.box_width*j+5*(j+1)+8
                            self.coin_rect.y = 55+80*i+8
                            self.display_surface.blit(self.coin_image, self.coin_rect)

                        if column == 11:
                            self.sword_rect.x = self.gap+self.box_width*j+5*(j+1)
                            self.sword_rect.y = 55+80*i
                            self.display_surface.blit(self.sword_image, self.sword_rect)
                        if column == 12:
                            self.axe_rect.x = self.gap+self.box_width*j+5*(j+1)
                            self.axe_rect.y = 55+80*i
                            self.display_surface.blit(self.axe_image, self.axe_rect)
                        if column == 13:
                            self.lance_rect.x = self.gap+self.box_width*j+5*(j+1)+5
                            self.lance_rect.y = 55+80*i+5
                            self.display_surface.blit(self.lance_image, self.lance_rect)
                        if column == 14:
                            self.rapier_rect.x = self.gap+self.box_width*j+5*(j+1)-6
                            self.rapier_rect.y = 55+80*i-6
                            self.display_surface.blit(self.rapier_image, self.rapier_rect)
                        if column == 15:
                            self.sai_rect.x = self.gap+self.box_width*j+5*(j+1)
                            self.sai_rect.y = 55+80*i
                            self.display_surface.blit(self.sai_image, self.sai_rect)

                        if column == 16:
                            self.wood_rect.x = self.gap+self.box_width*j+5*(j+1)
                            self.wood_rect.y = 55+80*i+5
                            self.display_surface.blit(self.wood_image, self.wood_rect)
                        if column == 17:
                            self.health_drink_rect.x = self.gap+self.box_width*j+5*(j+1)+3
                            self.health_drink_rect.y = 55+80*i+5
                            self.display_surface.blit(self.health_drink_image, self.health_drink_rect)
                        if column == 18:
                            self.poison_drink_rect.x = self.gap+self.box_width*j+5*(j+1)+3
                            self.poison_drink_rect.y = 55+80*i+5
                            self.display_surface.blit(self.poison_drink_image, self.poison_drink_rect)
                        if column == 19:
                            self.lettuce_juice_rect.x = self.gap+self.box_width*j+5*(j+1)+3
                            self.lettuce_juice_rect.y = 55+80*i+5
                            self.display_surface.blit(self.lettuce_juice_image, self.lettuce_juice_rect)
                        if column == 20:
                            self.empty_bottle_rect.x = self.gap+self.box_width*j+5*(j+1)+3
                            self.empty_bottle_rect.y = 55+80*i+5
                            self.display_surface.blit(self.empty_bottle_image, self.empty_bottle_rect)

                        if column == 21:
                            self.raw_iron_ore_rect.x = self.gap+self.box_width*j+5*(j+1)+2
                            self.raw_iron_ore_rect.y = 55+80*i+2
                            self.display_surface.blit(self.raw_iron_ore_image, self.raw_iron_ore_rect)
                        if column == 22:
                            self.iron_gem_rect.x = self.gap+self.box_width*j+5*(j+1)+2
                            self.iron_gem_rect.y = 55+80*i+2
                            self.display_surface.blit(self.iron_gem_image, self.iron_gem_rect)
                        if column == 23:
                            self.iron_block_rect.x = self.gap+self.box_width*j+5*(j+1)+4
                            self.iron_block_rect.y = 55+80*i+4
                            self.display_surface.blit(self.iron_block_image, self.iron_block_rect)
                        if column == 24:
                            self.raw_mythril_ore_rect.x = self.gap+self.box_width*j+5*(j+1)+2
                            self.raw_mythril_ore_rect.y = 55+80*i+2
                            self.display_surface.blit(self.raw_mythril_ore_image, self.raw_mythril_ore_rect)
                        if column == 25:
                            self.mythril_gem_rect.x = self.gap+self.box_width*j+5*(j+1)+2
                            self.mythril_gem_rect.y = 55+80*i+2
                            self.display_surface.blit(self.mythril_gem_image, self.mythril_gem_rect)
                        if column == 26:
                            self.mythril_block_rect.x = self.gap+self.box_width*j+5*(j+1)+4
                            self.mythril_block_rect.y = 55+80*i+4
                            self.display_surface.blit(self.mythril_block_image, self.mythril_block_rect)
                        if column == 27:
                            self.raw_amethyst_ore_rect.x = self.gap+self.box_width*j+5*(j+1)+2
                            self.raw_amethyst_ore_rect.y = 55+80*i+2
                            self.display_surface.blit(self.raw_amethyst_ore_image, self.raw_amethyst_ore_rect)
                        if column == 28:
                            self.amethyst_gem_rect.x = self.gap+self.box_width*j+5*(j+1)+2
                            self.amethyst_gem_rect.y = 55+80*i+2
                            self.display_surface.blit(self.amethyst_gem_image, self.amethyst_gem_rect)
                        if column == 29:
                            self.amethyst_block_rect.x = self.gap+self.box_width*j+5*(j+1)+4
                            self.amethyst_block_rect.y = 55+80*i+4
                            self.display_surface.blit(self.amethyst_block_image, self.amethyst_block_rect)
                        if column == 30:
                            self.raw_adamantite_ore_rect.x = self.gap+self.box_width*j+5*(j+1)+2
                            self.raw_adamantite_ore_rect.y = 55+80*i+2
                            self.display_surface.blit(self.raw_adamantite_ore_image, self.raw_adamantite_ore_rect)
                        if column == 31:
                            self.adamantite_gem_rect.x = self.gap+self.box_width*j+5*(j+1)+2
                            self.adamantite_gem_rect.y = 55+80*i+2
                            self.display_surface.blit(self.adamantite_gem_image, self.adamantite_gem_rect)
                        if column == 32:
                            self.adamantite_block_rect.x = self.gap+self.box_width*j+5*(j+1)+4
                            self.adamantite_block_rect.y = 55+80*i+4
                            self.display_surface.blit(self.adamantite_block_image, self.adamantite_block_rect)

            for i, row in enumerate(self.storage_count):
                for j, column in enumerate(row):
                    self.text = self.font.render(str(column), True, BLACK)
                    self.text_rect = self.text.get_rect()
                    if column < 10:
                        self.text_rect.x = self.gap+self.box_width*(j+1)+5*(j-2)
                    if column > 9 and column < 17:
                        self.text_rect.x = self.gap+self.box_width*(j+1)+5*(j-2)-9
                    self.text_rect.y = 27+80*(i+1)
                    if column != 0:
                        self.display_surface.blit(self.text, self.text_rect)
        
        if self.hovering and self.open_storage:
            if self.storage[self.chi[0]-1][self.chi[1]-1] == 1:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 86, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 80, 40)
                info_word = self.font.render("Beef", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+15
                info_word_rect.y = self.mouse_pos[1]+6
            if self.storage[self.chi[0]-1][self.chi[1]-1] == 2:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 116, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 110, 40)
                info_word = self.font.render("Calamari", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+6
                info_word_rect.y = self.mouse_pos[1]+6
            if self.storage[self.chi[0]-1][self.chi[1]-1] == 3:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 86, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 80, 40)
                info_word = self.font.render("Fish", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+15
                info_word_rect.y = self.mouse_pos[1]+6
            if self.storage[self.chi[0]-1][self.chi[1]-1] == 4:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 86, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 80, 40)
                info_word = self.font.render("Honey", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.storage[self.chi[0]-1][self.chi[1]-1] == 5:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 96, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 90, 40)
                info_word = self.font.render("Noodle", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.storage[self.chi[0]-1][self.chi[1]-1] == 6:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 96, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 90, 40)
                info_word = self.font.render("Shrimp", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.storage[self.chi[0]-1][self.chi[1]-1] == 7:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 86, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 80, 40)
                info_word = self.font.render("Sushi", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.storage[self.chi[0]-1][self.chi[1]-1] == 8:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 86, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 80, 40)
                info_word = self.font.render("Sushi", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.storage[self.chi[0]-1][self.chi[1]-1] == 9:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 116, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 110, 40)
                info_word = self.font.render("Yakitori", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+6
                info_word_rect.y = self.mouse_pos[1]+6
            if self.storage[self.chi[0]-1][self.chi[1]-1] == 10:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 86, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 80, 40)
                info_word = self.font.render("Coin", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+15
                info_word_rect.y = self.mouse_pos[1]+6
            if self.storage[self.chi[0]-1][self.chi[1]-1] == 11:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 96, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 90, 40)
                info_word = self.font.render("Sword", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.storage[self.chi[0]-1][self.chi[1]-1] == 12:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 86, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 80, 40)
                info_word = self.font.render("Axe", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+15
                info_word_rect.y = self.mouse_pos[1]+6
            if self.storage[self.chi[0]-1][self.chi[1]-1] == 13:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 96, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 90, 40)
                info_word = self.font.render("Lance", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.storage[self.chi[0]-1][self.chi[1]-1] == 14:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 96, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 90, 40)
                info_word = self.font.render("Rapier", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.storage[self.chi[0]-1][self.chi[1]-1] == 15:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 86, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 80, 40)
                info_word = self.font.render("Sai", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+15
                info_word_rect.y = self.mouse_pos[1]+6
            if self.storage[self.chi[0]-1][self.chi[1]-1] == 16:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 121, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 115, 40)
                info_word = self.font.render("Log Pile", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.storage[self.chi[0]-1][self.chi[1]-1] == 17:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 186, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 180, 40)
                info_word = self.font.render("Health Potion", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.storage[self.chi[0]-1][self.chi[1]-1] == 18:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 186, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 180, 40)
                info_word = self.font.render("Poison Potion", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.storage[self.chi[0]-1][self.chi[1]-1] == 19:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 186, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 180, 40)
                info_word = self.font.render("Lettuce Juice", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.storage[self.chi[0]-1][self.chi[1]-1] == 20:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 176, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 170, 40)
                info_word = self.font.render("Empty Bottle", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.storage[self.chi[0]-1][self.chi[1]-1] == 21:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 186, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 180, 40)
                info_word = self.font.render("Raw Iron Ore", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.storage[self.chi[0]-1][self.chi[1]-1] == 22:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 166, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 160, 40)
                info_word = self.font.render("Iron Gem", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.storage[self.chi[0]-1][self.chi[1]-1] == 23:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 176, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 170, 40)
                info_word = self.font.render("Iron Block", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.storage[self.chi[0]-1][self.chi[1]-1] == 24:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 216, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 210, 40)
                info_word = self.font.render("Raw Mythril Ore", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.storage[self.chi[0]-1][self.chi[1]-1] == 25:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 186, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 180, 40)
                info_word = self.font.render("Mythril Gem", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.storage[self.chi[0]-1][self.chi[1]-1] == 26:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 186, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 180, 40)
                info_word = self.font.render("Mythril Block", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.storage[self.chi[0]-1][self.chi[1]-1] == 27:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 226, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 220, 40)
                info_word = self.font.render("Raw Amethyst Ore", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.storage[self.chi[0]-1][self.chi[1]-1] == 28:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 186, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 180, 40)
                info_word = self.font.render("Amethyst Gem", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.storage[self.chi[0]-1][self.chi[1]-1] == 29:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 206, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 200, 40)
                info_word = self.font.render("Amethyst Block", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.storage[self.chi[0]-1][self.chi[1]-1] == 30:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 256, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 250, 40)
                info_word = self.font.render("Raw Adamantite Ore", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.storage[self.chi[0]-1][self.chi[1]-1] == 31:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 196, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 190, 40)
                info_word = self.font.render("Adamantite Gem", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.storage[self.chi[0]-1][self.chi[1]-1] == 32:
                info_rect_border = pygame.Rect(self.mouse_pos[0], self.mouse_pos[1], 216, 44)
                info_rect = pygame.Rect(self.mouse_pos[0]+3, self.mouse_pos[1]+2, 210, 40)
                info_word = self.font.render("Adamantite Block", True, WHITE)
                info_word_rect = info_word.get_rect()
                info_word_rect.x = self.mouse_pos[0]+10
                info_word_rect.y = self.mouse_pos[1]+6
            if self.storage[self.chi[0]-1][self.chi[1]-1] in self.item_list:
                pygame.draw.rect(self.display_surface, VIOLET, info_rect_border)
                pygame.draw.rect(self.display_surface, BLACK, info_rect)
                self.display_surface.blit(info_word, info_word_rect)
        self.hovering = False

    def button_def(self, add_to_x, mul_to_x, add_to_y, mul_to_y):
        return Button(self.gap+add_to_x+self.box_width*mul_to_x, 50+add_to_y+self.box_height*mul_to_y, self.box_width, self.box_height, BLACK, WHITE, '', 14)

    def draw_selection_rect(self, mul_to_x, add_to_y, mul_to_y):
        self.border_rect = pygame.Rect(self.gap+self.add_value*mul_to_x, 50+add_to_y+self.box_height*mul_to_y, self.box_width+10, self.box_height+10)
        pygame.draw.rect(self.display_surface, BLACK, self.border_rect)

    def draw_storage(self):
        pygame.draw.rect(self.display_surface, GREY, self.inv_rect)
        pygame.draw.rect(self.display_surface, GREY, self.name_rect)

        self.display_surface.blit(self.name_text, self.name_text_rect)

        if self.storage_index == 1:
            self.draw_selection_rect(0, 0, 0)
        elif self.storage_index == 2:
            self.draw_selection_rect(1, 0, 0)
        elif self.storage_index == 3:
            self.draw_selection_rect(2, 0, 0)
        elif self.storage_index == 4:
            self.draw_selection_rect(3, 0, 0)
        elif self.storage_index == 5:
            self.draw_selection_rect(4, 0, 0)
        elif self.storage_index == 6:
            self.draw_selection_rect(5, 0, 0)
        elif self.storage_index == 7:
            self.draw_selection_rect(6, 0, 0)
        elif self.storage_index == 8:
            self.draw_selection_rect(7, 0, 0)
        elif self.storage_index == 9:
            self.draw_selection_rect(8, 0, 0)

        if self.storage_index == 11:
            self.draw_selection_rect(0, 5, 1)
        elif self.storage_index == 12:
            self.draw_selection_rect(1, 5, 1)
        elif self.storage_index == 13:
            self.draw_selection_rect(2, 5, 1)
        elif self.storage_index == 14:
            self.draw_selection_rect(3, 5, 1)
        elif self.storage_index == 15:
            self.draw_selection_rect(4, 5, 1)
        elif self.storage_index == 16:
            self.draw_selection_rect(5, 5, 1)
        elif self.storage_index == 17:
            self.draw_selection_rect(6, 5, 1)
        elif self.storage_index == 18:
            self.draw_selection_rect(7, 5, 1)
        elif self.storage_index == 19:
            self.draw_selection_rect(8, 5, 1)

        for j in range(2):
            width_gap = 5*(j+1)
            for i in range(9):
                space = 5*(i+1)
                small_rect_x = self.box_width*i
                width = self.box_width
                height = self.box_height
                self.small_rect = pygame.Rect(self.gap+space+small_rect_x, 50+width_gap+self.box_height*j, width, height)
                pygame.draw.rect(self.display_surface, WHITE, self.small_rect)

        self.chest_close_button = self.button_def(60, 9, 5, 0)
        self.close_button_rect = pygame.Rect(self.gap+60+self.box_width*9, 55, self.box_width, self.box_height)
        pygame.draw.rect(self.display_surface, RED, self.close_button_rect)
        if self.chest_close_button.is_pressed(self.mouse_pos, self.mouse_pressed):
            self.open_storage = False
            self.storage_index = 0
            self.game.player.open_inventory = False

    def display(self):
        self.input()
        
        if self.open_storage:
            self.draw_storage()
            self.generate_loot()
