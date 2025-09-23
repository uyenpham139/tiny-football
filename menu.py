import pygame, os
from button import Button

class Menu:
  def __init__(self, game):
    self.game = game

    # flags for main loop
    self.start_selected = False
    self.quit_selected = False

    # Load background image
    try:
      self.bg = pygame.image.load(os.path.join("assets", "menu-bg.png")).convert()
      self.scaled_bg = pygame.transform.smoothscale(self.bg, (self.game.width, self.game.height))
    except (pygame.error, FileNotFoundError):
      self.bg = pygame.Surface((self.game.width, self.game.height))
      self.bg.fill((40, 40, 80))
      self.scaled_bg = self.bg

    # Load button image
    try:
      self.button_img = pygame.image.load(os.path.join("assets", "menu-button.png")).convert_alpha()
    except (pygame.error, FileNotFoundError):
      self.button_img = pygame.Surface((200, 50))
      self.button_img.fill((100, 100, 100))

    # Load font once
    try:
      self.button_font = pygame.font.Font("assets/fonts/LuckiestGuy-Regular.ttf", 50)
    except (pygame.error, FileNotFoundError):
      self.button_font = pygame.font.Font(None, 35)

  def draw_text_with_stroke(self, surface, button, text, font, color, stroke_color, stroke_width=2):
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=button.rect.center)

    # stroke
    for dx in range(-stroke_width, stroke_width + 1):
      for dy in range(-stroke_width, stroke_width + 1):
        if dx == 0 and dy == 0:
          continue
        stroke_surf = font.render(text, True, stroke_color)
        stroke_rect = stroke_surf.get_rect(center=(button.rect.centerx + dx, button.rect.centery + dy))
        surface.blit(stroke_surf, stroke_rect)

    surface.blit(text_surf, text_rect)

  def events(self):
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        self.game.running = False
      elif event.type == pygame.VIDEORESIZE:
        self.game.width, self.game.height = event.w, event.h
        self.game.screen = pygame.display.set_mode((self.game.width, self.game.height), pygame.RESIZABLE)
        self.scaled_bg = pygame.transform.smoothscale(self.bg, (self.game.width, self.game.height))
      elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
          self.game.running = False

  def draw(self):
    # background
    self.game.screen.blit(self.scaled_bg, (0, 0))

    # button size
    button_width = self.game.width // 6
    button_height = int(self.button_img.get_height() * (button_width / self.button_img.get_width()))
    scaled_button_img = pygame.transform.smoothscale(self.button_img, (button_width, button_height))

    # positions
    dist_x = self.game.width // 2 - button_width - 10
    dist_y = self.game.height - button_height - 100

    start_button = Button(dist_x, dist_y, scaled_button_img, self.game)
    quit_button = Button(dist_x + button_width + 20, dist_y, scaled_button_img, self.game)

    if start_button.draw():
      self.start_selected = True

    if quit_button.draw():
      self.quit_selected = True

    self.draw_text_with_stroke(self.game.screen, start_button, "PLAY", self.button_font, (255, 255, 255), (0, 0, 0), stroke_width=5)
    self.draw_text_with_stroke(self.game.screen, quit_button, "QUIT", self.button_font, (255, 255, 255), (0, 0, 0), stroke_width=5)

    pygame.display.flip()
