import pygame
from button import Button
import os

class OptionMenu:
  def __init__(self, game):
    self.game = game

    # selection result
    self.selected_mode = None  # 'pvp' or 'pvai'

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

  def draw_multiline_with_stroke(self, surface, button, lines, font, color, stroke_color, line_spacing=6, stroke_width=2):
    line_surfaces = [font.render(line, True, color) for line in lines]
    line_heights = [surf.get_height() for surf in line_surfaces]
    total_height = sum(line_heights) + line_spacing * (len(lines) - 1)
    current_y = button.rect.centery - total_height // 2

    for index, line in enumerate(lines):
      line_surf = line_surfaces[index]
      line_h = line_heights[index]
      center_y = current_y + line_h // 2

      # stroke
      for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
          if dx == 0 and dy == 0:
            continue
          stroke_surf = font.render(line, True, stroke_color)
          stroke_rect = stroke_surf.get_rect(center=(button.rect.centerx + dx, center_y + dy))
          surface.blit(stroke_surf, stroke_rect)

      text_rect = line_surf.get_rect(center=(button.rect.centerx, center_y))
      surface.blit(line_surf, text_rect)
      current_y += line_h + line_spacing

  def events(self):
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        self.game.running = False
      elif event.type == pygame.VIDEORESIZE:
        self.game.width, self.game.height = event.w, event.h
        self.game.screen = pygame.display.set_mode((self.game.width, self.game.height), pygame.RESIZABLE)
      elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
          self.game.running = False

  def draw(self):
    # solid blue background
    self.game.screen.fill((0, 0, 255))

    # button sizing
    text_pvp_w, text_pvp_h = self.button_font.size("PLAYER")
    text_vs_w, text_vs_h = self.button_font.size("VS")
    text_pvai_w, text_pvai_h = self.button_font.size("AI")

    max_text_w = max(text_pvp_w, text_vs_w, text_pvai_w)
    max_text_h = max(text_pvp_h, text_vs_h, text_pvai_h)

    pad_x, pad_y = 40, 20
    base_width = self.game.width // 6 if self.button_img.get_width() > 0 else 200
    extra_width = 100
    target_width = max(base_width, max_text_w + pad_x * 2) + extra_width

    src_w = max(self.button_img.get_width(), 1)
    src_h = max(self.button_img.get_height(), 1)
    ratio = src_h / src_w
    target_height = int(target_width * ratio)

    line_spacing = 6
    total_text_height = max_text_h * 3 + line_spacing * 2
    target_height = max(target_height, total_text_height + pad_y * 2)

    scaled_button_img = pygame.transform.smoothscale(self.button_img, (target_width, target_height))

    # positions
    x = self.game.width // 2 - target_width // 2
    spacing = 20
    y1 = self.game.height // 2 - target_height - spacing // 2
    y2 = self.game.height // 2 + spacing // 2

    pvp_button = Button(x, y1, scaled_button_img, self.game)
    pvai_button = Button(x, y2, scaled_button_img, self.game)

    if pvp_button.draw():
      self.selected_mode = 'pvp'

    if pvai_button.draw():
      self.selected_mode = 'pvai'

    self.draw_multiline_with_stroke(self.game.screen, pvp_button, ["PLAYER", "VS", "PLAYER"], self.button_font, (255, 255, 255), (0, 0, 0), stroke_width=5)
    self.draw_multiline_with_stroke(self.game.screen, pvai_button, ["PLAYER", "VS", "AI"], self.button_font, (255, 255, 255), (0, 0, 0), stroke_width=5)

    pygame.display.flip()
