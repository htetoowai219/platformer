from settings import * 
from sprites import *
from groups import AllSprites
from player import Player
from support import *
from myTimer import *
from random import randint
from sys import exit

world = 'world2.tmx'
BEE_TIMER, PLAYER_HEALTH = DIFFICULTY['easy']

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Platformer')
        self.clock = pygame.time.Clock()
        self.running = True
        self.finish_line = None

        # groups 
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        # setup
        self.load_assets()
        self.setup()

        # timer
        self.bee_timer = Timer(BEE_TIMER, func = self.create_bee, autostart=True, repeat='infinite')

    def create_bullet(self, pos, direction):
        x = pos[0] + direction * 34 if direction == 1 else pos[0] + direction * 34 - self.bullet_surf.get_width()
        self.audio['shoot'].play()
        Fire(self.fire_surf, pos, self.all_sprites, self.player)
        Bullet(self.bullet_surf, (x, pos[1]), direction, (self.all_sprites, self.bullet_sprites))

    def create_bee(self):
        Bee(
            frames=self.bee_frames, 
            pos=((self.level_width + WINDOW_WIDTH), randint(0, self.level_height)), 
            groups=(self.all_sprites, self.enemy_sprites),
            speed=randint(300, 500)
            )

    def load_assets(self):
        # graphics
        self.player_frames = import_folder('images', 'player')
        self.bullet_surf = import_image('images', 'gun', 'bullet')
        self.fire_surf = import_image('images', 'gun', 'fire')
        self.bee_frames = import_folder('images', 'enemies', 'bee')
        self.worm_frames = import_folder('images', 'enemies', 'worm')
        self.i_worm_frames = [pygame.transform.flip(surf, True, False) for surf in self.worm_frames]
        self.heart_surf = import_image('images', 'heart', 'heart')
        # audio
        self.audio = audio_importer('audio')
        for audio in self.audio.values():
            audio.set_volume(0.1)
        
    def display_health(self):
        for i in range(self.player.health):
            x = 10 + i * (self.heart_surf.get_width() + 10)
            self.display_surface.blit(self.heart_surf, (x, 10))

    def setup(self):
        map = load_pygame(join('data', 'maps', world))
        self.level_width = map.width * TILE_SIZE
        self.level_height = map.height * TILE_SIZE

        for x, y, image in map.get_layer_by_name('Main').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, (self.all_sprites, self.collision_sprites))

        for x, y, image in map.get_layer_by_name('Decoration').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)

        for obj in map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.playerx, self.playery = obj.x, obj.y
                self.player = Player((obj.x, obj.y), (self.all_sprites), self.collision_sprites, self.player_frames, self.create_bullet, PLAYER_HEALTH)
            if obj.name == 'Worm':
                Worm(self.worm_frames, self.i_worm_frames, pygame.FRect(obj.x, obj.y, obj.width, obj.height), (self.enemy_sprites, self.all_sprites))
            if obj.name == 'Finish':
                self.finish_line = pygame.FRect(obj.x, obj.y, obj.width, obj.height)

        
        self.audio['music'].play(loops = -1)

    def collision(self):
        # bullets -> enemies
        for bullet in self.bullet_sprites:
           sprite_collisions = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
           if sprite_collisions:
               self.audio['impact'].play()
               bullet.kill()
               for sprite in sprite_collisions:
                   sprite.destroy() 

        # Finish line
        if self.finish_line:
            if self.finish_line.colliderect(self.player.rect):
                print('You Won.')
                self.running = False

        # enemies -> player
        player_collision = pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask)
        if player_collision and not self.player.invicinble_timer:
            if self.player.health > 1:
                self.player.invicinble_timer.activate()
                self.player.health -= 1
            else:
                self.running = False

        # if self.player.rect.top >= self.level_height + WINDOW_HEIGHT:
        #     if self.player.health > 1:
        #         self.player.health -= 1
        #         self.player.rect.center = (self.playerx, self.playery)
        #     else:
        #         self.running = False

    def run(self):
        while self.running:
            dt = self.clock.tick(FRAMERATE) / 1000 

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False 
            
            # update
            self.bee_timer.update()
            self.all_sprites.update(dt)
            self.collision()

            # draw 
            self.display_surface.fill(BG_COLOR)
            self.all_sprites.draw(target_pos=self.player.rect.center)
            self.display_health()
            pygame.display.update()
        
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run() 

exit()