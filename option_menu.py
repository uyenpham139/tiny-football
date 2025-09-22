import pygame
from button import Button
import os

class OptionMenu:
  def __init__(self, game):
    self.game = game
    self.option_displaying = False
    
    self.teams = ['Blue', 'Red']
    
    # Player states
    self.p1 = {"team": 0, "character": 0, "confirmed": False}
    self.p2 = {"team": 0, "character": 0, "confirmed": False}
    
    # Selection state
    self.selected_mode = None  # 'pvp' or 'pvai'
    
    # Load background image (only field, no border)
    try:
      self.bg = pygame.image.load(os.path.join("assets", "Field", "Only Field.png")).convert()
    except (pygame.error, FileNotFoundError):
      self.bg = pygame.Surface((self.game.width, self.game.height))
      self.bg.fill((40, 40, 80))
    
    # Load button image (same behavior as menu)
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
    # Pre-render main line surfaces to get heights
    line_surfaces = [font.render(line, True, color) for line in lines]
    line_heights = [surf.get_height() for surf in line_surfaces]
    total_height = sum(line_heights) + line_spacing * (len(lines) - 1)
    current_y = button.rect.centery - total_height // 2

    for index, line in enumerate(lines):
      line_surf = line_surfaces[index]
      line_h = line_heights[index]
      center_y = current_y + line_h // 2

      # Stroke pass
      for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
          if dx == 0 and dy == 0:
            continue
          stroke_surf = font.render(line, True, stroke_color)
          stroke_rect = stroke_surf.get_rect(center=(button.rect.centerx + dx, center_y + dy))
          surface.blit(stroke_surf, stroke_rect)

      # Main text pass
      text_rect = line_surf.get_rect(center=(button.rect.centerx, center_y))
      surface.blit(line_surf, text_rect)

      current_y += line_h + line_spacing
  
  def draw(self):
    # Background (clear + cover)
    self.game.screen.fill((0, 0, 0))
    bg_w, bg_h = self.bg.get_width(), self.bg.get_height()
    scr_w, scr_h = self.game.width, self.game.height
    if bg_w > 0 and bg_h > 0:
      scale = max(scr_w / bg_w, scr_h / bg_h)
      scaled_size = (int(bg_w * scale), int(bg_h * scale))
      menu_img = pygame.transform.smoothscale(self.bg, scaled_size)
      offset_x = (scr_w - scaled_size[0]) // 2
      offset_y = (scr_h - scaled_size[1]) // 2
      self.game.screen.blit(menu_img, (offset_x, offset_y))
    else:
      menu_img = pygame.transform.smoothscale(self.bg, (scr_w, scr_h))
      self.game.screen.blit(menu_img, (0, 0))

    # Button sizing: ensure text fits with padding
    text_pvp_w, text_pvp_h = self.button_font.size("PLAYER")
    text_vs_w, text_vs_h = self.button_font.size("VS")
    text_pvai_w, text_pvai_h = self.button_font.size("AI")
    # Since we render 3 lines, take the max width among the three lines for each button
    max_text_w_pvp = max(text_pvp_w, text_vs_w, text_pvp_w)
    max_text_w_pvai = max(text_pvp_w, text_vs_w, text_pvai_w)
    max_text_w = max(max_text_w_pvp, max_text_w_pvai)
    max_text_h = max(text_pvp_h, text_vs_h, text_pvai_h)

    pad_x = 40
    pad_y = 20

    base_width = self.game.width // 6 if self.button_img.get_width() > 0 else 200
    extra_width = 100  # extend a bit for nicer look
    target_width = max(base_width, max_text_w + pad_x * 2) + extra_width

    # Keep aspect ratio from the source image
    src_w = max(self.button_img.get_width(), 1)
    src_h = max(self.button_img.get_height(), 1)
    ratio = src_h / src_w
    target_height = int(target_width * ratio)
    # Ensure height also fits three lines + vertical padding and line spacing
    line_spacing = 6
    total_text_height = max_text_h * 3 + line_spacing * 2
    target_height = max(target_height, total_text_height + pad_y * 2)

    scaled_button_img = pygame.transform.smoothscale(self.button_img, (target_width, target_height))

    # Positions: stack vertically, centered
    x = self.game.width // 2 - target_width // 2
    spacing = 20
    y1 = self.game.height // 2 - target_height - spacing // 2
    y2 = self.game.height // 2 + spacing // 2

    pvp_button = Button(x, y1, scaled_button_img, self.game)
    pvai_button = Button(x, y2, scaled_button_img, self.game)

    # Handle clicks
    if pvp_button.draw():
      self.selected_mode = 'pvp'
      self.option_displaying = False
      return

    if pvai_button.draw():
      self.selected_mode = 'pvai'
      self.option_displaying = False
      return

    # Labels (three lines each)
    self.draw_multiline_with_stroke(self.game.screen, pvp_button, ["PLAYER", "VS", "PLAYER"], self.button_font, (255, 255, 255), (0, 0, 0), line_spacing=6, stroke_width=5)
    self.draw_multiline_with_stroke(self.game.screen, pvai_button, ["PLAYER", "VS", "AI"], self.button_font, (255, 255, 255), (0, 0, 0), line_spacing=6, stroke_width=5)

    pygame.display.flip()
      
  def events(self):
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        self.game.running = False
        self.option_displaying = False

      elif event.type == pygame.VIDEORESIZE:
        self.game.width, self.game.height = event.w, event.h
        self.game.screen = pygame.display.set_mode((self.game.width, self.game.height), pygame.RESIZABLE)

      elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
          # Close only the option menu; keep game running unless explicitly quitting elsewhere
          self.option_displaying = False
  
  
  def display_option_menu(self):
    self.option_displaying = True
    while self.option_displaying and self.game.running:
      self.events()
      self.draw()
      self.game.clock.tick(60)
    