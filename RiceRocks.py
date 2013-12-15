# program template for Spaceship
import simplegui
import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
time = 0.5
score = 0
lives = 3
started = False

class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

    
# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris = ["debris1_blue.png", "debris2_blue.png", "debris3_blue.png", "debris4_blue.png", "debris_blend.png", 
          "debris1_brown.png", "debris2_brown.png", "debris3_brown.png", "debris4_brown.png"]
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/" + random.choice(debris))

# nebula images - nebula_brown.png, nebula_blue.png
nebulas = ["nebula_brown.png", "nebula_blue.png"]
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/" + random.choice(nebulas))

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missiles = ["shot1.png", "shot2.png", "shot3.png"]
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/" + random.choice(missiles))

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = [simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png"),
                  simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_brown.png"),
                  simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blend.png")]

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosions = ["explosion_orange.png", "explosion_blue.png", "explosion_blue2.png", "explosion_alpha.png"]
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/" + random.choice(explosions))
ship_explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/" + random.choice(explosions))
 
# sound assets purchased from sounddogs.com, please do not redistribute
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

# helper functions to handle transformations
def new_game():
    global started, rock_vel, rock_group, missile_group, my_ship, explosion_group
    started = False
    rock_group = set([])
    missile_group = set([])
    explosion_group= set([])
    rock_vel = .1
    my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
    
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p,q):
    return math.sqrt((p[0] - q[0]) ** 2+(p[1] - q[1]) ** 2)

def process_sprite_group(group, canvas):
    remove_item = set([])
    for item in group:
        if not item.update():
            remove_item.add(item)
        item.draw(canvas)
    group.difference_update(remove_item)
    
def group_collide(group, other_object):
    #Returns true is other_object collides with any member of group
    remove = set([])
    for obj in set(group):
        if obj.collide(other_object):
            remove.add(obj)
            explosion = Sprite(obj.get_position(), obj.get_velocity(), 0, 0, explosion_image, explosion_info, explosion_sound)
            explosion_group.add(explosion)
            group.difference_update(remove)
            return True
        
def group_group_collide(group1, group2):
    #returns the count of collisions of group1 with group2 
    count = 0
    for obj in set(group1):
        if group_collide(group2, obj):
            group1.discard(obj)
            count += 1
    return count
    
# Ship class
class Ship:
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        
    def draw(self,canvas):
        canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)

    def update(self):
        self.angle += self.angle_vel
        self.forward = angle_to_vector(self.angle)
        for i in range(2):
            self.pos[i] += self.vel[i] * 0.09
            self.vel[i] *= (1 - 0.01)
            if self.thrust:
                self.vel[i] += self.forward[i]
                
        self.pos[0] %= WIDTH
        self.pos[1] %= HEIGHT
        
    def get_radius(self):
        return self.radius
    
    def get_velocity(self):
        return self.vel
    
    def get_position(self):
        return self.pos
    
    def thrust_on(self):
        self.thrust = True
        self.image_center = [135, 45]
        ship_thrust_sound.play()
        
    def thrust_off(self):
        ship_thrust_sound.rewind()
        ship_thrust_sound.pause()
        self.thrust = False
        self.image_center = [45, 45]
        
    def set_angle_vel(self, ang_vel):
        self.angle_vel = ang_vel
        
    def shoot(self):
        missile_sound.rewind()
        missile_sound.play()
        vel = [self.forward[0] * 8 + self.vel[0] * 0.07, self.forward[1] * 8 + self.vel[1] * 0.07]
        position = [self.pos[0] + self.radius * self.forward[0], self.pos[1] + self.radius * self.forward[1]]
        missile_group.add(Sprite(position, vel, 0, 0, missile_image, missile_info, missile_sound))
        
# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()
   
    def draw(self, canvas):
        if self.animated:
            canvas.draw_image(self.image, [self.image_center[0] + self.image_size[0] * self.age, self.image_center[1]], self.image_size, self.get_position(), self.image_size)	
        else:
            canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)    
    
    def update(self):
        self.angle += self.angle_vel
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.pos[0] %= WIDTH
        self.pos[1] %= HEIGHT
        self.age += 1
        return self.age <= self.lifespan
        
    def collide(self, other_object):
        global score, rock_vel
        radius = other_object.get_radius()
        position = other_object.get_position()
        if dist(position, self.pos) <= self.radius + radius :
            explosion_sound.rewind()
            explosion_sound.play()
            if score % 100 == 0:
                rock_vel += .1
            return True
        else: 
            return False
     
    def get_radius(self):
        return self.radius
    
    def get_position(self):
        return self.pos
    
    def get_velocity(self):
        return self.vel
        
def draw(canvas):
    global time, lives, score

    # animiate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    
    # draw ship and sprites
    my_ship.draw(canvas)
    process_sprite_group(rock_group, canvas)
    process_sprite_group(missile_group, canvas)
    process_sprite_group(explosion_group, canvas)
    
    # update ship and sprites
    my_ship.update()
    
    # detect collision of ship and rocks
    if group_collide(rock_group, my_ship):
        lives -= 1
        explosion = Sprite(my_ship.get_position(), [0, 0], 0, 0, ship_explosion_image, explosion_info, explosion_sound)
        explosion_group.add(explosion)
    if lives == 0:
        soundtrack.pause()
        new_game()
        
    score += group_group_collide(missile_group, rock_group) * 10
    
    # draw scores and lives
    canvas.draw_text("Lives", [50, 50], 22, "White")
    canvas.draw_text("Scores", [650, 50], 22, "White")
    canvas.draw_text(str(lives), [50, 80], 22, "White")
    canvas.draw_text(str(score), [650, 80], 22, "White")

    # draw splash screen
    if not started:
        size = splash_info.get_size()
        canvas.draw_image(splash_image, 
                          [size[0] // 2, size[1] // 2],
                          size, [WIDTH // 2, HEIGHT // 2], size)
    
def keydown(key):
    if started:
        if key == simplegui.KEY_MAP['up']:
            my_ship.thrust_on()
        elif key == simplegui.KEY_MAP['right']:
            my_ship.set_angle_vel(.049)
        elif key == simplegui.KEY_MAP['left']:
            my_ship.set_angle_vel(-.049)
        elif key == simplegui.KEY_MAP['space']:
            my_ship.shoot()
        
def keyup(key):
    if key == simplegui.KEY_MAP['up']:
        my_ship.thrust_off()
    elif key == simplegui.KEY_MAP['left'] or key == simplegui.KEY_MAP['right']:
        my_ship.set_angle_vel(0)
        
def click(pos):
    global started, lives, score
    center = [WIDTH // 2, HEIGHT // 2]
    size = splash_info.get_size()
    inwidth = center[0] - size[0] / 2 < pos[0] < center[0] + size[0] / 2
    inheight = center[1] - size[1] / 2 < pos[1] < center[1] + size[1] / 2
    if (not started) and inwidth and inheight:
        soundtrack.rewind()
        soundtrack.play()
        score = 0
        lives = 3
        started = True
        
# timer handler that spawns a rock    
def rock_spawner():
    if started and len(rock_group) <= 12:
        a_rock = Sprite([random.randrange(WIDTH), random.randrange(HEIGHT)], [.1 + random.randrange(-2, 3) * rock_vel, .1 + random.randrange(-2, 3) * rock_vel], 0, random.randrange(-1, 2)*0.1, random.choice(asteroid_image), asteroid_info)
        if dist(a_rock.get_position(), my_ship.get_position()) > a_rock.get_radius() + my_ship.get_radius() + 50:
            rock_group.add(a_rock)
    
# initialize frame
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# register handlers
frame.set_draw_handler(draw)
frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)
frame.set_mouseclick_handler(click)
timer = simplegui.create_timer(1000.0, rock_spawner)

# get things rolling
timer.start()
new_game()
frame.start()