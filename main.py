
import sys
import random
import math
import os
import pygame
from pygame.locals import *
#based on pygame pong example

from collections import deque
from queue import PriorityQueue
from collections import defaultdict
from operator import attrgetter

import time

__PATHFIND_A_STAR__ = 0
__PATHFIND_FF__ = 1

PATHFIND = __PATHFIND_FF__

class Unit(pygame.sprite.Sprite):
  def __init__(self, id, pos, speed, squares_dict, squares_list):
    pygame.sprite.Sprite.__init__(self)
    self.id = id
    self.squares_dict = squares_dict
    self.squares_list = squares_list
    self.image = pygame.image.load('data/unit.png').convert_alpha()
    if id == 1:
      self.image.fill([255, 255, 0])
    # print(self.image.get_at([0, 0]))
    self.rect = self.image.get_rect(center=pos)
    screen = pygame.display.get_surface()
    self.area = screen.get_rect()
    self.pos = pygame.Vector2(pos)
    self.direction = pygame.Vector2((1, 1))
    self.target = pygame.Vector2(pos)
    self.speed = speed
    self.pathL = deque()
    self.FF_next_sq = None
  def update(self, dt, units, world):
    # update speed
    # current_square = world[self.xy()]
    current_square = get_square_at_coordinate(world, (int(self.pos[0]), int(self.pos[1])), x_squares, y_squares)
    self.speed = 100 / current_square.cost
    # try:
    # except Exception as e:
    #   print("Error", e, self.id, self.pos)
    #   self.speed = 0

    move_pos = None
    if PATHFIND == __PATHFIND_A_STAR__:
      move_pos = self.move_A_star(dt)
    elif PATHFIND == __PATHFIND_FF__:
      move_pos = self.move_FF(dt, world)

    #Collisons
    any_colision = False
    move_rect = self.image.get_rect(center=move_pos)
    # for u in units:
    tl = not self.area.collidepoint(move_rect.topleft)
    tr = not self.area.collidepoint(move_rect.topright)
    bl = not self.area.collidepoint(move_rect.bottomleft)
    br = not self.area.collidepoint(move_rect.bottomright)
    out_of_bounds = tl or tr or bl or br
    #   if u == self and not out_of_bounds:
    #     continue
    #   print(tl, tr, bl, br)
    #   if move_rect.colliderect(u.rect) or out_of_bounds:
    #     any_colision = True
    #     break
    if not out_of_bounds:
      self.last_pos = self.rect.center
      self.move_to(move_pos)
    else:
      self.pos = self.rect.center
      # print("out of bounds", move_pos)
      
  def move_A_star(self, dt):
    move_pos = self.pos
    if len(self.pathL) > 0:
      next_sq = self.pathL.pop()
      if calc_distance(self, next_sq) < 2:
        self.jumped = False
        self.rect = next_sq.image.get_rect(center=next_sq.rect.center)
      if self.rect.center != next_sq.rect.center:
        self.pathL.append(next_sq)
      # else:
        # print("target", next_sq.xy)
      angle = self.get_angle(next_sq.rect.center)
      movement_v = angle * 1
      move_pos = self.pos
      if movement_v.length() > 0:
        movement_v.normalize_ip()
        # move 100px per second in the direction we're facing
        move_pos += movement_v * dt * self.speed
    return move_pos
  def move_FF(self, dt, world):
    move_pos = self.pos
    if self.FF_next_sq != None:
      if calc_distance(self, self.FF_next_sq) < 2:
        self.rect = self.FF_next_sq.image.get_rect(center=self.FF_next_sq.rect.center)
      if self.rect.center == self.FF_next_sq.rect.center:
        current_sq = world[self.xy()]
        self.FF_next_sq = self.FF_next_sq.FF_next_sq
      if self.FF_next_sq != None:
        # else:
        #   print("target", next_sq.xy)
        angle = self.get_angle(self.FF_next_sq.rect.center)
        movement_v = angle * 1
        move_pos = self.pos
        if movement_v.length() > 0:
          movement_v.normalize_ip()
          # move 100px per second in the direction we're facing
          move_pos += movement_v * dt * self.speed
    return move_pos
  def start_FF(self, world):
    self.FF_next_sq = world[self.xy()]
  def move_to(self, move_pos):
    # self.set_angle(self.target)
    self.rect = self.image.get_rect(center=move_pos)
    self.pos = move_pos

  def calcnewpos(self,rect,vector):
    (angle,z) = vector
    (dx,dy) = (z*math.cos(angle),z*math.sin(angle))
    return rect.move(dx,dy)
  def set_angle(self, xy):
    v = pygame.Vector2(xy[0] - self.rect.center[0], xy[1] - self.rect.center[1])
    self.direction = v
  def get_angle(self, xy):
    return pygame.Vector2(xy[0] - self.rect.center[0], xy[1] - self.rect.center[1])
  def set_target(self, xy):
    self.target = pygame.Vector2(xy)
  def set_finish(self, squares_dict, xy, x_amount, y_amount):
    self.pathL = deque(a_star(get_square_at_coordinate(squares_dict, self.rect.center, x_amount, y_amount), squares_dict, squares_dict[(xy[0], xy[1])], x_amount, y_amount)[0])
    for i in self.pathL:
      i.set_color((255, 0, 0))
  def xy(self):
    return (self.rect.centerx//16, self.rect.centery//16)


class Square(pygame.sprite.Sprite):
  def __init__(self, x, y, cost):
    pygame.sprite.Sprite.__init__(self)
    self.img_FF1 = pygame.image.load('data/FF1.png').convert_alpha()
    self.img_FF2 = pygame.image.load('data/FF2.png').convert_alpha()
    self.img_FF3 = pygame.image.load('data/FF3.png').convert_alpha()
    self.img_FF4 = pygame.image.load('data/FF4.png').convert_alpha()
    self.img_FF6 = pygame.image.load('data/FF6.png').convert_alpha()
    self.img_FF7 = pygame.image.load('data/FF7.png').convert_alpha()
    self.img_FF8 = pygame.image.load('data/FF8.png').convert_alpha()
    self.img_FF9 = pygame.image.load('data/FF9.png').convert_alpha()
    self.img_a_star, self.rect = load_png("square.png")
    self.image = self.img_a_star.copy()
    # self.image.fill([0/cost, 255/cost, 0/cost])
    darken = 255 / cost
    self.image.fill((darken, darken, darken), special_flags=pygame.BLEND_RGB_MULT)
    self.rect.move_ip(x, y)
    screen = pygame.display.get_surface()
    self.area = screen.get_rect()
    #self.vector = vector
    self.cost = cost
    self.xy = (self.rect.centerx//16, self.rect.centery//16)
    self.FF_next_sq = None
    self.FF_cost = 0xFFFFFFFF
  def __lt__(self, other):
    return self.cost < other.cost
  # def update(self):
  #   newpos = self.calcnewpos(self.rect,self.vector)
  #   self.rect = newpos
  #   (angle,z) = self.vector
  def set_pos(self, x, y):
    self.rect = self.rect.move(x, y)
    self.xy = (self.rect.centerx//16, self.rect.centery//16)
  def randomize_cost(self):
    cost = random.randint(1, 8)
    self.cost = cost
    self.image.fill([0/cost, 255/cost, 0/cost])
    # self.FF_next_sq = None
    # self.FF_cost = 0xFFFFFFFF
    # self.image = self.img_a_star
  def set_color(self, rgb):
    self.image.fill([rgb[0]//self.cost, rgb[1]//self.cost, rgb[2]//self.cost])
  def set_FF_img(self, xy):
    direction = (self.xy[0] - xy[0], self.xy[1] - xy[1])
    if direction == (1, 0):
      self.image = self.img_FF4.copy()
    elif direction == (1, 1):
      self.image = self.img_FF7.copy()
    elif direction == (1, -1):
      self.image = self.img_FF1.copy()
    elif direction == (0, 1):
      self.image = self.img_FF8.copy()
    elif direction == (0, 0):
      self.image = self.img_a_star.copy()
    elif direction == (0, -1):
      self.image = self.img_FF2.copy()
    elif direction == (-1, 1):
      self.image = self.img_FF9.copy()
    elif direction == (-1, 0):
      self.image = self.img_FF6.copy()
    elif direction == (-1, -1):
      self.image = self.img_FF3.copy()
    darken = 255 / self.cost
    self.image.fill((darken, darken, darken), special_flags=pygame.BLEND_RGB_MIN)
def calc_distance(start, end, difficulty = 1):
  return math.sqrt((end.rect.center[0] - start.rect.center[0])**2 + (end.rect.center[1] - start.rect.center[1])**2) * difficulty

def get_neighbours(squares_dict, current_sq, size_x, size_y) -> list():
  coords = list()
  for x in range(3):
    for y in range(3):
      if x == 1 and y == 1: continue
      xx = current_sq.rect.center[0]//16 - 1 + x
      yy = current_sq.rect.center[1]//16 - 1 + y
      if (xx >= 0) and (xx <= size_x-1):
        if (yy >= 0) and (yy <= size_y-1):
          if(squares_dict[(xx, yy)].cost < 255):
            coords.append(squares_dict[(xx, yy)])
  return coords

#based on https://en.wikipedia.org/wiki/A*_search_algorithm
def reconstruct_path(cameFrom:dict, current):
  total_path = [current]
  while current in cameFrom.keys():
    current = cameFrom[current]
    total_path.append(current)
  return total_path

def get_difficulty(square):
  return square.cost

def a_star(start, world, end, size_x, size_y):
  visited = list()
  openSet = PriorityQueue()
  openSet.put((0, start))
  cameFrom = dict()
  gScore = defaultdict(lambda: 0xFFFFFFFFFFFFFFFFFFFF)
  fScore = defaultdict(lambda: 0xFFFFFFFFFFFFFFFFFFFF)
  gScore[start] = 0
  fScore[start] = calc_distance(start, end)
  while not openSet.empty():
    current = openSet.get()[1]
    visited.append(current)
    if current == end:
      return reconstruct_path(cameFrom, current), visited

    for neighbor in get_neighbours(world, current, size_x, size_y):
      tentative_gScore = gScore[current] + calc_distance(current, neighbor, neighbor.cost)
      if tentative_gScore < gScore[neighbor]:
        # This path to neighbor is better than any previous one. Record it!
        cameFrom[neighbor] = current
        gScore[neighbor] = tentative_gScore
        fScore[neighbor] = tentative_gScore + calc_distance(neighbor, end)
        if not any(neighbor in sublist for sublist in openSet.queue):
          new = (fScore[neighbor], neighbor)
          openSet.put(new)
  print("A* failed")
#based on https://leifnode.com/2013/12/flow-field-pathfinding/
def calculate_flowfield(world:dict, target, x_amount, y_amount):#world is dict, target is xy
  #integration field
  for sq in world.values():
    sq.FF_cost = 0xFFFFFFFF
  world[target].FF_cost = 0
  square_list = [world[target]]
  finished_nodes = set(target)
  while len(square_list) > 0:
    current_xy = square_list.pop(0).xy
    finished_nodes.add(current_xy)

    neighbours = get_neighbours(world, world[current_xy], x_amount, y_amount)

    for n in neighbours:
      new_cost = world[current_xy].FF_cost + n.cost
      if new_cost < n.FF_cost:
        if n not in square_list:
          square_list.append(n)
        n.FF_cost = new_cost
  #flow field
  for sq in world.values():
    if sq == world[target]:
      sq.FF_next_sq = None
      sq.set_FF_img(sq.xy)
      continue
    neighbours = get_neighbours(world, world[sq.xy], x_amount, y_amount)
    shortest_n = min(neighbours, key=attrgetter("FF_cost"))
    sq.FF_next_sq = shortest_n
    sq.set_FF_img(shortest_n.xy)
def load_png(name):
  """ Load image and return image object"""
  fullname = os.path.join("data", name)
  try:
    image = pygame.image.load(fullname)
    if image.get_alpha is None:
      image = image.convert()
    else:
      image = image.convert_alpha()
  except FileNotFoundError:
    print(f"Cannot load image: {fullname}")
    raise SystemExit
  return image, image.get_rect()
def get_square_idx_at(x, y, x_amount):
  return x//16 + y//16 * x_amount
def get_square_at_coordinate(world:dict, xy, x_amount, y_amount):
  if xy[0] < 0:
    x = 0
  elif xy[0] >= (x_amount * 16):
    x = (x_amount * 16)-1
  else:
    x = xy[0]
  if xy[1] < 0:
    y = 0
  elif xy[1] >= (y_amount * 16):
    y = (y_amount * 16)-1
  else:
    y = xy[1]
  return world[(int(x//16), int(y//16))]

def test_make_units(units_amount, world_list, world):
  units = list()
  for i in range(units_amount):
    units.append(Unit(i, (random.randint(8, x_squares * 16 - 8), random.randint(8, y_squares * 16 - 8)), 100, world, world_list))
  return units
def test_make_squares(x_amount, y_amount):
  squares = []
  squares_dict = {}
  for ysq in range(x_amount):
    for xsq in range(y_amount):
      s = Square(16 * xsq, 16 * ysq, random.randint(1, 8))
      squares.append(s)
      squares_dict[(xsq, ysq)] = s
  return squares, squares_dict
def test_ff():
  #FF with different size worlds
  f = open("metrics/FF_world_size.csv", "w")
  f.write("size,time\n")
  for i in range(10, 101, 5):
    print("test_ff", i)
    world_list, world = test_make_squares(i, i)
    runs = 5
    start_time = time.time()
    for r in range(runs):
      calculate_flowfield(world, random.choice(world_list).xy, i, i)
    end_time = time.time() - start_time
    f.write(f"{i},{end_time / runs}\n")
  f.close()

def test_A_star():
  #FF with different size worlds
  f = open("metrics/A_star.csv", "w")
  f.write("size,units,total_time,unit_time\n")
  for i in [10, 20, 50, 100]:
    world_list, world = test_make_squares(i, i)
    for u_amount in [1, 5, 50, 100, 1000, 5000, 10000]:
      print("test_A_star", i, u_amount)
      units = test_make_units(u_amount, world_list, world)
      runs = 5
      start_time = time.time()
      for r in range(runs):
        target = random.choice(world_list)
        for u in units:
          u.set_finish(world, target.xy, i, i)
      end_time = time.time() - start_time
      f.write(f"{i},{len(units)},{end_time / runs},{end_time / runs / len(units)}\n")
  f.close()

def main():
  # Initialise screen
  pygame.init()
  global x_squares, y_squares, x_squares, y_squares
  x_squares = 100
  y_squares = 50 
  screen = pygame.display.set_mode((x_squares * 16, y_squares * 16))
  pygame.display.set_caption(f'Flow field pathfinding {x_squares * 16} x {y_squares * 16}')

  # Fill background
  background = pygame.Surface(screen.get_size())
  background = background.convert()
  background.fill((250, 250, 250))
  
  # test2()
  # units = [Unit(0, (100, 100), 100), Unit(1, (8, 8),50), Unit(2, (8, 8),100)]
  # units = [Unit(0, (8, 8), 100), Unit(1, (150, 150), 100)]

  

  squares = []
  squares_dict = {}
  for ysq in range(y_squares):
    for xsq in range(x_squares):
      s = Square(16 * xsq, 16 * ysq, random.randint(1, 8))
      squares.append(s)
      squares_dict[(xsq, ysq)] = s

  units = list()
  for i in range(25):
    units.append(Unit(i, (random.randint(8, x_squares * 16 - 8), random.randint(8, y_squares * 16 - 8)), 100, squares_dict, squares))
  
  unitsprites = pygame.sprite.RenderPlain(units)
  sqprites = pygame.sprite.RenderPlain(squares)

  # calculate_flowfield(squares_dict, (10, 10))
  # path = a_star(squares[0], squares_dict, squares[-1], x_squares, y_squares)
  # for i in path[0]:
  #   # print(i.xy)
  #   i.set_color((255, 0, 0))

  # Blit everything to the screen
  screen.blit(background, (0, 0))
  pygame.display.flip()

  clock, dt = pygame.time.Clock(), 0

  # Event loop
  while True:
    for sq in squares:
      screen.blit(background, sq.rect, sq.rect)
      sq.update()
    sqprites.draw(screen)

    for unit in units:
      screen.blit(background, unit.rect, unit.rect)
      unit.update(dt, units, squares_dict)
    unitsprites.draw(screen)

    for event in pygame.event.get():
      # print(event)
      if event.type == QUIT:
        return
      elif event.type == MOUSEBUTTONDOWN:
        print(event)
        pos = pygame.mouse.get_pos()
        pos = pos[0]//16, pos[1]//16
        print("pos", pos)
        # squares_dict[pos].randomize_cost()
        start_time = time.time()
        if PATHFIND == __PATHFIND_A_STAR__:
          #measure A* time here
          for u in units:
            u.set_finish(squares_dict, pos, x_squares, y_squares)
        elif PATHFIND == __PATHFIND_FF__:
          calculate_flowfield(squares_dict, pos, x_squares, y_squares)
        print("--- %s seconds ---" % (time.time() - start_time))
        for u in units:
          u.start_FF(squares_dict)
      elif event.type == TEXTINPUT and event.__dict__['text'] == ' ':
        print(event)
        for u in units:
          u.move_to((random.randint(8, x_squares * 16 - 8), random.randint(8, y_squares * 16 - 8)))
        for sq in squares:
          sq.randomize_cost()

    pygame.display.flip()
    dt = clock.tick(60) / 1000


if __name__ == '__main__': main()