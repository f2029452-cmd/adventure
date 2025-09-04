import pygame, sys, random
from config import *
from sprites import *

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Adventure")
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = FONT

        self.character_spritesheet = Spritesheet('img/spritesheets/basic_spritesheet.png')
        self.blacksmith_spritesheet = Spritesheet('img/spritesheets/blacksmithSpritesheet.png')
        self.cook_spritesheet = Spritesheet('img/spritesheets/cook_spritesheet.png')
        self.potionmaker_spritesheet = Spritesheet('img/spritesheets/potionmaker_spritesheet.png')
        self.potion_maker_spritesheet_2 = Spritesheet('img/spritesheets/potion_maker.png')
        self.terrain_spritesheet = Spritesheet('img/spritesheets/TilesetNature.png')
        self.grass_spritesheet = Spritesheet('img/spritesheets/TilesetField.png')
        self.house_spritesheet = Spritesheet('img/spritesheets/TilesetHouse.png')
        self.relief_spritesheet = Spritesheet('img/spritesheets/TilesetRelief.png')
        self.water_spritesheet = Spritesheet('img/spritesheets/TilesetWater.png')
        self.element_spritesheet = Spritesheet('img/spritesheets/TilesetElement.png')
        self.floor_spritesheet = Spritesheet('img/spritesheets/TilesetFloor.png')
        self.path_spritesheet = Spritesheet('img/spritesheets/TilesetInteriorFloor.png')
        self.enemy_spritesheet = Spritesheet('img/spritesheets/enemy_spritesheet.png')
        self.water_animation = Spritesheet('img/spritesheets/water_animation.png')
        self.coin_spritesheet = Spritesheet('Treasure/Coin2.png')

        self.intro_background = pygame.transform.scale(INTRO_BG_IMAGE, (WIDTH, HEIGHT))
        self.outro_background = pygame.transform.scale(OUTRO_BG_IMAGE, (WIDTH, HEIGHT))
        self.load_background = pygame.transform.scale(LOAD_BG_IMAGE, (WIDTH, HEIGHT))
        self.background = pygame.transform.scale(BACKGROUND, (WIDTH, HEIGHT))

        self.logo = pygame.transform.scale(LOGO_IMAGE, (256, 256))
        self.logo_rect = self.logo.get_rect(x = 20, y = HEIGHT - 286)
        self.logo.set_colorkey(WHITE)
        self.logo_font = self.font.render("Dark Arts", True, BLACK)
        self.logo_font_rect = self.logo_font.get_rect(x = 30, y = HEIGHT - 90)

        self.chest_list = []
        
        self.ui = UI()
        self.inventory = Inventory(self)

        self.play_bool = False # set it to false if intro screen is needed
        self.settings = False
        self.intro_bool = True

    def createTilemap(self):
        # Quadrant - 2
        for n in range(7):
            for m in range(13):
                Ground(self).grass_ground(-m-1, -n-1)

        for n in range(4):
            for m in range(10):
                if m%4 == 0:
                    ForestTree(self, -m-4, -5, FOREST_LAYER_3)
                    PineTree(self, -m-5, -5)
                    ForestTree(self, -m-4, -7, FOREST_LAYER_1)
                    PineTree(self, -m-5, -7, FOREST_LAYER_1-1)

        # Quadrant - 1
        for n in range(7):
            for m in range(44):
                Ground(self).grass_ground(m, -n-1)
                if m%4 == 0:
                    ForestTree(self, m, -7, FOREST_LAYER_1)
                    ForestTree(self, m, -5, FOREST_LAYER_3)
        for m in range(-1, 43, 4):
            PineTree(self, m, -5)
            PineTree(self, m, -7, FOREST_LAYER_1-1)

        PineTree(self, 5, -3, FOREST_LAYER_3+1)
        PineTree(self, 11, -3, FOREST_LAYER_3+1)
        PineTree(self, 17, -3, FOREST_LAYER_3+1)
        PineTree(self, 24, -3, FOREST_LAYER_3+1)

        # Quadrant - 3
        for n in range(3):
            for m in range(52):
                if m%2 == 0:
                    ForestTree(self, -4-(n*4), m-3, FOREST_LAYER_3)
                    PineTree(self, -5-(n*4), m-3)
        for n in range(13):
            for m in range(51):
                Ground(self).grass_ground(-n-1, m)
            
        # Quadrant 4
        # for i in range(60):
        #     for j in range(60):
        #         Ground(self).grass_ground(j, i)
        

        for i, row in enumerate(WORLD_MAP):
            for j, column in enumerate(row):
                if column == -1:
                    Water(self, j, i)
                if column == -2:
                    Light_Brick_Road(self).road_left_up_border(j, i)
                if column == -3:
                    Light_Brick_Road(self).road_left_down_border(j, i)
                if column == -4:
                    Light_Brick_Road(self).road_right_up_border(j, i)
                if column == -5:
                    Light_Brick_Road(self).road_right_down_border(j, i)
                if column == -6:
                    Light_Brick_Road(self).road_upper_border(j, i)
                if column == -7:
                    Light_Brick_Road(self).road_lower_border(j, i)
                if column == -8:
                    Light_Brick_Road(self).road_left_border(j, i)
                if column == -9:
                    Light_Brick_Road(self).road_right_border(j, i)
                if column == 1:
                    ForestTree(self, j, i)
                if column == 2:
                    Tree(self, j, i)
                if column == 3:
                    PineTree(self, j, i)
                if column == 4:
                    pass
                if column == 5:
                    self.enemy = Blue_fire_spirit(self, j, i)
                if column == 6:
                    Light_Brick_Road(self).road_upper_border(j, i)
                    self.player = Player(self, j, i)
                if column == 7:
                    Light_Brick_Road(self).road_left_up_corner(j, i)
                if column == 8:
                    Light_Brick_Road(self).road_left_down_corner(j, i)
                if column == 9:
                    Light_Brick_Road(self).road_right_up_corner(j, i)
                if column == 10:
                    Light_Brick_Road(self).road_right_down_corner(j, i)
                if column == 11:
                    Buildings(self).house1(j, i)
                if column == 12:
                    Buildings(self).house2(j, i)
                if column == 13:
                    Buildings(self).house3(j, i)
                if column == 14:
                    Buildings(self).house4(j, i)
                if column == 15:
                    Buildings(self).mini_house(j, i)
                if column == 16:
                    Buildings(self).food_shop(j, i)
                if column == 17:
                    Buildings(self).post_office(j, i)
                if column == 18:
                    Buildings(self).mill(j, i)
                if column == 19:
                    Buildings(self).warehouse(j, i)
                if column == 20:
                    Buildings(self).armory(j, i)
                if column == 21:
                    Buildings(self).garrison(j, i)
                if column == 22:
                    Buildings(self).lumber_camp(j, i)
                if column == 23:
                    Buildings(self).military_watchtower(j, i)
                if column == 24:
                    Fence(self).fence_horizontal(j, i)
                if column == 25:
                    Fence(self).fence_vertical(j, i)
                if column == 26:
                    Light_Brick_Road(self).road_plain(j, i)
                if column == 27:
                    Ground(self).dirt_ground(j, i)
                if column == 28:
                    Ground(self).flower_bush(j, i)
                if column == 29:
                    Ground(self).dirt_path(j, i)
                if column == 30:
                    Buildings(self).stone_brick(j, i)
                if column == 31:
                    self.smith = Master_blacksmith(self, j, i)
                if column == 32:
                    self.cook = Cook(self, j, i)
                if column == 33:
                    self.potion_maker = Potion_Maker(self, j, i)
                if column == 34:
                    Stairs(self).stone_stairs_large(j, i)
                # 31 to 38 stone items defined in Buildings class are not required
                if column == 39:
                    Water(self, j, i)
                    Buildings(self).stone_ninja(j, i)
                # 40 to 49 deepslate items defined in Buildings class are not required
                if column == 50:
                    Element(self).door1(j, i)
                if column == 51:
                    Element(self).door2(j, i)
                if column == 52:
                    Element(self).door3(j, i)
                if column == 53:
                    Element(self).window1(j, i)
                if column == 54:
                    Element(self).window2(j, i)
                if column == 55:
                    Element(self).smokestack(j, i)
                if column == 56:
                    Element(self).board1(j, i)
                if column == 57:
                    Element(self).board2(j, i)
                if column == 58:
                    Element(self).woodworking_bench(j, i)
                if column == 59:
                    Element(self).stove(j, i)
                if column == 60:
                    Element(self).cooker(j, i)
                if column == 61:
                    Element(self).cooker_and_pan(j, i)
                if column == 62:
                    Element(self).meat_basket(j, i)
                if column == 63:
                    Element(self).closed_basket(j, i)
                if column == 64:
                    Element(self).empty_cauldron(j, i)
                if column == 65:
                    Element(self).filled_cauldron(j, i)
                if column == 66:
                    Element(self).empty_open_cooker(j, i)
                if column == 67:
                    Element(self).filled_open_cooker(j, i)
                if column == 68:
                    Element(self).closed_small_basket(j, i)
                if column == 69:
                    Element(self).open_small_basket(j, i)
                if column == 70:
                    Element(self).tomato_small_basket(j, i)
                if column == 71:
                    Element(self).lettuce_small_basket(j, i)
                if column == 72:
                    Element(self).fish_small_basket(j, i)
                if column == 73:
                    Element(self).chest(j, i)
                if column == 74:
                    Element(self).pot(j, i)
                if column == 75:
                    Element(self).fence(j, i)
                if column == 76:
                    Element(self).red_pot(j, i)
                if column == 77:
                    Element(self).inscription_long(j, i)
                if column == 78:
                    Element(self).inscription_big(j, i)
                if column == 79:
                    Element(self).roofed_well_with_bucket(j, i)
                if column == 80:
                    Element(self).wheelbarrow(j, i)
                if column == 81:
                    Element(self).wheelbarrow_with_stone(j, i)
                if column == 82:
                    Element(self).paddy_field(j, i)
                if column == 83:
                    Element(self).furnace(j, i)
                if column == 84:
                    Element(self).blast_furnace(j, i)
                if column == 85:
                    Element(self).steel_foundry(j, i)
                if column == 86:
                    Element(self).anvil(j, i)
                if column == 87:
                    Element(self).post_box(j, i)
                if column == 88:
                    Element(self).handle_workbench(j, i)
                if column == 89:
                    Element(self).wood_pile(j, i)
                if column == 90:
                    Element(self).weapon_stand_1(j, i)
                if column == 91:
                    Element(self).weapon_stand_2(j, i)
                if column == 92:
                    Element(self).knife_barrel(j, i)
                if column == 93:
                    Element(self).quiver(j, i)
                if column == 94:
                    Buildings(self).military_camp(j, i)
                if column == 95:
                    Fence(self).stone_wall_horizontal(j, i)
                if column == 96:
                    Fence(self).stone_wall_vertical(j, i)

        self.storage = random.choice(STORAGE_LOOT_LIST_TIER_1)
        self.storage_count = STORAGE_LOOT_LIST_COUNT_TIER_1[STORAGE_LOOT_LIST_TIER_1.index(self.storage)]
        self.chest = Chest(self, 13, 4, self.storage, self.storage_count)
        self.storage = random.choice(STORAGE_LOOT_LIST_TIER_1)
        self.storage_count = STORAGE_LOOT_LIST_COUNT_TIER_1[STORAGE_LOOT_LIST_TIER_1.index(self.storage)]
        self.chest_1 = Chest(self, 13, 5, self.storage, self.storage_count)
        self.storage = random.choice(STORAGE_LOOT_LIST_TIER_1)
        self.storage_count = STORAGE_LOOT_LIST_COUNT_TIER_1[STORAGE_LOOT_LIST_TIER_1.index(self.storage)]
        self.chest_2 = Chest(self, 24, 44, self.storage, self.storage_count)
        self.storage = random.choice(STORAGE_LOOT_LIST_TIER_2)
        self.storage_count = STORAGE_LOOT_LIST_COUNT_TIER_2[STORAGE_LOOT_LIST_TIER_2.index(self.storage)]
        self.chest_3 = Chest(self, 24, 42, self.storage, self.storage_count)
        self.coin = Coin(self, 18, 24)

    def new(self):
        self.playing = True
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.attacks = pygame.sprite.LayeredUpdates()
        self.coins = pygame.sprite.LayeredUpdates()

        self.createTilemap()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
                    
    def update(self):
        self.all_sprites.update()

    def draw(self):
        self.screen.fill(BLACK)
        self.screen.blit(self.background, (0, 0))
        self.all_sprites.draw(self.screen)
        self.clock.tick(FPS)
        self.ui.display(self.player)
        self.inventory.display(self.player)
        self.chest.display()
        self.chest_1.display()
        self.chest_2.display()
        self.chest_3.display()
        self.smith.display()
        self.cook.display()
        self.potion_maker.display()
        self.coin.animate()

        pygame.display.update()

    def main(self):
        while self.playing:
            self.current_time = pygame.time.get_ticks()

            self.events()
            self.update()
            self.draw()
            
    def game_over(self):
        outro = True

        font = pygame.font.Font('fonts/JetBrainsMono-Medium.ttf', 100)
        text = font.render("You Died!", True, RED)
        text_rect = text.get_rect()
        text_rect.x = WIDTH/2 - 275
        text_rect.y = 100

        restart_button = Button(WIDTH/2 - 220, HEIGHT/2 - 50, 420, 100, WHITE, BLACK, "Restart", 90, BLACK)
        quit_button = Button(WIDTH/2 - 160, HEIGHT/2 + 50, 280, 100, WHITE, BLACK, "Quit", 90, BLACK)

        for sprite in self.all_sprites:
            sprite.kill()

        while outro:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    outro = False

            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()

            if restart_button.is_pressed(mouse_pos, mouse_pressed):
                self.new()
                self.main()
            if quit_button.is_pressed(mouse_pos, mouse_pressed):
                outro = False
                self.running = False

            restart_button.is_hovering(mouse_pos, YELLOW)
            quit_button.is_hovering(mouse_pos, YELLOW)
            
            self.screen.blit(self.outro_background, (0, 0))
            self.screen.blit(text, text_rect)
            self.screen.blit(restart_button.image, restart_button.rect)
            self.screen.blit(quit_button.image, quit_button.rect)
            self.clock.tick(FPS)
            pygame.display.update()

    def intro_screen(self):
        font = pygame.font.Font('fonts/JetBrainsMono-Medium.ttf', 150)

        intro = True
        title = font.render("Adventure", True, LIGHT_BLUE)
        title_rect = title.get_rect()
        title_rect.x = WIDTH/2 - 400
        title_rect.y = 100

        play_button = Button(WIDTH/2 - 140, HEIGHT/2 - 100, 280, 100, WHITE, BLACK, "Play", 90, BLACK)
        settings_button = Button(WIDTH/2 - 190, HEIGHT/2, 420, 100, WHITE, BLACK, "Settings", 90, BLACK)
        quit_button = Button(WIDTH/2 - 140, HEIGHT/2 + 100, 280, 100, WHITE, BLACK, "Quit", 90, BLACK)

        while intro:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.intro = False
                    intro = False
                    self.play_bool = True

            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()

            if play_button.is_pressed(mouse_pos, mouse_pressed):
                self.play_bool = True
                self.intro = False
                intro = False
            if settings_button.is_pressed(mouse_pos, mouse_pressed):
                self.settings = True
                self.intro = False
                intro = False
            if quit_button.is_pressed(mouse_pos, mouse_pressed):
                self.running = False
                self.intro = False
                intro = False
                self.play_bool = True

            play_button.is_hovering(mouse_pos, YELLOW)
            settings_button.is_hovering(mouse_pos, YELLOW)
            quit_button.is_hovering(mouse_pos, YELLOW)

            self.screen.blit(self.intro_background, (0, 0))
            self.screen.blit(title, title_rect)
            self.screen.blit(play_button.image, play_button.rect)
            self.screen.blit(settings_button.image, settings_button.rect)
            self.screen.blit(quit_button.image, quit_button.rect)
            self.screen.blit(self.logo, self.logo_rect)
            self.screen.blit(self.logo_font, self.logo_font_rect)
            self.clock.tick(FPS)
            pygame.display.update()

    def setting(self):
        settings_bool = True

        image = pygame.Surface((WIDTH, HEIGHT))
        image.fill(LIGHT_GREY)
        small_font = SMALL_FONT

        main_text = self.font.render("Settings: ", True, BLACK)
        main_text_rect = main_text.get_rect(x=10, y=10)
        back_button = Button(WIDTH - 140, 10, 120, 50, BLACK, WHITE, "<< Back", 25, WHITE)

        dimension_text = small_font.render(f"Dimensions: WIDTH = {WIDTH}, HEIGHT = {HEIGHT}", True, BLACK)
        dimension_text_rect = dimension_text.get_rect(x = 10, y = 55)

        map_dim_text = small_font.render(f'Map dimensions: width = 40, height = 40', True, BLACK)
        map_dim_text_rect = map_dim_text.get_rect(x = 10, y = 70)

        general_info_text = small_font.render(f'FPS = {FPS}, LAYERS = {PLAYER_LAYER}', True, BLACK)
        general_info_text_rect = general_info_text.get_rect(x = 10, y = 85)

        tilesize_text = small_font.render(f'Normal Tilesize = {TILESIZE}, Large Tilesize = {TILESIZE_LARGE}', True, BLACK)
        tilesize_text_rect = tilesize_text.get_rect(x = 10, y = 100)

        font_text = small_font.render(f'Font: JetBrains Monospace Medium', True, BLACK)
        font_text_rect = font_text.get_rect(x = 10, y = 115)

        while settings_bool:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    settings_bool = False
                    self.play_bool = True

            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()

            if back_button.is_pressed(mouse_pos, mouse_pressed):
                self.intro = True
                self.settings = False
                settings_bool = False
            back_button.is_hovering(mouse_pos, RED)

            self.screen.blit(image, (0, 0))
            self.screen.blit(main_text, main_text_rect)
            self.screen.blit(back_button.image, back_button.rect)

            self.screen.blit(dimension_text, dimension_text_rect)
            self.screen.blit(map_dim_text, map_dim_text_rect)
            self.screen.blit(general_info_text, general_info_text_rect)
            self.screen.blit(tilesize_text, tilesize_text_rect)
            self.screen.blit(font_text, font_text_rect)
            self.clock.tick(FPS)
            pygame.display.update()

    def loading_screen(self):
        load = True
        x = 0

        font = pygame.font.Font('fonts/JetBrainsMono-Medium.ttf', 20)
        load_text = font.render('Loading', True, BLACK)
        load_text_rect = load_text.get_rect()
        load_text_rect.x = WIDTH//2 - 20
        load_text_rect.y = HEIGHT//2 - 50

        load_rect = pygame.Rect(WIDTH/2 - 150, HEIGHT/2, 300, 35)

        while load:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.play_bool = True
                    load = False
            
            load_fill_rect = pygame.Rect(WIDTH/2 - 149, HEIGHT/2+1, x, 31)
            if x < 299:
                x += 4
            elif x > 298:
                self.play_bool = False
                load = False

            self.screen.blit(self.load_background, (0, 0))
            self.screen.blit(load_text, load_text_rect)
            pygame.draw.rect(self.screen, BLACK, load_rect)
            pygame.draw.rect(self.screen, WHITE, load_fill_rect)
            self.screen.blit(self.logo, self.logo_rect)
            self.screen.blit(self.logo_font, self.logo_font_rect)
            self.clock.tick(FPS)
            pygame.display.update()

    def display(self):
        self.loading_screen()

        while not self.play_bool:
            if self.intro_bool:
                self.intro_screen()
            if self.settings:
                self.setting()

        if self.play_bool:
            self.new()
            while self.running:
                self.main()
                self.game_over()

        pygame.quit()
        sys.exit()

game = Game()
game.display()
