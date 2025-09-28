import pygame, os
from ball import Ball
from button import Button
from resume import PauseMenu

WIN_SCORE = 3

class PvPGameplay:
  def __init__(self, screen, width, height, side_p1, side_p2, sounds):
    self.screen = screen
    self.width = width
    self.height = height
    self.side_p1 = side_p1
    self.side_p2 = side_p2
    self.sounds = sounds

    self.paused = False
    self.music_on = pygame.mixer.music.get_volume() > 0
    self.show_bounds = True
    
    bg_path = os.path.join("assets", "Field", "Only Field.png")
    try:
      self.bg_img = pygame.image.load(bg_path).convert()
    except (pygame.error, FileNotFoundError):
      self.bg_img = pygame.Surface((self.width, self.height)); self.bg_img.fill((0, 100, 0))
    self.scaled_bg = pygame.transform.smoothscale(self.bg_img, (self.width, self.height))

    self._load_ui_assets()
    
    self.ui_margin_x = 40
    self.pause_button = Button(self.ui_margin_x, 20, self.pause_btn_img, self.screen)
    self.sound_button = Button(self.ui_margin_x + 50 + 10, 20, self.vol_on_img if self.music_on else self.vol_off_img, self.screen)
    
    self.pause_menu = PauseMenu(screen, width, height)
    
    self.player1_img = self.load_player(side_p1, (0,0,255))
    self.player2_img = self.load_player(side_p2, (255,0,0))
    self.p1 = self.player1_img.get_rect(center=(200, self.height // 2))
    self.p2 = self.player2_img.get_rect(center=(self.width - 200, self.height // 2))
    self.player_size = self.p1.width
    self.ball = Ball(self.width, self.height, self.player_size, self.width // 2, self.height // 2)

    self.score = [0,0]
    self.goal_text = ""
    self.goal_text_timer = 0
    self.winner = None
    self.back_to_menu = False
    
    self._create_goals(); self._create_play_area()

    try:
      self.button_img = pygame.image.load(os.path.join("assets", "menu-button.png")).convert_alpha()
      self.button_font = pygame.font.Font("assets/fonts/LuckiestGuy-Regular.ttf", 36)
    except (pygame.error, FileNotFoundError):
      self.button_img = pygame.Surface((200, 50)); self.button_img.fill((100, 100, 100))
      self.button_font = pygame.font.Font(None, 28)
    self.back_button = None

  # ------------------- FONT SCALING -------------------
  def get_scaled_font_size(self, base_size):
    """Scale font size relative to a 1200x800 base resolution."""
    scale_factor = min(self.width / 1200, self.height / 800)
    return max(16, int(base_size * scale_factor))
  # ----------------------------------------------------

  def _load_ui_assets(self):
    try:
        self.pause_btn_img = pygame.transform.smoothscale(pygame.image.load(os.path.join("assets", "pause", "pause-button.png")).convert_alpha(), (50, 50))
        self.vol_on_img = pygame.transform.smoothscale(pygame.image.load(os.path.join("assets", "pause", "volumn-button-on.png")).convert_alpha(), (50, 50))
        self.vol_off_img = pygame.transform.smoothscale(pygame.image.load(os.path.join("assets", "pause", "volumn-button-off.png")).convert_alpha(), (50, 50))
    except (pygame.error, FileNotFoundError):
        self.pause_btn_img = pygame.Surface((50, 50)); self.pause_btn_img.fill((200,200,200))
        self.vol_on_img = pygame.Surface((50, 50)); self.vol_on_img.fill((0,255,0))
        self.vol_off_img = pygame.Surface((50, 50)); self.vol_off_img.fill((255,0,0))

  def toggle_music(self):
    self.music_on = not self.music_on
    pygame.mixer.music.set_volume(0.5 if self.music_on else 0.0)
    self.sound_button.image = self.vol_on_img if self.music_on else self.vol_off_img

  def handle_events(self, events):
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p and not self.winner:
                self.paused = not self.paused
            if event.key == pygame.K_m and not self.winner:
                self.toggle_music()
            if event.key == pygame.K_b:
                self.show_bounds = not self.show_bounds

  def update(self):
    if self.winner is not None or self.paused:
      return
    self.handle_input()
    self.ball.move(self.play_area, self.goal_left, self.goal_right)
    if self.ball.kick(self.p1, 0): self.sounds["kick"].play()
    if self.ball.kick(self.p2, 1): self.sounds["kick"].play()
    scorer, conceding_team, own_goal = None, None, False
    if self.ball.rect.colliderect(self.goal_left):
      conceding_team, scorer = 0, 1
    elif self.ball.rect.colliderect(self.goal_right):
      conceding_team, scorer = 1, 0
    if scorer is not None:
      self.sounds["goal"].play()
      own_goal = (self.ball.last_touch == conceding_team)
      self.score[scorer] += 1
      self.goal_text = "OWN GOAL!" if own_goal else "GOAL!"
      self.goal_text_timer = 120
      self.reset_positions()
      if self.score[0] >= WIN_SCORE or self.score[1] >= WIN_SCORE:
        self.winner = 0 if self.score[0] >= WIN_SCORE else 1
        self.ball.vx = self.ball.vy = 0.0
        self.back_button = None
        return

  def draw(self):
    self.screen.blit(self.scaled_bg, (0, 0))
    
    if self.show_bounds:
        pygame.draw.rect(self.screen, (255,255,0), self.main_rect, 3)
        pygame.draw.rect(self.screen, (255,255,0), self.goal_left, 3)
        pygame.draw.rect(self.screen, (255,255,0), self.goal_right, 3)

    self.screen.blit(self.player1_img, self.p1)
    self.screen.blit(self.player2_img, self.p2)
    self.ball.draw(self.screen)

    # Scores
    score_size = self.get_scaled_font_size(60)
    p1_color = (0,0,255) if self.side_p1 == "left" else (255,0,0)
    p2_color = (0,0,255) if self.side_p2 == "left" else (255,0,0)
    p1_score_surf, p1_rect = self.draw_text(str(self.score[0]), score_size, p1_color, self.width // 4, 50)
    p2_score_surf, p2_rect = self.draw_text(str(self.score[1]), score_size, p2_color, 3 * self.width // 4, 50)
    self.screen.blit(p1_score_surf, p1_rect)
    self.screen.blit(p2_score_surf, p2_rect)

    # Goal text
    if self.goal_text_timer > 0 and not self.paused:
      goal_size = self.get_scaled_font_size(72)
      txt, rect = self.draw_text(self.goal_text, goal_size, (255, 255, 0), self.width // 2, self.height // 2)
      self.screen.blit(txt, rect)
      self.goal_text_timer -= 1

    # Pause & Sound buttons
    if self.pause_button.draw() and not self.winner: self.paused = True
    if self.sound_button.draw() and not self.winner: self.toggle_music()

    # Pause menu
    if self.paused:
      action = self.pause_menu.draw()
      if action == 'resume': self.paused = False
      elif action == 'quit': self.back_to_menu = True

    # Winner screen
    elif self.winner is not None:
      winner_size = self.get_scaled_font_size(84)
      winner_txt, winner_rect = self.draw_text(f"P{self.winner + 1} WINS!", winner_size, (255, 215, 0), self.width // 2, self.height // 2 - 80)
      self.screen.blit(winner_txt, winner_rect)

      self.ensure_back_button()
      if self.back_button:
        if self.back_button.draw(): self.back_to_menu = True

        btn_font_size = self.get_scaled_font_size(36)
        try:
          btn_font = pygame.font.Font("assets/fonts/LuckiestGuy-Regular.ttf", btn_font_size)
        except (pygame.error, FileNotFoundError):
          btn_font = pygame.font.Font(None, btn_font_size)

        self.draw_text_with_stroke(self.screen, self.back_button, "BACK TO MENU", btn_font, (255,255,255), (0,0,0), stroke_width=4)
        
  def resize(self, width, height, screen):
    self.width, self.height, self.screen = width, height, screen
    self.scaled_bg = pygame.transform.smoothscale(self.bg_img, (self.width, self.height))
    self._create_goals(); self._create_play_area()
    self.pause_menu.resize(width, height, screen)
    self.pause_button = Button(self.ui_margin_x, 20, self.pause_btn_img, self.screen)
    self.sound_button = Button(self.ui_margin_x + 50 + 10, 20, self.vol_on_img if self.music_on else self.vol_off_img, self.screen)
    self.player1_img = self.load_player(self.side_p1, (0,0,255))
    self.player2_img = self.load_player(self.side_p2, (255,0,0))
    self.p1 = self.player1_img.get_rect(center=self.p1.center)
    self.p2 = self.player2_img.get_rect(center=self.p2.center)
    self.ball.width, self.ball.height = width, height
    self.back_button = None

  def load_player(self, side, tint_color):
    if side == "left": path = os.path.join("assets", "Romanos FC (Home Team)", "2.png")
    else: path = os.path.join("assets", "Saint Bari (Visitor Team)", "2.png")
    try: img = pygame.image.load(path).convert_alpha()
    except: img = pygame.Surface((80,80), pygame.SRCALPHA); img.fill(tint_color)
    target_w = max(80, self.width // 16); ratio = target_w / max(1, img.get_width())
    return pygame.transform.smoothscale(img, (int(img.get_width()*ratio), int(img.get_height()*ratio)))

  def _create_play_area(self):
    margin_x = self.width // 9.5; margin_y = self.height // 10
    self.main_rect = pygame.Rect(margin_x, margin_y, self.width - 2*margin_x, self.height - 2*margin_y)
    self.play_area = [self.main_rect, self.goal_left, self.goal_right]

  def _create_goals(self):
    goal_height = max(120, self.height // 5); goal_thickness = max(32, self.width // 9)
    self.goal_left = pygame.Rect(0, self.height//2 - goal_height//2, goal_thickness, goal_height)
    self.goal_right = pygame.Rect(self.width-goal_thickness, self.height//2 - goal_height//2, goal_thickness, goal_height)

  def reset_positions(self):
    self.ball.x, self.ball.y = self.width // 2, self.height // 2
    self.ball.vx, self.ball.vy = 0.0, 0.0; self.ball.last_touch = None
    self.ball.rect.center = (int(self.ball.x), int(self.ball.y))
    self.p1.center = (200, self.height // 2)
    self.p2.center = (self.width - 200, self.height // 2)

  def handle_input(self):
    keys = pygame.key.get_pressed(); speed = 6
    if keys[pygame.K_w]: self.p1.y -= speed
    if keys[pygame.K_s]: self.p1.y += speed
    if keys[pygame.K_a]: self.p1.x -= speed
    if keys[pygame.K_d]: self.p1.x += speed
    if keys[pygame.K_UP]: self.p2.y -= speed
    if keys[pygame.K_DOWN]: self.p2.y += speed
    if keys[pygame.K_LEFT]: self.p2.x -= speed
    if keys[pygame.K_RIGHT]: self.p2.x += speed
    self.p1.clamp_ip(self.screen.get_rect()); self.p2.clamp_ip(self.screen.get_rect())

  def draw_text_with_stroke(self, surface, button, text, font, color, stroke_color, stroke_width=2):
    text_surf = font.render(text, True, color); text_rect = text_surf.get_rect(center=button.rect.center)
    for dx in range(-stroke_width, stroke_width + 1):
      for dy in range(-stroke_width, stroke_width + 1):
        if dx == 0 and dy == 0: continue
        stroke_surf = font.render(text, True, stroke_color)
        stroke_rect = stroke_surf.get_rect(center=(button.rect.centerx + dx, button.rect.centery + dy))
        surface.blit(stroke_surf, stroke_rect)
    surface.blit(text_surf, text_rect)

  def ensure_back_button(self):
    if self.back_button is not None: return
    btn_w = self.width // 6; src_w = max(self.button_img.get_width(), 1); src_h = max(self.button_img.get_height(), 1)
    btn_h = int(src_h * (btn_w / src_w)); scaled_btn = pygame.transform.smoothscale(self.button_img, (btn_w, btn_h))
    btn_x = self.width // 2 - btn_w // 2; btn_y = self.height // 2 + 40
    self.back_button = Button(btn_x, btn_y, scaled_btn, self.screen)

  def draw_text(self, text, size, color, x, y):
    try: font = pygame.font.Font("assets/fonts/LuckiestGuy-Regular.ttf", size)
    except (pygame.error, FileNotFoundError): font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    return text_surface, text_rect
