import pygame, os
from ball import Ball

WIN_SCORE = 3

class PvPGameplay:
  def __init__(self, screen, width, height, side_p1, side_p2):
    """
    side_p1, side_p2: 'left' or 'right', coming from OptionMenu
    """
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

    # Load players based on option menu
    self.player1_img = self.load_player(side_p1, (0,0,255))   # blue for left
    self.player2_img = self.load_player(side_p2, (255,0,0))   # red for right

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

    self._create_goals()
    self.running = True
    self.playing = True

  # -------- helpers --------
  def load_player(self, side, tint_color):
    """
    Load team sprite based on side selection from option menu.
    Apply tint to enforce blue (left) or red (right).
    """
    if side == "left":
      path = os.path.join("assets", "Romanos FC (Home Team)", "2.png")
    else:
      path = os.path.join("assets", "Saint Bari (Visitor Team)", "2.png")
    try:
      img = pygame.image.load(path).convert_alpha()
    except:
      img = pygame.Surface((80,80))
      img.fill(tint_color)

    # scale
    target_w = max(80, self.width // 16)
    ratio = target_w / max(1, img.get_width())
    img = pygame.transform.smoothscale(img, (int(img.get_width()*ratio), int(img.get_height()*ratio)))
    return img

  def _create_goals(self):
    goal_height = max(120, self.height // 5)
    goal_thickness = max(32, self.width // 10)
    self.goal_left = pygame.Rect(0, self.height//2 - goal_height//2, goal_thickness, goal_height)
    self.goal_right = pygame.Rect(self.width-goal_thickness, self.height//2 - goal_height//2, goal_thickness, goal_height)

  def resize(self, width, height, screen):
    self.width, self.height, self.screen = width, height, screen
    self.scaled_bg = pygame.transform.smoothscale(self.bg_img, (self.width, self.height))
    self._create_goals()
    # reload scaled/tinted sprites
    self.player1_img = self.load_player(self.side_p1, (0,0,255))
    self.player2_img = self.load_player(self.side_p2, (255,0,0))
    self.p1 = self.player1_img.get_rect(center=self.p1.center)
    self.p2 = self.player2_img.get_rect(center=self.p2.center)
    self.ball.width, self.ball.height = width, height

  def reset_ball(self):
    # always reset ball to center
    self.ball.x, self.ball.y = self.width // 2, self.height // 2
    self.ball.vx, self.ball.vy = 0.0, 0.0
    self.ball.last_touch = None
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

    # keep players within screen
    self.p1.clamp_ip(self.screen.get_rect())
    self.p2.clamp_ip(self.screen.get_rect())

  def update(self):
    # if winner display active, countdown and then finish
    if self.win_timer > 0:
      self.win_timer -= 1
      if self.win_timer == 0:
        self.playing = False
      return

    # normal update
    self.handle_input()
    self.ball.move()

    # kicks with player id so Ball records last_touch
    self.ball.kick(self.p1, 0)
    self.ball.kick(self.p2, 1)

    # goal detection
    scorer = None
    conceding_team = None
    own_goal = False

    if self.ball.rect.colliderect(self.goal_left):
      conceding_team = 0   # left goal belongs to P1
      scorer = 1           # so P2 gets the point
    elif self.ball.rect.colliderect(self.goal_right):
      conceding_team = 1
      scorer = 0

    if scorer is not None:
      # was it an own goal? conceding team last touched it
      own_goal = (self.ball.last_touch is not None and self.ball.last_touch == conceding_team)

      # award point to scorer (opponent of conceding team)
      self.score[scorer] += 1
      self.last_scorer = scorer
      self.last_goal_own = own_goal

      # goal message
      if own_goal:
        self.goal_text = "OWN GOAL!"
      else:
        self.goal_text = f"GOAL!"
      self.goal_text_timer = 120

      # reset ball to the winner's half
      self.reset_ball()

      # check win condition
      if self.score[0] >= WIN_SCORE or self.score[1] >= WIN_SCORE:
        self.winner = 0 if self.score[0] >= WIN_SCORE else 1
        # display winner for 3 seconds (180 frames)
        self.win_timer = 180
        # freeze ball
        self.ball.vx = self.ball.vy = 0.0
        return

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
    
    # draw goals (for debugging / visibility)
    pygame.draw.rect(self.screen, (0, 0, 255), self.goal_left, 3)   # blue outline
    pygame.draw.rect(self.screen, (255, 0, 0), self.goal_right, 3)  # red outline
    
    self.screen.blit(self.player1_img, self.p1)
    self.screen.blit(self.player2_img, self.p2)
    self.ball.draw(self.screen)

    # determine score colors based on side
    p1_color = (0,0,255) if self.side_p1 == "left" else (255,0,0)
    p2_color = (0,0,255) if self.side_p2 == "left" else (255,0,0)

    # draw scores
    p1_score_surf, p1_rect = self.draw_text(str(self.score[0]), 60, p1_color, self.width // 4, 50)
    p2_score_surf, p2_rect = self.draw_text(str(self.score[1]), 60, p2_color, 3 * self.width // 4, 50)
    self.screen.blit(p1_score_surf, p1_rect)
    self.screen.blit(p2_score_surf, p2_rect)

    # goal text (temporary)
    if self.goal_text_timer > 0:
      txt, rect = self.draw_text(self.goal_text, 72, (255, 255, 0), self.width // 2, self.height // 2)
      self.screen.blit(txt, rect)
      self.goal_text_timer -= 1

    # winner text (if any)
    if self.win_timer > 0 and self.winner is not None:
      winner_txt, winner_rect = self.draw_text(
        f"P{self.winner + 1} WINS!", 84, (255, 215, 0),
        self.width // 2, self.height // 2 - 80
      )
      self.screen.blit(winner_txt, winner_rect)
