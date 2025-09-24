import pygame, os
from ball import Ball
from button import Button

WIN_SCORE = 3

class PvPGameplay:
  def __init__(self, screen, width, height, side_p1, side_p2):
    self.screen = screen
    self.width = width
    self.height = height
    self.side_p1 = side_p1
    self.side_p2 = side_p2

    # Background
    bg_path = os.path.join("assets", "Field", "Only Field.png")
    try:
      self.bg_img = pygame.image.load(bg_path).convert()
    except (pygame.error, FileNotFoundError):
      self.bg_img = pygame.Surface((self.width, self.height))
      self.bg_img.fill((0, 100, 0))
    self.scaled_bg = pygame.transform.smoothscale(self.bg_img, (self.width, self.height))

    # Load players
    self.player1_img = self.load_player(side_p1, (0,0,255))
    self.player2_img = self.load_player(side_p2, (255,0,0))

    # Rects
    self.p1 = self.player1_img.get_rect(center=(200, self.height // 2))
    self.p2 = self.player2_img.get_rect(center=(self.width - 200, self.height // 2))
    self.player_size = self.p1.width

    # Ball
    self.ball = Ball(self.width, self.height, self.player_size, self.width // 2, self.height // 2)

    # Score etc
    self.score = [0,0]
    self.goal_text = ""
    self.goal_text_timer = 0
    self.last_scorer = None
    self.last_goal_own = False
    self.winner = None
    self.win_timer = 0
    self.back_to_menu = False

    self._create_goals()
    self.running = True
    self.playing = True

    # Button asset + font (for winner/back button)
    try:
      self.button_img = pygame.image.load(os.path.join("assets", "menu-button.png")).convert_alpha()
    except (pygame.error, FileNotFoundError):
      self.button_img = pygame.Surface((200, 50))
      self.button_img.fill((100, 100, 100))

    try:
      self.button_font = pygame.font.Font("assets/fonts/LuckiestGuy-Regular.ttf", 36)
    except (pygame.error, FileNotFoundError):
      self.button_font = pygame.font.Font(None, 28)

    # We'll lazy-create the Button object (so it uses current scaled size)
    self.back_button = None

  # -------- helpers --------
  def load_player(self, side, tint_color):
    if side == "left":
      path = os.path.join("assets", "Romanos FC (Home Team)", "2.png")
    else:
      path = os.path.join("assets", "Saint Bari (Visitor Team)", "2.png")
    try:
      img = pygame.image.load(path).convert_alpha()
    except:
      img = pygame.Surface((80,80), pygame.SRCALPHA)
      img.fill(tint_color)

    target_w = max(80, self.width // 16)
    ratio = target_w / max(1, img.get_width())
    img = pygame.transform.smoothscale(img, (int(img.get_width()*ratio), int(img.get_height()*ratio)))
    return img

  def _create_goals(self):
    goal_height = max(120, self.height // 5)
    goal_thickness = max(32, self.width // 10)
    self.goal_left = pygame.Rect(0, self.height//2 - goal_height//2, goal_thickness, goal_height)
    self.goal_right = pygame.Rect(self.width-goal_thickness, self.height//2 - goal_height//2, goal_thickness, goal_height)

  def reset_ball(self):
    # always center the ball
    self.ball.x, self.ball.y = self.width // 2, self.height // 2
    self.ball.vx, self.ball.vy = 0.0, 0.0
    # if your Ball class has last_touch, clear it
    try:
      self.ball.last_touch = None
    except AttributeError:
      pass
    self.ball.rect.center = (int(self.ball.x), int(self.ball.y))

  # ----- gameplay -----
  def handle_input(self):
    keys = pygame.key.get_pressed()
    speed = 6
    if keys[pygame.K_w]: self.p1.y -= speed
    if keys[pygame.K_s]: self.p1.y += speed
    if keys[pygame.K_a]: self.p1.x -= speed
    if keys[pygame.K_d]: self.p1.x += speed
    if keys[pygame.K_UP]: self.p2.y -= speed
    if keys[pygame.K_DOWN]: self.p2.y += speed
    if keys[pygame.K_LEFT]: self.p2.x -= speed
    if keys[pygame.K_RIGHT]: self.p2.x += speed
    self.p1.clamp_ip(self.screen.get_rect())
    self.p2.clamp_ip(self.screen.get_rect())

  def update(self):
    # while winner screen is up we don't update gameplay
    if self.winner is not None:
      # nothing else here — click detection is done when drawing the button
      return

    self.handle_input()
    self.ball.move()

    # Ball kick calls should match your Ball signature (this code assumes ball.kick(rect, player_id))
    try:
      self.ball.kick(self.p1, 0)
      self.ball.kick(self.p2, 1)
    except TypeError:
      # fallback if Ball.kick doesn't accept player id
      self.ball.kick(self.p1)
      self.ball.kick(self.p2)

    # goal detection
    scorer = None
    conceding_team = None
    own_goal = False

    if self.ball.rect.colliderect(self.goal_left):
      conceding_team = 0
      scorer = 1
    elif self.ball.rect.colliderect(self.goal_right):
      conceding_team = 1
      scorer = 0

    if scorer is not None:
      own_goal = (hasattr(self.ball, "last_touch") and self.ball.last_touch == conceding_team)
      self.score[scorer] += 1
      self.last_scorer = scorer
      self.last_goal_own = own_goal
      self.goal_text = "OWN GOAL!" if own_goal else "GOAL!"
      self.goal_text_timer = 120
      self.reset_ball()

      if self.score[0] >= WIN_SCORE or self.score[1] >= WIN_SCORE:
        self.winner = 0 if self.score[0] >= WIN_SCORE else 1
        self.ball.vx = self.ball.vy = 0.0
        # prepare button next draw
        self.back_button = None
        return

  # ----- drawing helpers -----
  def draw_text_with_stroke(self, surface, button, text, font, color, stroke_color, stroke_width=2):
    # Draw stroked text centered on the button rect
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

  def ensure_back_button(self):
    """Create / recreate the back button scaled to current window."""
    if self.back_button is not None:
      return
    btn_w = self.width // 6
    src_w = max(self.button_img.get_width(), 1)
    src_h = max(self.button_img.get_height(), 1)
    btn_h = int(src_h * (btn_w / src_w))
    scaled_btn = pygame.transform.smoothscale(self.button_img, (btn_w, btn_h))
    btn_x = self.width // 2 - btn_w // 2
    btn_y = self.height // 2 + 40
    self.back_button = Button(btn_x, btn_y, scaled_btn, self.screen)

  # ----- drawing -----
  def draw_text(self, text, size, color, x, y):
    try:
      font = pygame.font.Font("assets/fonts/LuckiestGuy-Regular.ttf", size)
    except (pygame.error, FileNotFoundError):
      font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    return text_surface, text_rect

  def draw(self):
    # background and players/ball
    self.screen.blit(self.scaled_bg, (0, 0))

    # show goal rects (debug/visibility)
    pygame.draw.rect(self.screen, (0, 0, 255), self.goal_left, 3)
    pygame.draw.rect(self.screen, (255, 0, 0), self.goal_right, 3)

    self.screen.blit(self.player1_img, self.p1)
    self.screen.blit(self.player2_img, self.p2)
    self.ball.draw(self.screen)

    # score colors depend on side choice
    p1_color = (0,0,255) if self.side_p1 == "left" else (255,0,0)
    p2_color = (0,0,255) if self.side_p2 == "left" else (255,0,0)

    p1_score_surf, p1_rect = self.draw_text(str(self.score[0]), 60, p1_color, self.width // 4, 50)
    p2_score_surf, p2_rect = self.draw_text(str(self.score[1]), 60, p2_color, 3 * self.width // 4, 50)
    self.screen.blit(p1_score_surf, p1_rect)
    self.screen.blit(p2_score_surf, p2_rect)

    # temporary goal text
    if self.goal_text_timer > 0:
      txt, rect = self.draw_text(self.goal_text, 72, (255, 255, 0), self.width // 2, self.height // 2)
      self.screen.blit(txt, rect)
      self.goal_text_timer -= 1

    # winner screen + back button
    if self.winner is not None:
      winner_txt, winner_rect = self.draw_text(f"P{self.winner + 1} WINS!", 84, (255, 215, 0), self.width // 2, self.height // 2 - 80)
      self.screen.blit(winner_txt, winner_rect)

      # create scaled button if needed
      self.ensure_back_button()

      # draw button and stroke text on it (like Menu.draw)
      if self.back_button:
        clicked = self.back_button.draw()
        # label text on button (stroke)
        self.draw_text_with_stroke(self.screen, self.back_button, "BACK TO MENU", self.button_font, (255,255,255), (0,0,0), stroke_width=4)
        if clicked:
          self.back_to_menu = True

  def resize(self, width, height, screen):
    """Call this on window resize to rescale assets."""
    self.width = width
    self.height = height
    self.screen = screen
    self.scaled_bg = pygame.transform.smoothscale(self.bg_img, (self.width, self.height))
    self._create_goals()

    # reload and rescale player images
    self.player1_img = self.load_player(self.side_p1, (0,0,255))
    self.player2_img = self.load_player(self.side_p2, (255,0,0))
    # keep players in same center positions
    self.p1 = self.player1_img.get_rect(center=self.p1.center)
    self.p2 = self.player2_img.get_rect(center=self.p2.center)

    # update ball bounds
    self.ball.width = width
    self.ball.height = height

    # recreate back button with new sizes next draw
    self.back_button = None
