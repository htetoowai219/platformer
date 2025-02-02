from settings import *
from sprites import *
from myTimer import *

class Player(AnimatedSprite):
    def __init__(self, pos,  groups, collision_sprites, frames, create_bullet):
        super().__init__(frames, pos, groups)

        # movement
        self.collision_sprites = collision_sprites
        self.direction = pygame.Vector2()
        self.speed = 400
        self.gravity = 50
        self.on_floor = False
        self.flip = False
        self.create_bullet = create_bullet

        self.invicinble_frames = []
        for frame in self.frames:
            iframe = pygame.mask.from_surface(frame).to_surface()
            iframe.set_colorkey('black')
            self.invicinble_frames.append(frame)
            self.invicinble_frames.append(iframe)

        # timer
        self.shoot_timer = Timer(500)
        self.invicinble_timer = Timer(2000)

        # health
        self.health = 5

    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])

        # jump
        if keys[pygame.K_SPACE] and self.on_floor:
            self.direction.y = -20
            self.on_floor = False
        
        # shoot, Use the J key to shoot
        if keys[pygame.K_j] and not self.shoot_timer:
            self.create_bullet(self.rect.center, -1 if self.flip else 1)
            self.shoot_timer.activate()

    def move(self, dt):
        # horizontal
        self.rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')

        # vertical
        self.direction.y += self.gravity * dt
        self.rect.y += self.direction.y
        self.collision('vertical')

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.rect):
                if direction == 'horizontal':
                    if self.direction.x > 0: 
                        self.rect.right = sprite.rect.left
                    if self.direction.x < 0: 
                        self.rect.left = sprite.rect.right
                else:
                    if self.direction.y > 0: 
                        self.rect.bottom = sprite.rect.top
                        self.direction.y = 0
                    if self.direction.y < 0: self.rect.top = sprite.rect.bottom
                    
    def check_floor(self):
        bottom_rect = pygame.FRect((0, 0), (self.rect.width, 2)).move_to(midtop = self.rect.midbottom)
        level_rects = [sprite.rect for sprite in self.collision_sprites]
        self.on_floor = True if bottom_rect.collidelist(level_rects) >= 0 else False

    def animate(self, dt):
        if self.direction.x:
            self.frame_index += self.animation_speed * dt
            self.flip = self.direction.x < 0
        else:
            self.frame_index = 0

        self.frame_index = 1 if not self.on_floor else self.frame_index
        if self.invicinble_timer:
            self.image = self.invicinble_frames[int(self.frame_index) % len(self.invicinble_frames)]
        else:
            self.image = self.frames[int(self.frame_index) % len(self.frames)]
        self.image = pygame.transform.flip(self.image, self.flip, False)

    def update(self, dt):
        self.shoot_timer.update()
        self.invicinble_timer.update()
        self.check_floor()
        self.input()
        self.move(dt)
        self.animate(dt)