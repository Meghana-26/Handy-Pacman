import pygame
from pygame import mixer

pygame.mixer.pre_init (44100, -16, 2, 512)
mixer.init ()
pygame.init ()
clock = pygame.time.Clock ()
# timer
start_ticks = pygame.time.get_ticks()
fps = 60
# display
screen = pygame.display.set_mode ((800, 600))
pygame.display.set_caption ("Pacman")
icon1 = pygame.image.load ("pacman.png")
pygame.display.set_icon (icon1)

# Define font
font = pygame.font.SysFont ('Bauhaus 93', 70)
font_score = pygame.font.SysFont ('Bauhaus 93', 30)

# grid spliting
screen_width = 800
screen_height = 600
tile_size = 25
game_over = 0
main_menu = True
score = 0

# Define colors
white = (255, 255, 255)
Red = (255, 0, 0)

# image loading
restart_img = pygame.image.load ('restart.png')
start_img = pygame.image.load ('start.png')
exit1_img = pygame.image.load ('exit.png')
exit2_img = pygame.image.load ('exit2.png')

# load sounds
coin_fx = pygame.mixer.Sound ('Chomp.wav')
coin_fx.set_volume (0.5)
game_over_fx = pygame.mixer.Sound ('pacman-die.wav')
game_over_fx.set_volume (0.5)
intro_fx = pygame.mixer.Sound ('pacman_intro.wav')
intro_fx.set_volume (0.5)
win_fx = pygame.mixer.Sound ('win.wav')
win_fx.set_volume (0.2)


def draw_text(text, font, text_col, x, y):
    img = font.render (text, True, text_col)
    screen.blit (img, (x, y))


class Button ():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect ()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False
        # get mouse position
        pos = pygame.mouse.get_pos ()
        # check mouse over and check conditions
        if self.rect.collidepoint (pos):
            if pygame.mouse.get_pressed ()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True
        if pygame.mouse.get_pressed ()[0] == 0:
            self.clicked = False
        screen.blit (self.image, self.rect)
        return action


class Player ():
    def __init__(self, x, y):
        self.reset (x, y)

    def is_collided_with(self, world):
        return self.rect.colliderect (world.rect)

    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cooldown = 20

        if game_over == 0:
            # Events
            key = pygame.key.get_pressed()
            if key[pygame.K_LEFT]:
                dx -= 2
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 2
                self.counter += 1
                self.direction = 1
            if key[pygame.K_UP]:
                dy -= 2
                self.counter += 1
                self.direction = -2
            if key[pygame.K_DOWN]:
                dy += 2
                self.counter += 1
                self.direction = 2
            if key[pygame.K_RIGHT] == False and key[pygame.K_LEFT] == False and key[pygame.K_UP] == False and key[
                pygame.K_DOWN] == False:
                self.counter = 0
                self.index = 0
                self.image = self.images_right[self.index]

            # handle animations
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index == len (self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]
                if self.direction == 2:
                    self.image = self.images_down[self.index]
                if self.direction == -2:
                    self.image = self.images_up[self.index]

            # check for collisions
            for tile in world.tile_list:
                # check collision in X-direction
                if tile[1].colliderect (self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # check collision in Y-direction
                if tile[1].colliderect (self.rect.x, self.rect.y + dy, self.width, self.height):
                    dy = 0

            if pygame.sprite.spritecollide (self, blob_ghost1, False):
                game_over = -1
                game_over_fx.play ()
            if pygame.sprite.spritecollide (self, blob_ghost2, False):
                game_over = -1
                game_over_fx.play ()
            if pygame.sprite.spritecollide (self, blob_ghost3, False):
                game_over = -1
                game_over_fx.play ()
            if pygame.sprite.spritecollide (self, blob_ghost4, False):
                game_over = -1
                game_over_fx.play ()

            # update player coordinates
            self.rect.x += dx
            self.rect.y += dy
        elif game_over == -1:
            self.image = self.dead_image
            draw_text ("GAME OVER!", font, Red, 200, 275)
            self.rect.y -= 4

        # draw player onto screen
        screen.blit (self.image, self.rect)
        #pygame.draw.rect (screen, (0, 0, 255), self.rect, 1)
        return game_over

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.images_up = []
        self.images_down = []
        self.ghost1 = []
        self.index = 0
        self.counter = 0
        for num in range (1, 4):
            img_right = pygame.image.load (f'pacmanImg{num}.png')
            img_right = pygame.transform.scale (img_right, (20, 20))
            img_left = pygame.transform.flip (img_right, True, False)
            self.images_right.append (img_right)
            self.images_left.append (img_left)
        for num1 in range (4, 7):
            img_up = pygame.image.load (f'pacmanImg{num1}.png')
            img_up = pygame.transform.scale (img_up, (20, 20))
            img_down = pygame.transform.flip (img_up, True, True)
            self.images_up.append (img_up)
            self.images_down.append (img_down)
        self.dead_image = pygame.image.load ('ghost.jpeg')
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect ()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width ()
        self.height = self.image.get_height ()
        self.direction = 0


# grid creation
class World ():
    def __init__(self, data):
        self.tile_list = []
        wall_horiz = pygame.image.load ("b.png")
        wall_verti = pygame.image.load ("bv.png")
        wall_border1 = pygame.image.load ("b1.png")
        wall_border2 = pygame.image.load ("b2.png")
        wall_border3 = pygame.image.load ("b3.png")
        wall_border4 = pygame.image.load ("b4.png")

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:  # horizontal wall
                    img = pygame.transform.scale (wall_horiz, (25, 25))
                    img_rect = img.get_rect ()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append (tile)
                if tile == 2:  # power pellets
                    coin_White= Coin_White (col_count * tile_size + (tile_size / 2), row_count * tile_size + (tile_size / 2))
                    coin_White_group.add (coin_White)
                if tile == 12:  # power pellets
                    coin_Red = Coin_Red(col_count * tile_size + (tile_size / 2), row_count * tile_size + (tile_size / 2))
                    coin_Red_group.add (coin_Red)
                if tile == 13:  # power pellets
                    coin_Green = Coin_Green(col_count * tile_size + (tile_size / 2), row_count * tile_size + (tile_size / 2))
                    coin_Green_group.add (coin_Green)
                if tile == 3:  # vertical wall
                    img = pygame.transform.scale (wall_verti, (25, 25))
                    img_rect = img.get_rect ()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append (tile)
                if tile == 4:
                    img = pygame.transform.scale (wall_border1, (25, 25))
                    img_rect = img.get_rect ()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append (tile)
                if tile == 5:  # reverse L
                    img = pygame.transform.scale (wall_border2, (25, 25))
                    img_rect = img.get_rect ()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append (tile)
                if tile == 6:  # reverse L
                    img = pygame.transform.scale (wall_border3, (25, 25))
                    img_rect = img.get_rect ()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append (tile)
                if tile == 7:
                    img = pygame.transform.scale (wall_border4, (25, 25))
                    img_rect = img.get_rect ()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append (tile)
                if tile == 8:
                    blob1 = Ghost1 (col_count * tile_size + 5, row_count * tile_size - 10)
                    blob_ghost1.add (blob1)
                if tile == 9:
                    blob2 = Ghost2 (col_count * tile_size + 5, row_count * tile_size - 10)
                    blob_ghost2.add (blob2)
                if tile == 10:
                    blob3 = Ghost3 (col_count * tile_size + 5, row_count * tile_size - 10)
                    blob_ghost3.add (blob3)
                if tile == 11:
                    blob4 = Ghost4 (col_count * tile_size + 5, row_count * tile_size - 10)
                    blob_ghost4.add (blob4)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit (tile[0], tile[1])
            #pygame.draw.rect (screen, (0, 0, 205), tile[1], 1)

#White pellet
class Coin_White (pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__ (self)
        img = pygame.image.load ('pellet.png')
        self.image = pygame.transform.scale (img, (25, 25))
        self.rect = self.image.get_rect ()
        self.rect.center = (x, y)
#Red pellet
class Coin_Red(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__ (self)
        img = pygame.image.load ('red.png')
        self.image = pygame.transform.scale (img, (25, 25))
        self.rect = self.image.get_rect ()
        self.rect.center = (x, y)
#green pellet
class Coin_Green(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__ (self)
        img = pygame.image.load ('green.png')
        self.image = pygame.transform.scale (img, (25, 25))
        self.rect = self.image.get_rect ()
        self.rect.center = (x, y)


class Ghost1 (pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__ (self)
        self.image = pygame.image.load ('ghost_pink.png')
        self.rect = self.image.get_rect ()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs (self.move_counter) > 410:
            self.move_direction *= -1
            self.move_counter *= -1


class Ghost2 (pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__ (self)
        self.image = pygame.image.load ('ghost_green.png')
        self.rect = self.image.get_rect ()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs (self.move_counter) > 410:
            self.move_direction *= -1
            self.move_counter *= -1


class Ghost3 (pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__ (self)
        self.image = pygame.image.load ('ghost_red.png')
        self.rect = self.image.get_rect ()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs (self.move_counter) > 410:
            self.move_direction *= -1
            self.move_counter *= -1


class Ghost4 (pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__ (self)
        self.image = pygame.image.load ('ghost_yellow.png')
        self.rect = self.image.get_rect ()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs (self.move_counter) > 410:
            self.move_direction *= -1
            self.move_counter *= -1


world_data = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 5],
    [3, 12, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 12, 3],
    [3, 2, 4, 1, 1, 5, 2, 4, 1, 1, 1, 1, 1, 1, 1, 5, 2, 4, 1, 1, 1, 1, 1, 1, 5, 2, 4, 1, 1, 5, 2, 3],
    [3, 2, 3, 0, 0, 3, 13, 3, 0, 0, 0, 0, 0, 0, 0, 3, 2, 3, 0, 0, 0, 0, 0, 0, 3, 13, 3, 0, 0, 3, 2, 3],
    [3, 2, 6, 1, 1, 7, 2, 6, 1, 1, 1, 1, 1, 1, 1, 7, 2, 6, 1, 1, 1, 1, 1, 1, 7, 2, 6, 1, 1, 7, 2, 3],
    [3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3],
    [3, 2, 1, 1, 1, 1, 2, 4, 1, 1, 1, 1, 5, 2, 4, 1, 1, 5, 2, 4, 1, 1, 1, 1, 5, 2, 1, 1, 1, 1, 2, 3],
    [3, 2, 2, 2, 2, 2, 2, 3, 0, 0, 0, 0, 3, 2, 3, 0, 0, 3, 2, 3, 0, 0, 0, 0, 3, 2, 2, 2, 2, 2, 2, 3],
    [6, 1, 1, 1, 1, 5, 12, 6, 1, 1, 1, 1, 7, 2, 6, 1, 1, 7, 2, 6, 1, 1, 1, 1, 7, 12, 4, 1, 1, 1, 1, 7],
    [0, 0, 0, 0, 0, 3, 2, 2, 2, 2, 2, 2, 13, 2, 2, 2, 2, 2, 2, 13, 2, 2, 2, 2, 2, 2, 3, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 7, 2, 4, 1, 1, 1, 5, 2, 4, 0, 0, 0, 0, 5, 2, 4, 1, 1, 1, 5, 2, 6, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 2, 3, 0, 0, 0, 3, 2, 3, 8, 9, 10, 11, 3, 2, 3, 0, 0, 0, 3, 2, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 5, 2, 6, 1, 1, 1, 7, 2, 6, 1, 1, 1, 1, 7, 2, 6, 1, 1, 1, 7, 2, 4, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 3, 2, 2, 2, 2, 2, 2, 13, 2, 2, 2, 2, 2, 2, 13, 2, 2, 2, 2, 2, 2, 3, 0, 0, 0, 0, 0],
    [4, 1, 1, 1, 1, 7, 12, 4, 1, 1, 1, 1, 5, 2, 4, 1, 1, 5, 2, 4, 1, 1, 1, 1, 5, 12, 6, 1, 1, 1, 1, 5],
    [3, 2, 2, 2, 2, 2, 2, 3, 0, 0, 0, 0, 3, 2, 3, 0, 0, 3, 2, 3, 0, 0, 0, 0, 3, 2, 2, 2, 2, 2, 2, 3],
    [3, 2, 1, 1, 1, 1, 2, 6, 1, 1, 1, 1, 7, 2, 6, 1, 1, 7, 2, 6, 1, 1, 1, 1, 7, 2, 1, 1, 1, 1, 2, 3],
    [3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3],
    [3, 2, 4, 1, 1, 5, 2, 4, 1, 1, 1, 1, 1, 1, 1, 5, 2, 4, 1, 1, 1, 1, 1, 1, 5, 2, 4, 0, 2, 5, 2, 3],
    [3, 2, 3, 0, 0, 3, 13, 3, 0, 0, 0, 0, 0, 0, 0, 3, 2, 3, 0, 0, 0, 0, 0, 0, 3, 13, 3, 0, 0, 3, 2, 3],
    [3, 2, 6, 1, 1, 7, 2, 6, 1, 1, 1, 1, 1, 1, 1, 7, 2, 6, 1, 1, 1, 1, 1, 1, 7, 2, 6, 1, 1, 7, 2, 3],
    [3, 12, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 12, 3],
    [6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 7],
]

player = Player (686, 490)
coin_White_group = pygame.sprite.Group ()
coin_Red_group = pygame.sprite.Group ()
coin_Green_group = pygame.sprite.Group ()
blob_ghost1 = pygame.sprite.Group ()
blob_ghost2 = pygame.sprite.Group ()
blob_ghost3 = pygame.sprite.Group ()
blob_ghost4 = pygame.sprite.Group ()

# Create dummy coin for showing the score
score_coin = Coin_White (348, 10)
coin_White_group.add (score_coin)

world = World (world_data)

# Buttons
restart_button = Button (600, 5, restart_img)
start_button = Button (screen_width // 2 - 50, screen_height // 2, start_img)
exit1_button = Button (screen_width // 2 + 50, screen_height // 2, exit1_img)
exit2_button = Button (700, 7, exit2_img)

# game loop
running = True
while running:
    clock.tick (fps)
    screen.fill ((0, 0, 0))
    if main_menu == True:
        if exit1_button.draw ():
            running = False
        if start_button.draw ():
            main_menu = False
            intro_fx.play ()
    else:
        world.draw ()
        coin_White_group.draw (screen)
        coin_Red_group.draw (screen)
        coin_Green_group.draw (screen)
        blob_ghost1.draw (screen)
        blob_ghost2.draw (screen)
        blob_ghost3.draw (screen)
        blob_ghost4.draw (screen)

        if game_over == 0:
            seconds = (pygame.time.get_ticks () - start_ticks) / 1000  # calculate how many seconds
            # Timer
            if seconds > 100:
                draw_text ("GAME OVER!", font, Red, 200, 275)
                screen.fill ((0, 0, 0))
                draw_text ('TIME UP!', font, Red, 260, 275)
                draw_text ('Total Score : ' + str (score), font_score, white, 300, 350)
                seconds = 0
                if exit2_button.draw ():
                    running = False
            draw_text ('Timer : ' + str (int (seconds)) + '/10', font_score, white, 100, -4)

            # update score
            # check if the coin has been collected
            if pygame.sprite.spritecollide (player, coin_White_group, True):
                coin_fx.play ()
                score += 1
            if pygame.sprite.spritecollide (player, coin_Red_group, True):
                coin_fx.play ()
                score += 5
            if pygame.sprite.spritecollide (player, coin_Green_group, True):
                coin_fx.play ()
                score += 10
            draw_text ('Score : ' + str (score), font_score, white, 372, -4)
            blob_ghost1.update ()
            blob_ghost2.update ()
            blob_ghost3.update ()
            blob_ghost4.update ()

        # draw_grid()
        game_over = player.update (game_over)
        if score >= 354:
            draw_text ('YOU WIN', font, Red, 260, 275)
            win_fx.play ()
            if exit2_button.draw ():
                running = False
        # To restart
        if game_over == -1:
            if restart_button.draw ():
                player.reset (686, 490)
                game_over = 0
                score = 0
            if exit2_button.draw ():
                running = False
    # Quit event
    for event in pygame.event.get ():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.update ()
