import pygame, os
from button import Button

class Menu:
  def __init__(self, screen, width, height):
    self.screen = screen
    self.width = width
    self.height = height

    self.start_selected = False
    self.quit_selected = False

    try:
      self.bg = pygame.image.load(os.path.join("assets", "menu-bg.png")).convert()
      self.scaled_bg = pygame.transform.smoothscale(self.bg, (self.width, self.height))
    except (pygame.error, FileNotFoundError):
      self.bg = pygame.Surface((self.width, self.height))
      self.bg.fill((40, 40, 80))
      self.scaled_bg = self.bg

    try:
      self.button_img = pygame.image.load(os.path.join("assets", "menu-button.png")).convert_alpha()
    except (pygame.error, FileNotFoundError):
      self.button_img = pygame.Surface((200, 50))
      self.button_img.fill((100, 100, 100))

    # load font dynamically
    self._load_font()

  def _load_font(self):
    """Load font with size based on current window size."""
    # for example: 6% of window height
    font_size = max(20, int(self.height * 0.06))
    try:
      self.button_font = pygame.font.Font("assets/fonts/LuckiestGuy-Regular.ttf", font_size)
    except (pygame.error, FileNotFoundError):
      self.button_font = pygame.font.Font(None, font_size)

  def resize(self, width, height, screen):
    """Update menu when window is resized."""
    self.width = width
    self.height = height
    self.screen = screen
    self.scaled_bg = pygame.transform.smoothscale(self.bg, (self.width, self.height))
    self._load_font()   # reload font with new size

  def draw_text_with_stroke(self, surface, button, text, font, color, stroke_color, stroke_width=2):
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=button.rect.center)

    for dx in range(-stroke_width, stroke_width + 1):
      for dy in range(-stroke_width, stroke_width + 1):
        if dx == 0 and dy == 0:
          continue
        stroke_surf = font.render(text, True, stroke_color)
        stroke_rect = stroke_surf.get_rect(center=(button.rect.centerx + dx, button.rect.centery + dy))
        surface.blit(stroke_surf, stroke_rect)

    surface.blit(text_surf, text_rect)

  def events(self, events):
    for event in events:
      if event.type == pygame.QUIT:
        pass
      elif event.type == pygame.VIDEORESIZE:
        self.width, self.height = event.w, event.h
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        self.scaled_bg = pygame.transform.smoothscale(self.bg, (self.width, self.height))
        self._load_font()
      elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        self.quit_selected = True

  def draw(self):
    self.screen.blit(self.scaled_bg, (0, 0))

    button_width = self.width // 6
    button_height = int(self.button_img.get_height() * (button_width / self.button_img.get_width()))
    scaled_button_img = pygame.transform.smoothscale(self.button_img, (button_width, button_height))

    dist_x = self.width // 2 - button_width - 10
    dist_y = self.height - button_height - 100

    start_button = Button(dist_x, dist_y, scaled_button_img, self.screen)
    quit_button = Button(dist_x + button_width + 20, dist_y, scaled_button_img, self.screen)

    if start_button.draw():
      self.start_selected = True

    if quit_button.draw():
      self.quit_selected = True

    self.draw_text_with_stroke(self.screen, start_button, "PLAY", self.button_font, (255, 255, 255), (0, 0, 0), stroke_width=5)
    self.draw_text_with_stroke(self.screen, quit_button, "QUIT", self.button_font, (255, 255, 255), (0, 0, 0), stroke_width=5)
