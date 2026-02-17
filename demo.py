import pygame, math, random
# https://stackoverflow.com/questions/70128800/trouble-with-explosion-animation

FPS = 60
GAME_WIDTH = 500
GAME_HEIGHT = 400
HERO_WIDTH = 42
HERO_HEIGHT = 48
FLYING_ENEMY_WIDTH = HERO_WIDTH-10
FLYING_ENEMY_HEIGHT = HERO_HEIGHT-10
BULLET_SIZE = 12
TILE_SIZE = 24
COOLDOWN = 500
RADIUS = 50

# 500 / 24 = 20.83 round up 21 | number of columns
# 400 / 24 = 16.67 round up 17 | number of rows
tilemap = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0],
    [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]



pygame.init()
pygame.display.init()
surface = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
clock = pygame.time.Clock()

REAL_FLOOR = 320
FLOOR = 300
GRAVITY = 5000
FRICTION = 20
KNOCKBACK_FORCE = 30

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load("megaman-right-walk0.png").convert_alpha(), (HERO_WIDTH, HERO_HEIGHT))
        self.orientation = {1: self.image, -1: pygame.transform.flip(self.image, True, False)}
        self.rect = self.image.get_rect()
        self.jumping = False
        self.rect.topleft = (x, y)
        self.y_velocity = 0
        self.x_velocity = 0
        self.x_direction = 1

        self.particles = []

    def update(self, dt):
        self.image = self.orientation[self.x_direction]

        # ############### CHARACTER TRAIL
        # # make this independent like the functions create particles and draw particles so
        # # the dust would still appear despite the keys are not being pressed
        # for particle in self.particles:
        #     particle[0][0] -= 2
        #     particle[0][1] += particle[1]
        # particle = [list(self.rect.midbottom), random.uniform(-1, 1), (random.randrange(100, 200), random.randint(50, 120), random.randint(0, 80))]
        # self.particles.append(particle)
        # if len(self.particles) > 10:
        #     self.particles.pop(0)

        # if self.x_velocity > 0 or self.x_velocity < 0:
        #     if self.rect.y == 312 or not self.jumping:
        #         self._draw_particles()
        # ############### CHARACTER TRAIL

        
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x > GAME_WIDTH - HERO_WIDTH:
            self.rect.x = GAME_WIDTH - HERO_WIDTH 
        
        if self.rect.y > 312:
            self.rect.y = 312
        # slide effect
        if int(self.x_velocity) == 0:
            self.x_velocity = 0
        elif self.x_velocity > 0:
            self.x_velocity -= FRICTION
            # print("x_velocity",self.x_velocity)
        elif self.x_velocity < 0:
            self.x_velocity += FRICTION

        # print(self.y_velocity)
        # print(self.rect.y)
        # print("dt",dt)
        self.rect.x += self.x_velocity * dt #+ scroll[0]

        detect_x_collision(self)

        # responsible for simulating the character free-falling because of gravity
        self.y_velocity += GRAVITY * dt * .5
        self.rect.y += self.y_velocity * dt * .5 #+ scroll[1]
        self.y_velocity += GRAVITY * dt * .5
        # print(self.y_velocity)
        # print(self.rect.y)

        detect_y_collision(self)
        
        # if self.hero_rect.y + HERO_HEIGHT > FLOOR:
        #     self.hero_rect.y = FLOOR - HERO_HEIGHT
        #     self.jumping = False
        

        # keeps the character from going out of the window  border
        if self.rect.y < 0:
            self.rect.y = 0
    
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load("megaman-right-walk0.png").convert_alpha(), (HERO_WIDTH, HERO_HEIGHT))
        self.rect = self.image.get_rect(center=(x, y))
        self.x_velocity = 120
        self.y_velocity = 0
        self.jumping = False

        self.sensor = pygame.Rect(0, 0, HERO_WIDTH+20, 10)
        self.stucked = False
        self.stuck_center_posx = 0
    
    def update(self, pl: Player, dt):
        # pygame.draw.rect(surface, (255, 255, 255), self.rect, 1)
        
        self.sensor.center = self.rect.midtop
        pygame.draw.rect(surface, (255, 255, 255), ((self.sensor.x-scroll[0], self.sensor.y-scroll[1]), (self.sensor.w, self.sensor.h)), 1)

        for tile in tiles:
            collided_tile = tile.image_rect.colliderect(self.sensor)
            if collided_tile and self.rect.y > pl.rect.y and not self.jumping:
                self.y_velocity = -1300
                self.jumping = True

        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x > GAME_WIDTH - HERO_WIDTH:
            self.rect.x = GAME_WIDTH - HERO_WIDTH
        
        if self.rect.y > 312:
            self.rect.y = 312
        elif self.rect.y < 0:
            self.rect.y = 0

        ##############################
        MAP_HALF = GAME_WIDTH//2

        if self.rect.y < pl.rect.y: # if enemy is above player
            if pl.rect.y == 312:
                if pl.rect.centerx < self.rect.centerx:
                    self.x_velocity = -80
                elif pl.rect.centerx > self.rect.centerx:
                    self.x_velocity = 120
                else:
                    self.stucked = True
                    self.stuck_center_posx = self.rect.centerx
        
        elif self.rect.y > pl.rect.y: # if enemy is below player
            if self.rect.y == 312:
                if pl.rect.centerx < self.rect.centerx:
                    self.x_velocity = -80
                elif pl.rect.centerx > self.rect.centerx:
                    self.x_velocity = 120
                else:
                    self.stucked = True
                    self.stuck_center_posx = self.rect.centerx
            else:
                if pl.rect.centerx < self.rect.centerx:
                    self.x_velocity = -80
                elif pl.rect.centerx > self.rect.centerx:
                    self.x_velocity = 120
        else: # both are equal
            if self.rect.centerx < pl.rect.centerx:
                self.x_velocity = 120
            elif self.rect.centerx > pl.rect.centerx:
                self.x_velocity = -80

        # 218 and 291
        if self.stucked and self.rect.centerx <= 291 and self.rect.centerx >= 218 and not self.is_stucked_pos_inside_center():
            self.stucked = False
        elif self.stucked and self.rect.centerx >= 180 and self.rect.centerx <= 190 and self.is_stucked_pos_inside_center():
            self.stucked = False
        elif self.stucked and self.stuck_center_posx <= 291 and self.stuck_center_posx >= 218:
            self.x_velocity = -80
        elif self.stucked and self.stuck_center_posx <= MAP_HALF:
            self.x_velocity = 120
        elif self.stucked and self.stuck_center_posx >= MAP_HALF:
            self.x_velocity = -80

        self.rect.centerx += self.x_velocity * dt
        #############################

        detect_x_collision(self)
        
        self.y_velocity += GRAVITY * dt * .5
        self.rect.y += self.y_velocity * dt * .5
        self.y_velocity += GRAVITY * dt * .5

        detect_y_collision(self)
    
    def is_stucked_pos_inside_center(self):
        return True if self.stuck_center_posx <= 291 and self.stuck_center_posx >= 218 else False

class FlyingEnemy(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load("blader-left.png").convert_alpha(), (FLYING_ENEMY_WIDTH, FLYING_ENEMY_HEIGHT))
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        self.x_vel = 0
        self.y_vel = 0
        self.speed = speed
    
    def update(self, pl: Player, dt):
        # pygame.draw.rect(surface, (255, 0, 0), self.rect, 1)

        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.left > GAME_WIDTH - FLYING_ENEMY_WIDTH:
            self.rect.left = GAME_WIDTH - FLYING_ENEMY_WIDTH
        
        if self.rect.y > 312:
            self.rect.y = 312
        elif self.rect.y < 0:
            self.rect.y = 0
        
        dx = pl.rect.x - self.rect.x
        dy = pl.rect.y - self.rect.y
        dist = pygame.Vector2(dx, dy).length()

        if dist > 1:
            direction_vector = pygame.Vector2(dx, dy).normalize()
            self.x_vel = direction_vector.x * self.speed * dt
            self.y_vel = direction_vector.y * self.speed * dt
            
            self.pos += direction_vector * self.speed * dt
        else:
            self.x_vel = 0
            self.y_vel = 0
        
        # self.rect.centerx += int(self.x_vel)
        self.rect.centerx = int(self.pos.x)
        collided_tile = self.get_tile_collided()
        if collided_tile is not None:
            if self.x_vel > 0:
                self.rect.right = collided_tile.image_rect.left
            elif self.x_vel < 0:
                self.rect.left = collided_tile.image_rect.right
            self.pos.x = pygame.Vector2(self.rect.center).x
        
        # self.rect.centery += int(self.y_vel)
        self.rect.centery = int(self.pos.y)
        collided_tile = self.get_tile_collided()
        if collided_tile is not None:
            if self.y_vel > 0:
                self.rect.bottom = collided_tile.image_rect.top
            elif self.y_vel < 0:
                self.rect.top = collided_tile.image_rect.bottom
            self.pos.y = pygame.Vector2(self.rect.center).y
        


        # SMOOTH ANIMATION BUT DOES NOT FOLLOW PHYSICS (STOP WHEN IT HITS PLATFORM)
        # GOOD FOR GHOST OR SOMETHING ALIKE
        ###########################################################
        # dist = pygame.Vector2(pl.rect.x - self.rect.x, pl.rect.y - self.rect.y)
        
        # if dist.length() > 1:
        #     dist = dist.normalize()
        #     new_pos = dist * self.speed * dt
        #     self.pos += new_pos
        #     self.rect.center = int(self.pos.x), int(self.pos.y)
        ###########################################################

    def get_tile_collided(self):
        for tile in tiles:
            if tile.image_rect.colliderect(self.rect):
                return tile
        return None

class Bullet(pygame.sprite.Sprite):
    def __init__(self, image, x, y, dt, direction, mouse_target_x, mouse_target_y):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load(image), (BULLET_SIZE, BULLET_SIZE))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.speed = 450
        self.direction = direction
        self._x = x
        self._y = y
        self._mouse_target_x = mouse_target_x + scroll[0]
        self._mouse_target_y = mouse_target_y + scroll[1]
        self._angle = math.atan2(self._mouse_target_y - self._y, self._mouse_target_x - self._x) # ORIGNIAL!!!
        self._x_vel = math.cos(self._angle)*self.speed
        self._y_vel = math.sin(self._angle)*self.speed

        self.particles = []
    
    def update(self, tiles: list[Tile], dt):
        ########## TRAIL PARTICLE ##########
        for particle in self.particles:
            particle[0][0] -= 1
            particle[0][1] += particle[1]
        particle = [list(self.rect.midleft), random.uniform(-2, 2), pygame.Color(255, random.randrange(255), 0)]
        self.particles.append(particle)
        if len(self.particles) > 20:
            self.particles.pop(0)
        ########## TRAIL PARTICLE ##########
        self._draw_particles()


        if self.rect.x > GAME_WIDTH:
            self.kill()
        elif self.rect.x < 0:
            self.kill()
        
        if self.direction > 0:
            self.speed = self.speed
        elif self.direction < 0:
            self.speed = -400
        
        # erase bullet if it hits a tile
        for tile in tiles:
            if self.rect.colliderect(tile.image_rect):
                self.kill()
        # self._check_collision_against_own_enemy() # LINE 672 - 693 functions bullet_hit_own_enemy and bullet_hit_flying_enemy
        # self._check_collision_against_flying_enemy()
        
        # Responsible for bullet movement, you could remove everything above
        # these and the bullet will still travel
        self._x += self._x_vel * dt
        self._y += self._y_vel * dt
        self.rect.x = int(self._x)
        self.rect.y = int(self._y)
    
    def _draw_particles(self):
        for i, particle in enumerate(self.particles):
            pygame.draw.circle(surface, particle[2], (particle[0][0]-scroll[0], particle[0][1]-scroll[1]), (i//3+2))
    
    def _check_collision_against_own_enemy(self):
        for own_enemy in own_enemy_group.sprites():
            if self.rect.colliderect(own_enemy.rect):
                explosion = Explosion(bullet.rect.centerx, bullet.rect.centery, RADIUS) # ORIGINAL!!
                explosions.add(explosion)
                self.kill()
    
    def _check_collision_against_flying_enemy(self):
        for flying_enemy in flying_enemy_group.sprites():
            if self.rect.colliderect(flying_enemy.rect):
                explosion = Explosion(bullet.rect.centerx, bullet.rect.centery, RADIUS)
                explosions.add(explosion)
                self.kill()
        
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, radius):
        super().__init__()
        self.radius = radius
        self.image = pygame.surface.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 40, 0, 255), (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect(center=(x, y))
        self.orig_center = (x, y)
        self.frame_delay = 55
        self.last_update_time = pygame.time.get_ticks()
    
    def update(self):
        current_time = pygame.time.get_ticks()
        if self.radius <= 0:
            self.kill()
        else:
            if current_time - self.last_update_time >= self.frame_delay:
                self.radius -= 1
                self.image = pygame.transform.scale(self.image, (self.radius, self.radius))
                self.rect = self.image.get_rect(center=(self.orig_center[0], self.orig_center[1]))
                # pygame.draw.circle(self.image, (255, 0, 0, 128), (self.radius, self.radius), self.radius)

class Wand(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load("wand.png"), (80, 80))
        self.image = pygame.transform.rotate(self.image, 270)
        self.image.set_colorkey((255, 255, 255))
        self.orig_image = self.image

        self.rect = self.image.get_rect(center=(x, y))
        # center of image or surface - wand in this case
        self.pivot_point = self.rect.centerx/2, self.rect.centery/2
        # offset
        self.offset = pygame.math.Vector2(20, 0)
    
    def update(self, player, x, y):
        pos_mouse = pygame.mouse.get_pos()
        # mouse_pos_x = pos_mouse[0] #ORIGNAL!!!
        # mouse_pos_y = pos_mouse[1] #ORIGNAL!!!
        mouse_pos_x = pos_mouse[0] + scroll[0]
        mouse_pos_y = pos_mouse[1] + scroll[1]
        pl_x = x
        pl_y = y
        # print("Player center pos:",player.rect.center)

        # offset_mouse = pos_mouse - self.pivot_point
        # angle_mouse = math.atan2(self._mouse_target_y-self.rect.y, self._mouse_target_x-self.rect.x)

        angle_mouse = math.degrees(math.atan2(mouse_pos_y - pl_y, mouse_pos_x - pl_x))
        self.switch_player_orientation(player, angle_mouse)
        self.rotate_around_pivot(angle_mouse, x, y)

    def rotate_around_pivot(self, angle, x, y):
        # self.image = pygame.transform.rotozoom(self.orig_image, -angle, 1)
        self.image = pygame.transform.rotate(self.orig_image, -angle)
        rotated_offset = self.offset.rotate(angle)

        self.rect = self.image.get_rect(center=self.pivot_point+rotated_offset)
        self.rect.center = (x, y) + rotated_offset

    def switch_player_orientation(self, pl: Player, angle):
        pl.x_direction = -1 if angle > 90 or angle < -90 else 1

class Spark():
    def __init__(self, loc, angle, speed, color, scale=1):
        self.loc = loc
        self.angle = angle
        self.speed = speed
        self.scale = scale
        self.color = color
        self.alive = True

    def point_towards(self, angle, rate):
        rotate_direction = ((angle - self.angle + math.pi * 3) % (math.pi * 2)) - math.pi
        try:
            rotate_sign = abs(rotate_direction) / rotate_direction
        except ZeroDivisionError:
            rotate_sign = 1
        if abs(rotate_direction) < rate:
            self.angle = angle
        else:
            self.angle += rate * rotate_sign

    def calculate_movement(self, dt):
        return [math.cos(self.angle) * self.speed * dt, math.sin(self.angle) * self.speed * dt]

    # gravity and friction
    def velocity_adjust(self, friction, force, terminal_velocity, dt):
        movement = self.calculate_movement(dt)
        movement[1] = min(terminal_velocity, movement[1] + force * dt)
        movement[0] *= friction
        self.angle = math.atan2(movement[1], movement[0])
        # if you want to get more realistic, the speed should be adjusted here

    def move(self, dt):
        movement = self.calculate_movement(dt)
        self.loc[0] += movement[0]
        self.loc[1] += movement[1]

        # a bunch of options to mess around with relating to angles...
        # self.point_towards(math.pi / 2, 0.02)
        # self.velocity_adjust(0.975, 0.2, 8, dt)
        # self.angle += 0.1

        self.speed -= 0.1

        if self.speed <= 0:
            self.alive = False

    def draw(self, surf, offset=[0, 0]):
        if self.alive:
            points = [
                [(self.loc[0] - scroll[0]) + math.cos(self.angle) * self.speed * self.scale, (self.loc[1] - scroll[1]) + math.sin(self.angle) * self.speed * self.scale],
                [(self.loc[0] - scroll[0]) + math.cos(self.angle + math.pi / 2) * self.speed * self.scale * 0.3, (self.loc[1] - scroll[1]) + math.sin(self.angle + math.pi / 2) * self.speed * self.scale * 0.3],
                [(self.loc[0] - scroll[0]) - math.cos(self.angle) * self.speed * self.scale * 3.5, (self.loc[1] - scroll[1]) - math.sin(self.angle) * self.speed * self.scale * 3.5],
                [(self.loc[0] - scroll[0]) + math.cos(self.angle - math.pi / 2) * self.speed * self.scale * 0.3, (self.loc[1] - scroll[1]) - math.sin(self.angle + math.pi / 2) * self.speed * self.scale * 0.3],
                ]
            pygame.draw.polygon(surf, self.color, points)

def detect_explosion(explosions: CustomGroup, bullets: list[Bullet], tiles: list[Tile]):
    for bullet in bullets:
        for tile in tiles:
            if bullet.rect.colliderect(tile.image_rect):
                # pygame.draw.circle(surface, (255, 0, 0, 128), (bullet.rect.centerx, bullet.rect.centery), RADIUS)
                explosion = Explosion(bullet.rect.centerx, bullet.rect.centery, RADIUS)
                explosions.add(explosion)

                create_particles(bullet.rect.center)
                for _ in range(6):
                    sparks.append(Spark([bullet.rect.centerx, bullet.rect.centery], math.radians(random.randint(0, 360)), random.randint(3, 6), (255, 255, 255), 2))


def create_particles(pos: tuple):
    # add particles on a list then on main loop draw it
    # still call draw even when it is empty
    for _ in range(2):
        particles.append([[random.randrange(pos[0]-30, pos[0]+30),
                          random.randrange(pos[1]-40, pos[1])],
                          random.randrange(40, 50)])
    
    for _ in range(5): # loc, radius
        particles.append([[random.randrange(pos[0]-50, pos[0]+50),
                            random.randrange(pos[1]-70, pos[1])],
                            random.randrange(10, 30)])

def create_radiation(pos: tuple):
    for _ in range(1): # loc, radius, width
        radiations.append([[pos[0], pos[1]],
                            15,
                              5])

def create_background_particles():
    if len(background_particles) < 7: # loc, radius, direction
        background_particles.append([[random.randrange(GAME_WIDTH), random.randrange(GAME_HEIGHT)],
                                     random.randrange(2, 4),
                                     [random.choice([.5, -.5]), random.choice([.5, -.5])]])

def create_dust():
    global dusts
    if pl.x_velocity != 0:
        if pl.rect.y == 312 or not pl.jumping:
            if len(dusts) < 30:# loc, radius, velocity
                dusts.append([[pl.rect.midbottom[0], pl.rect.midbottom[1]],
                            5,
                            [random.randint(-2, 2), random.randint(-15, 0)*.1]])


def check_overlap_own_enemy(own_enemies: list[Enemy]):
    for enemy in own_enemies:
        for other_enemy in own_enemies:
            if enemy is other_enemy:
                continue

            if enemy.rect.colliderect(other_enemy):
                overlap = enemy.rect.clip(other_enemy)

                if overlap.w < overlap.h:
                    if enemy.rect.centerx < other_enemy.rect.centerx:
                        enemy.rect.centerx -= overlap.w // 2
                        # other_enemy.rect.centerx += overlap.w // 2
                    else:
                        enemy.rect.centerx += overlap.w // 2
                        # other_enemy.rect.centerx -= overlap.w // 2
                # else:
                #     if enemy.rect.centery < other_enemy.rect.centery:
                #         enemy.rect.centery -= overlap.h // 2
                #         # other_enemy.rect.centery += overlap.h // 2
                #     else:
                #         enemy.rect.centery += overlap.h // 2
                #         # other_enemy.rect.centery -= overlap.h // 2

def check_overlap_flying_enemy(flying_enemy: list[FlyingEnemy]):
    for enemy in flying_enemy:
        for other_enemy in flying_enemy:
            if enemy is other_enemy:
                continue

            
            if enemy.rect.colliderect(other_enemy):
                overlap = enemy.rect.clip(other_enemy)

                if isinstance(overlap, pygame.Rect):
                    if enemy.rect.centerx < other_enemy.rect.centerx:
                        enemy.rect.centerx -= overlap.w // 2
                        # other_enemy.rect.centerx += overlap.w // 2
                    else:
                        enemy.rect.centerx += overlap.w // 2
                        # other_enemy.rect.centerx -= overlap.w // 2

                # else:
                #     if enemy.rect.centery < other_enemy.rect.centery:
                #         enemy.rect.centery -= overlap.h // 2 * 1
                #         # other_enemy.rect.centery += overlap.h // 2 * 1.5
                #     else:
                #         enemy.rect.centery += overlap.h // 2  * 1
                #         # other_enemy.rect.centery -= overlap.h // 2  * 1.5

def draw_particles(particles):
        if particles:
            particles = [particle for particle in particles if particle[1] > 0]

            for particle in particles:
                particle[1] -= 1
                pygame.draw.circle(surface, (255, random.randrange(255), 0), (particle[0][0]-scroll[0], particle[0][1]-scroll[1]), int(particle[1]))

def draw_radiation(radiations):
    if radiations:
        radiations = [radiation for radiation in radiations if radiation[2] > 1.1]

        for radiation in radiations:
            radiation[1] += 5 # radius
            radiation[2] -= .1 # width
            pygame.draw.circle(surface, (255, 126, 0), (radiation[0][0]-scroll[0], radiation[0][1]-scroll[1]), int(radiation[1]), int(radiation[2]))

def draw_background_particles():
    global background_particles
    if background_particles:
        background_particles = [background_particle for background_particle in background_particles
                                 if (background_particle[0][1] > 0 and background_particle[0][1] < GAME_HEIGHT) and 
                                 (background_particle[0][0] > 0 and background_particle[0][0] < GAME_WIDTH)]
        
        # loc, radius, direction
        for bg_particle in background_particles:
            # bg_particle[0][1] += -.5
            bg_particle[0][0] += bg_particle[2][0]
            bg_particle[0][1] += bg_particle[2][1]
            pygame.draw.circle(surface, (255, 255, 255), [int(bg_particle[0][0])-scroll[0], int(bg_particle[0][1])-scroll[1]], bg_particle[1])

            # change the multiplier if you want to make the glow particle (circle) to be bigger
            bg_particle_radius = bg_particle[1]*3

            particle_surface = pygame.Surface((bg_particle_radius * 2, bg_particle_radius * 2))
            pygame.draw.circle(particle_surface, (20, 20, 20), (bg_particle_radius, bg_particle_radius), bg_particle_radius)
            # pygame.draw.circle(particle_surface, (20, 20, 20), (bg_particle_radius-scroll[0], bg_particle_radius-scroll[1]), bg_particle_radius) # ORIGINAL!!
            particle_surface.set_colorkey((0,0,0))

            surface.blit(particle_surface, [int(bg_particle[0][0] - bg_particle_radius)-scroll[0], int(bg_particle[0][1] - bg_particle_radius)-scroll[1]], special_flags=pygame.BLEND_RGB_ADD)

def draw_sparks():
    for i, spark in sorted(enumerate(sparks), reverse=True):
        spark.move(1)
        spark.draw(surface)
        if not spark.alive:
            sparks.pop(i)

def draw_dust():
    global dusts, pl

    if dusts:# loc, radius, velocity
        dusts = [dust for dust in dusts if dust[1] > 0]

        for dust in dusts:
            dust[0][0] -= dust[2][0]
            dust[0][1] += dust[2][1]
            dust[1] -= .2
            pygame.draw.circle(surface,
                            (random.randrange(100, 200), random.randint(50, 120), random.randint(0, 80)),
                            (dust[0][0]-scroll[0], dust[0][1]-scroll[1]),
                            int(dust[1]))
        

# def check_if_enemy_within_aoe(enemies: list[Player], explosions: list[Explosion]):
#     for explosion in explosions:
#         for enemy in enemies:
#             distance_left = math.hypot(enemy.rect.bottomleft[0] - explosion.rect.x, enemy.rect.bottomleft[1] - explosion.rect.y)
#             distance_right = math.hypot(enemy.rect.bottomright[0] - explosion.rect.x, enemy.rect.bottomright[1] - explosion.rect.y)
#             if distance_left < RADIUS or distance_right < RADIUS:
#                 enemy.kill()

# def kill_enemies(explosion_group: pygame.sprite.Group, enemy_group: pygame.sprite.Group):
#     hits = pygame.sprite.groupcollide(explosion_group, enemy_group, False, True)

#     for hit in hits:
#         create_particles(hit.rect.center)
#         create_radiation(hit.rect.center)

# def kill_own_enemy(explosion_group: pygame.sprite.Group, enemy_group: pygame.sprite.Group):
#     hits: dict[Explosion, Enemy] = pygame.sprite.groupcollide(explosion_group, enemy_group, False, False)

#     for hit in hits:
#         create_particles(hit.rect.center)
#         # create_radiation(hit.rect.center)

def bullet_hit_own_enemy():
    hits: dict[Bullet, Enemy] = pygame.sprite.groupcollide(bullet_group, own_enemy_group, False, False)

    for bullet, own_enemies in hits.items():
        create_particles(bullet.rect.center)
        bullet.kill()

        for own_enemy in own_enemies:
            apply_knockback(bullet.speed, own_enemy)
            explosions.add(Explosion(bullet.rect.centerx, bullet.rect.centery, RADIUS))

        for _ in range(6):
            sparks.append(Spark([bullet.rect.centerx, bullet.rect.centery], math.radians(random.randint(0, 360)), random.randint(3, 6), (255, 255, 255), 2))

# def kill_flying_enemy(explosion_group: pygame.sprite.Group, enemy_group: pygame.sprite.Group):
#     hits: dict[Explosion, FlyingEnemy] = pygame.sprite.groupcollide(explosion_group, enemy_group, False, True)

#     for hit in hits:
#         create_particles(hit.rect.center)
#         create_radiation(hit.rect.center)

def bullet_hit_flying_enemy():
    hits: dict[Bullet, FlyingEnemy] = pygame.sprite.groupcollide(bullet_group, flying_enemy_group, False, False)

    for bullet, flying_enemies in hits.items():
        create_particles(bullet.rect.center)
        create_radiation(bullet.rect.center)
        bullet.kill()

        for flying_enemy in flying_enemies:
            apply_knockback_flying_enemy(bullet.speed, flying_enemy)
            explosions.add(Explosion(bullet.rect.centerx, bullet.rect.centery, RADIUS))

        for _ in range(6):
            sparks.append(Spark([bullet.rect.centerx, bullet.rect.centery], math.radians(random.randint(0, 360)), random.randint(3, 6), (255, 255, 255), 2))

# negative if bullet going left and pos if going right
def apply_knockback(bullet_speed, enemy):
    if bullet_speed < 0:
        enemy.rect.x -= KNOCKBACK_FORCE
    else:
        enemy.rect.x += KNOCKBACK_FORCE

def apply_knockback_flying_enemy(bullet_speed, enemy:FlyingEnemy):
    if bullet_speed < 0:
        enemy.pos.x -= KNOCKBACK_FORCE
    else:
        enemy.pos.x += KNOCKBACK_FORCE


class Tile:
    def __init__(self, image, x, y):
        self.image_surface = pygame.transform.scale(pygame.image.load(image).convert_alpha(), (TILE_SIZE, TILE_SIZE))
        self.image_rect = self.image_surface.get_rect()
        self.image_rect.topleft = (x, y)


tiles: list[Tile] = []

def create_tilemap():
    for i, row in enumerate(tilemap):
        for j, column in enumerate(row):
            if column == 1:
                tile = Tile("rock-tile1.png", (j*TILE_SIZE), (i*TILE_SIZE))
                tiles.append(tile)

def draw_tiles():
    for tile in tiles:
        surface.blit(tile.image_surface, (tile.image_rect.x-scroll[0], tile.image_rect.y-scroll[1]))
        # surface.blit(tile.image_surface, (tile.image_rect.x, tile.image_rect.y))

def get_tile_collided(player: Player):
    for tile in tiles:
        if tile.image_rect.colliderect(player.rect):
            return tile
    return None

def detect_y_collision(player: Player):
    collided_tile = get_tile_collided(player)
    if player.y_velocity > 0 and collided_tile is not None:
        player.rect.y = collided_tile.image_rect.top - HERO_HEIGHT
        player.y_velocity = 0 
        player.jumping = False
    elif player.y_velocity < 0 and collided_tile is not None:
        player.rect.y = collided_tile.image_rect.bottom
        player.y_velocity = 0

def detect_x_collision(player: Player):
    collided_tile = get_tile_collided(player)
    if player.x_velocity > 0 and collided_tile is not None:
        player.rect.x = collided_tile.image_rect.x - HERO_WIDTH
    elif player.x_velocity < 0 and collided_tile is not None:
        player.rect.x = collided_tile.image_rect.right

class CustomGroup(pygame.sprite.Group):
    def draw(self, surface):
        sprites = self.sprites()
        surface_blit = surface.blit
        for spr in sprites:
            self.spritedict[spr] = surface_blit(spr.image, (spr.rect.x-scroll[0], spr.rect.y-scroll[1])) ### !!!!!

            # taken from scroll_demo.py. Not really needed here
            # pygame.draw.rect(surface, (255, 0, 0), ((spr.rect.x-scroll[0], spr.rect.y-scroll[1]), (spr.rect.w, spr.rect.h)), width=2) ### !!!!!
        self.lostsprites = []

# x = 500 - 42
x = 0
y = 0
pl = Player(x, y)
wand = Wand(pl.rect.centerx, pl.rect.centery)

all_enemy_group = CustomGroup()

# ENEMY CLASS
own_enemy_group = CustomGroup()
flying_enemy_group = CustomGroup()
# ENEMY CLASS

for _ in range(1):
    enemy = Enemy(random.randint(0, GAME_WIDTH), 312)
    own_enemy_group.add(enemy)
    all_enemy_group.add(enemy)

for _ in range(1):
    rand_speed = random.randrange(50, 140)
    flying_enemy = FlyingEnemy(random.randint(0, GAME_WIDTH), 0, rand_speed)
    flying_enemy_group.add(flying_enemy)
    all_enemy_group.add(enemy)

bullet_group = CustomGroup()
player_group = CustomGroup(pl)

explosions = CustomGroup()

wands = CustomGroup(wand)

background_particles = []
particles = []
radiations = []
sparks: list[Spark] = []
dusts = []

true_scroll = [0, 0]
scroll = [0, 0]

create_tilemap()
previous_time = pygame.time.get_ticks()
running = True
while running:
    true_scroll[0] += (pl.rect.x-scroll[0]-(GAME_WIDTH//2 - HERO_WIDTH//2)) / 20 # the higher the slower the camera will move
    true_scroll[1] += (pl.rect.y-scroll[1]-(GAME_HEIGHT//2 - HERO_HEIGHT//2)) / 20

    scroll = true_scroll.copy()
    scroll[0] = int(true_scroll[0])
    scroll[1] = int(true_scroll[1])


    create_background_particles()

    dt = clock.tick(FPS) / 1000
    pygame.display.flip()
    surface.fill((56, 56, 56))

    pygame.draw.rect(surface, (0, 80, 0), ((-GAME_WIDTH-scroll[0]*.5, 300-scroll[1]*.5), (GAME_WIDTH*5, 400))) # add before fill or display flip | no idea

    pygame.draw.rect(surface, (0, 255, 0), ((300-scroll[0]*.5, 250-scroll[1]*.5), (120, 360))) # add before fill or display flip | no idea
    pygame.draw.rect(surface, (0, 120, 160), ((150-scroll[0]*.5, 170-scroll[1]*.5), (120, 360))) # add before fill or display flip | no idea
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    mouse_pos = pygame.mouse.get_pos()
    mouse_hold = pygame.mouse.get_pressed()
    if mouse_hold[0]:
        current_time = pygame.time.get_ticks()
        if current_time - previous_time > 300:
            bullet = Bullet("bullet.png", pl.rect.centerx, pl.rect.centery, dt, pl.x_direction, mouse_pos[0], mouse_pos[1]) #ORIGINAL!!!
            bullet_group.add(bullet)
            previous_time = current_time

    bullet_group.update(tiles, dt)
    bullet_group.draw(surface)
    detect_explosion(explosions, bullet_group.sprites(), tiles)

    keys_hold = pygame.key.get_pressed()
    if keys_hold[pygame.K_SPACE] and not pl.jumping:
        pl.y_velocity = -1300
        pl.jumping = True
    elif keys_hold[pygame.K_d]:
        pl.x_velocity = 300
        pl.x_direction = 1
    elif keys_hold[pygame.K_a]:
        pl.x_velocity = -300
        pl.x_direction = -1
        
    # check_if_enemy_within_aoe(enemy_group.sprites(), explosions.sprites())
    # kill_own_enemy(explosions, own_enemy_group) # PROBLEM: the create_particles function create particles
    # not because the enemy is hit but because enemy gets touched by the explosion
    # kill_flying_enemy(explosions, flying_enemy_group)

    bullet_hit_own_enemy()
    bullet_hit_flying_enemy()
    
    draw_tiles()

    # enemy_group.draw(surface)
    # enemy_group.update(dt)
    check_overlap_own_enemy(own_enemy_group.sprites())
    check_overlap_flying_enemy(flying_enemy_group.sprites())

    draw_particles(particles)
    draw_radiation(radiations)
    draw_background_particles()

    own_enemy_group.draw(surface)
    own_enemy_group.update(pl, dt)

    flying_enemy_group.draw(surface)
    flying_enemy_group.update(pl, dt)

    explosions.update()
    explosions.draw(surface)

    # wand.update(pl, pl.rect.centerx, pl.rect.centery)
    # surface.blit(wand.image, (wand.rect.x-scroll[0], wand.rect.y-scroll[1]))
    wands.draw(surface)
    wands.update(pl, pl.rect.centerx, pl.rect.centery)

    # pl.update(dt)
    # surface.blit(pl.image, (pl.rect.x-scroll[0], pl.rect.y-scroll[1]))
    player_group.draw(surface)
    player_group.update(dt)
    # print(pl.y_velocity)

    draw_sparks()

    create_dust()
    draw_dust()

