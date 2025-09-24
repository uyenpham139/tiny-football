import pygame, math, os

FRICTION_FACTOR = 0.98
VELOCITY_THRESHOLD = 0.05

class Ball:
  def __init__(self, width, height, player_size, x, y):
    self.width = width
    self.height = height
    self.player_size = player_size

    # bigger ball if you used the larger values earlier
    self.radius = 22
    self.speed = 6
    self.vx, self.vy = 0.0, 0.0
    self.x, self.y = float(x), float(y)

    # who last touched the ball: None, 0 (p1), or 1 (p2)
    self.last_touch = None

    # Load ball image (fallback circle)
    try:
      raw_img = pygame.image.load(os.path.join("assets", "ball.png")).convert_alpha()
    except (pygame.error, FileNotFoundError):
      raw_img = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
      pygame.draw.circle(raw_img, (255, 255, 255), (self.radius, self.radius), self.radius)

    # Scale to ball radius
    self.image = pygame.transform.smoothscale(raw_img, (self.radius*2, self.radius*2))
    self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

  def move(self):
    # integrate
    self.x += self.vx
    self.y += self.vy

    # Bounce on left/right walls (treat edges as solid walls)
    if self.x - self.radius <= 0:
      self.x = self.radius
      self.vx *= -1
    elif self.x + self.radius >= self.width:
      self.x = self.width - self.radius
      self.vx *= -1

    # Bounce on top/bottom walls
    if self.y - self.radius <= 0:
      self.y = self.radius
      self.vy *= -1
    elif self.y + self.radius >= self.height:
      self.y = self.height - self.radius
      self.vy *= -1

    # friction
    self.vx *= FRICTION_FACTOR
    self.vy *= FRICTION_FACTOR

    if abs(self.vx) < VELOCITY_THRESHOLD:
      self.vx = 0.0
    if abs(self.vy) < VELOCITY_THRESHOLD:
      self.vy = 0.0

    # update rect for drawing
    self.rect.center = (int(self.x), int(self.y))

  def collide_rect(self, rect):
    # circle-rect collision test
    closest_x = max(rect.left, min(self.x, rect.right))
    closest_y = max(rect.top, min(self.y, rect.bottom))
    dx = self.x - closest_x
    dy = self.y - closest_y
    return (dx * dx + dy * dy) < (self.radius * self.radius)

  def kick(self, player_rect, player_id):
    """
    player_id: 0 for P1, 1 for P2
    If player is within kick range, set velocity away from player and record last_touch.
    """
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
