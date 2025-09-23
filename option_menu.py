import pygame
from button import Button
import os

class OptionMenu:
  def __init__(self, game):
    self.game = game

    # selection result
    self.selected_mode = None  # 'pvp' or 'pvai'
    self.selected_squad = None  # 'home' or 'visitor'
    self.phase = 'mode'  # 'mode' -> 'squad' (when pvp selected)

    # Persistent keyboard selection side for squad phase: 'left' or 'right'
    self.selected_side = None
    # P1 ready state (W to set, S to unset)
    self.p1_ready = False

    # P2 controls and ready state (Arrow keys)
    self.selected_side_p2 = None  # 'left' or 'right'
    self.p2_ready = False
    
    # Load background image (only field, no border)
    try:
      self.bg = pygame.image.load(os.path.join("assets", "Field", "Only Field.png")).convert()
    except (pygame.error, FileNotFoundError):
      self.bg = pygame.Surface((self.game.width, self.game.height))
      self.bg.fill((40, 40, 80))
    
    # Load button image
    try:
      self.button_img = pygame.image.load(os.path.join("assets", "menu-button.png")).convert_alpha()
    except (pygame.error, FileNotFoundError):
      self.button_img = pygame.Surface((200, 50))
      self.button_img.fill((100, 100, 100))
    
    # Load preview images for squad selection
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
    
    # Load fonts
    try:
      self.button_font = pygame.font.Font("assets/fonts/LuckiestGuy-Regular.ttf", 50)
    except (pygame.error, FileNotFoundError):
      self.button_font = pygame.font.Font(None, 35)
    try:
      self.badge_font = pygame.font.Font("assets/fonts/LuckiestGuy-Regular.ttf", 28)
    except (pygame.error, FileNotFoundError):
      self.badge_font = pygame.font.Font(None, 22)
      
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

  def draw_text_with_stroke_center(self, text, center, font, color, stroke_color, stroke_width=2):
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=center)
    for dx in range(-stroke_width, stroke_width + 1):
      for dy in range(-stroke_width, stroke_width + 1):
        if dx == 0 and dy == 0:
          continue
        stroke_surf = font.render(text, True, stroke_color)
        stroke_rect = stroke_surf.get_rect(center=(center[0] + dx, center[1] + dy))
        self.game.screen.blit(stroke_surf, stroke_rect)
    self.game.screen.blit(text_surf, text_rect)

  def draw_checkmark(self, center, radius=10):
    # Green circle background
    pygame.draw.circle(self.game.screen, (0, 200, 120), center, radius)
    # White check mark
    arm1_start = (center[0] - radius // 3, center[1])
    arm1_end = (center[0] - 1, center[1] + radius // 3)
    arm2_end = (center[0] + radius // 2, center[1] - radius // 3)
    pygame.draw.line(self.game.screen, (255,255,255), arm1_start, arm1_end, max(2, radius // 4))
    pygame.draw.line(self.game.screen, (255,255,255), arm1_end, arm2_end, max(2, radius // 4))

  def draw_button_feedback(self, button, is_hovered, is_pressed, is_selected=False):
    # Shape-respecting tint using the button image alpha
    if is_pressed:
      overlay = button.image.copy()
      overlay.fill((200, 200, 200, 255), special_flags=pygame.BLEND_RGBA_MULT)
      self.game.screen.blit(overlay, (button.rect.x, button.rect.y))
    elif is_hovered:
      overlay = button.image.copy()
      overlay.fill((40, 40, 40, 0), special_flags=pygame.BLEND_RGBA_ADD)
      self.game.screen.blit(overlay, (button.rect.x, button.rect.y))

    if is_selected:
      pygame.draw.rect(self.game.screen, (0, 200, 120), button.rect, 3, border_radius=10)
  
  def draw_background(self):
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

  def draw_phase_mode(self):
    # Button sizing: ensure text fits with padding
    text_pvp_w, text_pvp_h = self.button_font.size("PLAYER")
    text_vs_w, text_vs_h = self.button_font.size("VS")
    text_pvai_w, text_pvai_h = self.button_font.size("AI")
    max_text_w_pvp = max(text_pvp_w, text_vs_w, text_pvp_w)
    max_text_w_pvai = max(text_pvp_w, text_vs_w, text_pvai_w)
    max_text_w = max(max_text_w_pvp, max_text_w_pvai)
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

    pvp_action = pvp_button.draw()
    pvai_action = pvai_button.draw()

    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()[0] == 1
    self.draw_button_feedback(pvp_button, pvp_button.rect.collidepoint(mouse_pos), mouse_pressed and pvp_button.rect.collidepoint(mouse_pos))
    self.draw_button_feedback(pvai_button, pvai_button.rect.collidepoint(mouse_pos), mouse_pressed and pvai_button.rect.collidepoint(mouse_pos))

    self.draw_multiline_with_stroke(self.game.screen, pvp_button, ["PLAYER", "VS", "PLAYER"], self.button_font, (255, 255, 255), (0, 0, 0), line_spacing=6, stroke_width=5)
    self.draw_multiline_with_stroke(self.game.screen, pvai_button, ["PLAYER", "VS", "AI"], self.button_font, (255, 255, 255), (0, 0, 0), line_spacing=6, stroke_width=5)

    if pvp_action:
      self.selected_mode = 'pvp'
      self.phase = 'squad'
      return

    if pvai_action:
      self.selected_mode = 'pvai'
      self.phase = 'squad'
      return

  def draw_phase_squad(self):
    # Scale preview images to consistent width
    target_width = max(240, self.game.width // 6)
    def scale_keep_ratio(img):
      w, h = img.get_width(), img.get_height()
      scale = target_width / max(w, 1)
      return pygame.transform.smoothscale(img, (int(w * scale), int(h * scale)))

    home_img = scale_keep_ratio(self.home_img_raw)
    visitor_img = scale_keep_ratio(self.visitor_img_raw)

    # Horizontal positions for left/right layout
    gap = 500
    total_width = home_img.get_width() + visitor_img.get_width() + gap
    start_x = max(20, self.game.width // 2 - total_width // 2)
    y = self.game.height // 2 - max(home_img.get_height(), visitor_img.get_height()) // 2

    pvp_home_btn = Button(start_x, y, home_img, self.game)
    pvp_visitor_btn = Button(start_x + home_img.get_width() + gap, y, visitor_img, self.game)

    act_home = pvp_home_btn.draw()
    act_visitor = pvp_visitor_btn.draw()

    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()[0] == 1

    # Pressed states combine mouse press and persistent keyboard selections from P1 and P2
    left_pressed = (mouse_pressed and pvp_home_btn.rect.collidepoint(mouse_pos)) or (self.selected_side == 'left') or (self.selected_side_p2 == 'left')
    right_pressed = (mouse_pressed and pvp_visitor_btn.rect.collidepoint(mouse_pos)) or (self.selected_side == 'right') or (self.selected_side_p2 == 'right')

    self.draw_button_feedback(pvp_home_btn, pvp_home_btn.rect.collidepoint(mouse_pos), left_pressed)
    self.draw_button_feedback(pvp_visitor_btn, pvp_visitor_btn.rect.collidepoint(mouse_pos), right_pressed)

    # P1 badge and optional checkmark
    if self.selected_side == 'left':
      badge_pos = (pvp_home_btn.rect.centerx, pvp_home_btn.rect.top - 16)
      self.draw_text_with_stroke_center("P1", badge_pos, self.badge_font, (255,255,255), (0,0,0), stroke_width=3)
      if self.p1_ready:
        self.draw_checkmark((badge_pos[0] + 24, badge_pos[1]), radius=10)
    elif self.selected_side == 'right':
      badge_pos = (pvp_visitor_btn.rect.centerx, pvp_visitor_btn.rect.top - 16)
      self.draw_text_with_stroke_center("P1", badge_pos, self.badge_font, (255,255,255), (0,0,0), stroke_width=3)
      if self.p1_ready:
        self.draw_checkmark((badge_pos[0] + 24, badge_pos[1]), radius=10)

    # P2 badge and optional checkmark (offset higher to avoid overlap) - only show in PvP mode
    if self.selected_mode == 'pvp':
      if self.selected_side_p2 == 'left':
        badge_pos2 = (pvp_home_btn.rect.centerx, pvp_home_btn.rect.top - 46)
        self.draw_text_with_stroke_center("P2", badge_pos2, self.badge_font, (255,255,255), (0,0,0), stroke_width=3)
        if self.p2_ready:
          self.draw_checkmark((badge_pos2[0] + 24, badge_pos2[1]), radius=10)
      elif self.selected_side_p2 == 'right':
        badge_pos2 = (pvp_visitor_btn.rect.centerx, pvp_visitor_btn.rect.top - 46)
        self.draw_text_with_stroke_center("P2", badge_pos2, self.badge_font, (255,255,255), (0,0,0), stroke_width=3)
        if self.p2_ready:
          self.draw_checkmark((badge_pos2[0] + 24, badge_pos2[1]), radius=10)

    # Auto-continue when both players are ready and have selected sides (PvP mode)
    if self.selected_mode == 'pvp' and self.p1_ready and self.p2_ready and (self.selected_side is not None) and (self.selected_side_p2 is not None):
      self.option_displaying = False
      return
    
    # Auto-continue when P1 is ready and has selected side (PvAI mode)
    if self.selected_mode == 'pvai' and self.p1_ready and (self.selected_side is not None):
      self.option_displaying = False
      return

    # Labels under each image button
    label_offset = 12
    self.draw_text_with_stroke_center("Squad Home Team", (pvp_home_btn.rect.centerx, pvp_home_btn.rect.bottom + label_offset + 10), self.button_font, (255,255,255), (0,0,0), stroke_width=4)
    self.draw_text_with_stroke_center("Squad Visitor Team", (pvp_visitor_btn.rect.centerx, pvp_visitor_btn.rect.bottom + label_offset + 10), self.button_font, (255,255,255), (0,0,0), stroke_width=4)

    if act_home:
      self.selected_squad = 'home'
      self.option_displaying = False
      return

    if act_visitor:
      self.selected_squad = 'visitor'
      self.option_displaying = False
      return
  
  def draw(self):
    self.draw_background()
    if self.phase == 'mode':
      self.draw_phase_mode()
    elif self.phase == 'squad':
      self.draw_phase_squad()
    
    pygame.display.flip()
      
  def events(self):
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        self.game.running = False

      elif event.type == pygame.VIDEORESIZE:
        self.game.width, self.game.height = event.w, event.h
        self.game.screen = pygame.display.set_mode((self.game.width, self.game.height), pygame.RESIZABLE)

      elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
          # Close only the option menu; keep game running unless explicitly quitting elsewhere
          if self.phase == 'squad':
            # go back to mode selection
            self.phase = 'mode'
          else:
            self.game.running = False
        elif self.phase == 'squad':
          # P1 controls (A/D to select, W ready, S unready). Lock switching while ready
          if not self.p1_ready and event.key == pygame.K_a:
            # Check if P2 has already claimed 'left' side (only in PvP mode)
            if self.selected_mode == 'pvp' and (self.p2_ready and self.selected_side_p2 == 'left'):
              pass  # Block selection
            else:
              self.selected_side = 'left'
          elif not self.p1_ready and event.key == pygame.K_d:
            # Check if P2 has already claimed 'right' side (only in PvP mode)
            if self.selected_mode == 'pvp' and (self.p2_ready and self.selected_side_p2 == 'right'):
              pass  # Block selection
            else:
              self.selected_side = 'right'
          elif event.key == pygame.K_w:
            self.p1_ready = True
          elif event.key == pygame.K_s:
            self.p1_ready = False
          
          # P2 controls (Arrows) - only active in PvP mode
          elif self.selected_mode == 'pvp':
            if not self.p2_ready and event.key == pygame.K_LEFT:
              # Check if P1 has already claimed 'left' side
              if not (self.p1_ready and self.selected_side == 'left'):
                self.selected_side_p2 = 'left'
            elif not self.p2_ready and event.key == pygame.K_RIGHT:
              # Check if P1 has already claimed 'right' side
              if not (self.p1_ready and self.selected_side == 'right'):
                self.selected_side_p2 = 'right'
            elif event.key == pygame.K_UP:
              self.p2_ready = True
            elif event.key == pygame.K_DOWN:
              self.p2_ready = False
