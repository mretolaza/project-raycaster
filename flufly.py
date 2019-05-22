import pygame
from math import pi, cos, sin, atan2


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BACKGROUND = (0, 255, 255)
BLOCK_SIZE = 40



wall1 = pygame.image.load('wall/wall1.png')
wall2 = pygame.image.load('wall/wall2.png')
wall3 = pygame.image.load('wall/wall3.png')
wall4 = pygame.image.load('wall/wall4.png')
wall5 = pygame.image.load('wall/wall5.png')

textures = {
  "1": wall1,
  "2": wall2,
  "3": wall3,
  "4": wall4,
  "5": wall5,
}
hand = pygame.image.load('player/player.png')

enemies = [
  {
    "x": 95,
    "y": 95,
    "texture": pygame.image.load('sprite/sprite2.png')
  },
  {
    "x": 280,
    "y": 100,
    "texture": pygame.image.load('sprite/sprite3.png')
  },
  {
    "x": 225,
    "y": 340,
    "texture": pygame.image.load('sprite/sprite4.png')
  },
  {
    "x": 220,
    "y": 425,
    "texture": pygame.image.load('sprite/sprite1.png')
  },
  {
    "x": 320,
    "y": 420,
    "texture": pygame.image.load('sprite/sprite2.png')
  }
]

class Raycaster(object):
  def __init__(self, screen):
    _, _, self.width, self.height = screen.get_rect()
    self.screen = screen
    self.blocksize = BLOCK_SIZE
    self.player = {
      "x": self.blocksize + 20,
      "y": self.blocksize + 20,
      "a": pi/3,
      "fov": pi/3
    }
    self.map = []
    self.zbuffer = [-float('inf') for z in range(0, 500)]
    # self.clear()

  def clear(self):
    for x in range(self.width):
      for y in range(self.height):
        r = int((x/self.width)*255) if x/self.width < 1 else 1
        g = int((y/self.height)*255) if y/self.height < 1 else 1
        b = 0
        color = (r, g, b)
        self.point(x, y, color)

  def point(self, x, y, c = None):
    screen.set_at((x, y), c)

  def load_map(self, filename):
    with open(filename) as f:
      for line in f.readlines():
        self.map.append(list(line))

  def cast_ray(self, a):
    d = 0
    while True:
      x = self.player["x"] + d*cos(a)
      y = self.player["y"] + d*sin(a)

      i = int(x/BLOCK_SIZE)
      j = int(y/BLOCK_SIZE)

      if self.map[j][i] != ' ':
        hitx = x - i*BLOCK_SIZE
        hity = y - j*BLOCK_SIZE

        if 1 < hitx < BLOCK_SIZE - 1:
          maxhit = hitx
        else:
          maxhit = hity

        tx = int(maxhit * 128 / BLOCK_SIZE)

        return d, self.map[j][i], tx

      d += 1

  def draw_stake(self, x, h, texture, tx):
    start = int(250 - h/2)
    end = int(250 + h/2)
    for y in range(start, end):
      ty = int(((y - start)*128)/(end - start))
      c = texture.get_at((tx, ty))
      self.point(x, y, c)

  def draw_sprite(self, sprite):
    sprite_a = atan2(sprite["y"] - self.player["y"], sprite["x"] - self.player["x"])   # why atan2? https://stackoverflow.com/a/12011762
    sprite_d = ((self.player["x"] - sprite["x"])**2 + (self.player["y"] - sprite["y"])**2)**0.5
    sprite_size = (250/sprite_d) * 70

    sprite_x = (sprite_a - self.player["a"])*500/self.player["fov"] + 250 - sprite_size/2
    sprite_y = 250 - sprite_size/2

    sprite_x = int(sprite_x)
    sprite_y = int(sprite_y)
    sprite_size = int(sprite_size)

    for x in range(sprite_x, sprite_x + sprite_size):
      for y in range(sprite_y, sprite_y + sprite_size):
        if  0 < x < 500 and self.zbuffer[x] >= sprite_d:
          tx = int((x - sprite_x) * 128/sprite_size)
          ty = int((y - sprite_y) * 128/sprite_size)
          c = sprite["texture"].get_at((tx, ty))
          if c != (152, 0, 136, 255):
            self.point(x, y, c)
            self.zbuffer[x] = sprite_d

  def draw_player(self, xi, yi, w = 256, h = 256):
    for x in range(xi, xi + w):
      for y in range(yi, yi + h):
        tx = int((x - xi) * 32/w)
        ty = int((y - yi) * 32/h)
        c = hand.get_at((tx, ty))
        if c != (152, 0, 136, 255):
          self.point(x, y, c)

  def render(self):
    for i in range(0, 500):
      a =  self.player["a"] - self.player["fov"]/2 + self.player["fov"]*i/500
      d, c, tx = self.cast_ray(a)
      x = i
      h = 500/(d*cos(a-self.player["a"])) * 70
      self.draw_stake(x, h, textures[c], tx)
      self.zbuffer[i] = d

    for enemy in enemies:
      self.point(enemy["x"], enemy["y"], (0, 0, 0))
      self.draw_sprite(enemy)

    self.draw_player(500 - 256 - 125, 500 - 256)

pygame.init()
screen = pygame.display.set_mode((500, 500), pygame.DOUBLEBUF|pygame.HWACCEL|pygame.FULLSCREEN|pygame.HWSURFACE)
screen.set_alpha(None)
r = Raycaster(screen)
r.load_map('./map.txt')

c = 0
while True:
  screen.fill((113, 113, 113))
  r.render()

  for e in pygame.event.get():
    if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
      exit(0)
    if e.type == pygame.KEYDOWN:
      if e.key == pygame.K_a:
        r.player["a"] -= pi/10
      elif e.key == pygame.K_d:
        r.player["a"] += pi/10

      elif e.key == pygame.K_RIGHT:
        r.player["x"] += 10
      elif e.key == pygame.K_LEFT:
        r.player["x"] -= 10
      elif e.key == pygame.K_UP:
        r.player["y"] += 10
      elif e.key == pygame.K_DOWN:
        r.player["y"] -= 10

      if e.key == pygame.K_f:
        if screen.get_flags() and pygame.FULLSCREEN:
            pygame.display.set_mode((500, 500))
        else:
            pygame.display.set_mode((500, 500),  pygame.DOUBLEBUF|pygame.HWACCEL|pygame.FULLSCREEN)

  pygame.display.flip()