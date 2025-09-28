import pygame, os
from button import Button

class OptionMenu:
  def __init__(self, screen, width, height):
    self.screen = screen
    self.width = width
    self.height = height

    # selection state
    self.selected_mode = None  # 'pvp' or 'pvai'
    self.phase = 'mode'
    self.option_completed = False
    self.selected_side = None
    self.selected_side_p2 = None

    # Load background image
    try:
      self.bg = pygame.image.load(os.path.join("assets", "Field", "Only Field.png")).convert()
      self.scaled_bg = pygame.transform.smoothscale(self.bg, (self.width, self.height))
    except (pygame.error, FileNotFoundError):
      self.bg = pygame.Surface((self.width, self.height))
      self.bg.fill((40, 40, 80))
      self.scaled_bg = self.bg

    # Load button image
    try:
      self.button_img = pygame.image.load(os.path.join("assets", "menu-button.png")).convert_alpha()
    except (pygame.error, FileNotFoundError):
      self.button_img = pygame.Surface((200, 50))
      self.button_img.fill((100, 100, 100))

    # Load squad preview images
    try:
      self.home_img_raw = pygame.image.load(os.path.join("assets", "Preview", "10.png")).convert_alpha()
    except (pygame.error, FileNotFoundError):
      self.home_img_raw = pygame.Surface((200, 200), pygame.SRCALPHA)
      self.home_img_raw.fill((180, 180, 180, 255))
    try:
      self.visitor_img_raw = pygame.image.load(os.path.join("assets", "Preview", "14.png")).convert_alpha()
    except (pygame.error, FileNotFoundError):
      self.visitor_img_raw = pygame.Surface((200, 200), pygame.SRCALPHA)
      self.visitor_img_raw.fill((160, 160, 160, 255))

    # Load fonts dynamically
    self._load_fonts()

    # Pre-render static text surfaces
    self.text_cache = {}
    self.cache_text("PVP", ["PLAYER", "VS", "PLAYER"])
    self.cache_text("PVAI", ["PLAYER", "VS", "AI"])

    # Pre-scaled squad images
    self.home_img = None
    self.visitor_img = None
    self.scale_squads()

  # -----------------------------
  # Font handling
  # -----------------------------
  def _load_fonts(self):
    """Reload fonts based on window size."""
    button_font_size = max(22, int(self.height * 0.06))  # ~6% of screen height
    badge_font_size = max(14, int(self.height * 0.035))  # ~3.5% of screen height
    try:
      self.button_font = pygame.font.Font("assets/fonts/LuckiestGuy-Regular.ttf", button_font_size)
    except (pygame.error, FileNotFoundError):
      self.button_font = pygame.font.Font(None, button_font_size)

    try:
      self.badge_font = pygame.font.Font("assets/fonts/LuckiestGuy-Regular.ttf", badge_font_size)
    except (pygame.error, FileNotFoundError):
      self.badge_font = pygame.font.Font(None, badge_font_size)

  # -----------------------------
  # Utilities
  # -----------------------------
  def resize(self, width, height, screen):
    """Called when window is resized"""
    self.width = width
    self.height = height
    self.screen = screen
    self.scaled_bg = pygame.transform.smoothscale(self.bg, (self.width, self.height))
    self.scale_squads()
    self._load_fonts()   # reload fonts

  def cache_text(self, key, lines, stroke_color=(0,0,0), stroke_width=5):
    """Pre-render a multi-line text with stroke and cache it."""
    line_surfaces = []
    for line in lines:
      surf = self.button_font.render(line, True, (255,255,255))
      line_surfaces.append(surf)
    self.text_cache[key] = (lines, line_surfaces, stroke_color, stroke_width)

  def render_cached_text(self, surface, button, key):
    lines, line_surfaces, stroke_color, stroke_width = self.text_cache[key]
    line_heights = [surf.get_height() for surf in line_surfaces]
    total_height = sum(line_heights) + 6 * (len(lines) - 1)
    current_y = button.rect.centery - total_height // 2

    for i, line in enumerate(lines):
      surf = line_surfaces[i]
      line_h = line_heights[i]
      center_y = current_y + line_h // 2

      # stroke
      for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
          if dx == 0 and dy == 0:
            continue
          stroke_surf = self.button_font.render(line, True, stroke_color)
          stroke_rect = stroke_surf.get_rect(center=(button.rect.centerx + dx, center_y + dy))
          surface.blit(stroke_surf, stroke_rect)

      rect = surf.get_rect(center=(button.rect.centerx, center_y))
      surface.blit(surf, rect)
      current_y += line_h + 6

  def draw_text_with_stroke_center(self, text, center, font, color, stroke_color, stroke_width=2):
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=center)
    for dx in range(-stroke_width, stroke_width + 1):
      for dy in range(-stroke_width, stroke_width + 1):
        if dx == 0 and dy == 0:
          continue
        stroke_surf = font.render(text, True, stroke_color)
        stroke_rect = stroke_surf.get_rect(center=(center[0] + dx, center[1] + dy))
        self.screen.blit(stroke_surf, stroke_rect)
    self.screen.blit(text_surf, text_rect)

  def scale_squads(self):
    """Pre-scale squad preview images based on current window size."""
    target_width = max(240, self.width // 6)
    def scale(img):
      w, h = img.get_width(), img.get_height()
      scale = target_width / max(w, 1)
      return pygame.transform.smoothscale(img, (int(w * scale), int(h * scale)))
    self.home_img = scale(self.home_img_raw)
    self.visitor_img = scale(self.visitor_img_raw)

  # -----------------------------
  # Drawing
  # -----------------------------
  def draw_background(self):
    self.screen.blit(self.scaled_bg, (0,0))

  def draw_phase_mode(self):
    base_width = self.width // 6 if self.button_img.get_width() > 0 else 200
    target_width = base_width + 100

    src_w = max(self.button_img.get_width(), 1)
    src_h = max(self.button_img.get_height(), 1)
    ratio = src_h / src_w
    target_height = int(target_width * ratio)

    scaled_button_img = pygame.transform.smoothscale(self.button_img, (target_width, target_height))

    # positions
    x = self.width // 2 - target_width // 2
    spacing = 20
    y1 = self.height // 2 - target_height - spacing // 2
    y2 = self.height // 2 + spacing // 2

    pvp_button = Button(x, y1, scaled_button_img, self.screen)
    pvai_button = Button(x, y2, scaled_button_img, self.screen)

    if pvp_button.draw():
      self.selected_mode = 'pvp'
      self.phase = 'squad'
      self.scale_squads()
      return

    if pvai_button.draw():
      self.selected_mode = 'pvai'
      self.phase = 'squad'
      self.scale_squads()
      return

    self.render_cached_text(self.screen, pvp_button, "PVP")
    self.render_cached_text(self.screen, pvai_button, "PVAI")

  def draw_phase_squad(self):
    gap = 500
    total_width = self.home_img.get_width() + self.visitor_img.get_width() + gap
    start_x = max(20, self.width // 2 - total_width // 2)
    y = self.height // 2 - max(self.home_img.get_height(), self.visitor_img.get_height()) // 2

    # Always draw both buttons
    pvp_home_btn = Button(start_x, y, self.home_img, self.screen)
    pvp_visitor_btn = Button(start_x + self.home_img.get_width() + gap, y, self.visitor_img, self.screen)

    # Selection logic
    if not (self.selected_side == 'left' or self.selected_side_p2 == 'left'):
      if pvp_home_btn.draw():
        if self.selected_side is None:
          self.selected_side = 'left'
        elif self.selected_mode == 'pvp' and self.selected_side_p2 is None:
          self.selected_side_p2 = 'left'
    else:
      pvp_home_btn.draw()

    if not (self.selected_side == 'right' or self.selected_side_p2 == 'right'):
      if pvp_visitor_btn.draw():
        if self.selected_side is None:
          self.selected_side = 'right'
        elif self.selected_mode == 'pvp' and self.selected_side_p2 is None:
          self.selected_side_p2 = 'right'
    else:
      pvp_visitor_btn.draw()

    # Badges
    if self.selected_side == 'left':
      self.draw_text_with_stroke_center("P1", (pvp_home_btn.rect.centerx, pvp_home_btn.rect.top - 26), self.badge_font, (255,255,255), (0,0,0), stroke_width=3)
    elif self.selected_side == 'right':
      self.draw_text_with_stroke_center("P1", (pvp_visitor_btn.rect.centerx, pvp_visitor_btn.rect.top - 26), self.badge_font, (255,255,255), (0,0,0), stroke_width=3)

    if self.selected_mode == 'pvp':
      if self.selected_side_p2 == 'left':
        self.draw_text_with_stroke_center("P2", (pvp_home_btn.rect.centerx, pvp_home_btn.rect.top - 26), self.badge_font, (255,255,255), (0,0,0), stroke_width=3)
      elif self.selected_side_p2 == 'right':
        self.draw_text_with_stroke_center("P2", (pvp_visitor_btn.rect.centerx, pvp_visitor_btn.rect.top - 26), self.badge_font, (255,255,255), (0,0,0), stroke_width=3)

    # Continue button
    ready = False
    if self.selected_mode == 'pvp' and self.selected_side and self.selected_side_p2:
      if self.selected_side != self.selected_side_p2:
        ready = True
    elif self.selected_mode == 'pvai' and self.selected_side:
      ready = True

    if ready:
      cont_width = self.width // 5
      cont_height = int(self.button_img.get_height() * (cont_width / self.button_img.get_width()))
      cont_x = self.width // 2 - cont_width // 2
      cont_y = self.height - cont_height - 60
      cont_surface = pygame.transform.smoothscale(self.button_img, (cont_width, cont_height))
      cont_button = Button(cont_x, cont_y, cont_surface, self.screen)
      if cont_button.draw():
        self.option_completed = True
      self.draw_text_with_stroke_center("CONTINUE", cont_button.rect.center, self.button_font, (255,255,255), (0,0,0), stroke_width=5)

    # Back button
    back_width = self.width // 7
    back_height = int(self.button_img.get_height() * (back_width / self.button_img.get_width()))
    back_img = pygame.transform.smoothscale(self.button_img, (back_width, back_height))
    back_x = 40
    back_y = self.height - back_height - 40
    back_button = Button(back_x, back_y, back_img, self.screen)

    if back_button.draw():
      self.selected_mode = None
      self.phase = 'mode'
      self.option_completed = False
      self.selected_side = None
      self.selected_side_p2 = None

    self.draw_text_with_stroke_center("BACK", back_button.rect.center, self.button_font, (255,255,255), (0,0,0), stroke_width=4)

  def draw(self):
    self.draw_background()
    if self.phase == 'mode':
      self.draw_phase_mode()
    elif self.phase == 'squad':
      self.draw_phase_squad()

  def events(self, events):
    for event in events:
      if event.type == pygame.QUIT:
        pass
      elif event.type == pygame.VIDEORESIZE:
        self.width, self.height = event.w, event.h
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        self.bg_scaled = pygame.transform.smoothscale(self.bg, (self.width, self.height))
        self.scale_squads()
      elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        if self.phase == 'squad':
          self.phase = 'mode'
          self.selected_side = None
          self.selected_side_p2 = None
        else:
          self.option_completed = True

  def reset(self):
    self.phase = 'mode'
    self.option_completed = False
    self.selected_side = None
    self.selected_side_p2 = None
    self.scale_squads()
