import pygame, math, os

FRICTION_FACTOR = 0.98
VELOCITY_THRESHOLD = 0.05

class Ball:
  def __init__(self, width, height, player_size, x, y):
    self.width = width
    self.height = height
    self.player_size = player_size    
    self.last_collision_side = None

    self.radius = 22
    self.speed = 6
    self.vx, self.vy = 0.0, 0.0
    self.x, self.y = float(x), float(y)

    self.last_touch = None

    try:
      raw_img = pygame.image.load(os.path.join("assets", "ball.png")).convert_alpha()
    except (pygame.error, FileNotFoundError):
      raw_img = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
      pygame.draw.circle(raw_img, (255, 255, 255), (self.radius, self.radius), self.radius)

    self.image = pygame.transform.smoothscale(raw_img, (self.radius*2, self.radius*2))
    self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

  def move(self, play_area, goal_left, goal_right):
    self.last_collision_side = None
    self.x += self.vx
    self.y += self.vy

    main_rect = play_area[0]  # rect chính

    # Top
    if self.y - self.radius <= main_rect.top:
      self.y = main_rect.top + self.radius
      self.vy *= -1
      self.last_collision_side = "top"

    # Bottom
    elif self.y + self.radius >= main_rect.bottom:
      self.y = main_rect.bottom - self.radius
      self.vy *= -1
      self.last_collision_side = "bottom"

    # Left edge (trừ phần goal)
    if self.x - self.radius <= main_rect.left:
      if not goal_left.colliderect(self.rect):
        self.x = main_rect.left + self.radius
        self.vx *= -1
        self.last_collision_side = "left"

    # Right edge (trừ phần goal)
    elif self.x + self.radius >= main_rect.right:
      if not goal_right.colliderect(self.rect):
        self.x = main_rect.right - self.radius
        self.vx *= -1
        self.last_collision_side = "right"

    # friction
    self.vx *= FRICTION_FACTOR
    self.vy *= FRICTION_FACTOR
    if abs(self.vx) < VELOCITY_THRESHOLD: self.vx = 0.0
    if abs(self.vy) < VELOCITY_THRESHOLD: self.vy = 0.0

    self.rect.center = (int(self.x), int(self.y))


  def collide_rect(self, rect):
    closest_x = max(rect.left, min(self.x, rect.right))
    closest_y = max(rect.top, min(self.y, rect.bottom))
    dx = self.x - closest_x
    dy = self.y - closest_y
    return (dx * dx + dy * dy) < (self.radius * self.radius)

  def kick(self, player_rect, player_id):
    px, py = player_rect.center
    dx = self.x - px
    dy = self.y - py
    dist = math.hypot(dx, dy)
    if dist < self.radius + (self.player_size / 2) + 5:
      dist = dist or 1.0
      self.vx = (dx / dist) * self.speed
      self.vy = (dy / dist) * self.speed
      self.last_touch = player_id

  def draw(self, screen):
    screen.blit(self.image, self.rect)
