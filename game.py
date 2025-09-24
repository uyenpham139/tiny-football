import pygame, os

WIDTH = 1600
HEIGHT = 900
BG = os.path.join("assets", "Field", "Only Field.png")

class Game:
  def __init__(self):
    pygame.init()
    self.width, self.height = WIDTH, HEIGHT
    self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
    pygame.display.set_caption("Tiny football")
    self.clock = pygame.time.Clock()
    
    # selection state
    self.selected_mode = None  # 'pvp' or 'pvai'
    self.selected_side = None
    self.selected_side_p2 = None

    # load background once
    try:
      self.bg_img = pygame.image.load(BG).convert()
      self.scaled_bg = pygame.transform.smoothscale(self.bg_img, (self.width, self.height))
    except (pygame.error, FileNotFoundError):
      self.bg_img = pygame.Surface((self.width, self.height))
      self.bg_img.fill((30, 100, 30))
      self.scaled_bg = self.bg_img

    # control flags
    self.running = True
    self.playing = False  # toggled on when game starts from main.py

  def draw_text(self, text, size, color, x, y):
    try:
      font = pygame.font.Font("assets/fonts/LuckiestGuy-Regular.ttf", size)
    except (pygame.error, FileNotFoundError):
      font = pygame.font.Font(None, size)

    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    return text_surface, text_rect

  def draw(self):
    """Draw the game background (and later gameplay elements)."""
    self.screen.blit(self.scaled_bg, (0, 0))
    pygame.display.flip()

  def events(self):
    """Handle input while the game is playing."""
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        self.running = False
        self.playing = False
      elif event.type == pygame.VIDEORESIZE:
        self.width, self.height = event.w, event.h
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        # rescale background only on resize
        self.scaled_bg = pygame.transform.smoothscale(self.bg_img, (self.width, self.height))
      elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        # ESC should stop playing, return to menu
        self.playing = False
