import pygame, os
from ball import Ball
from button import Button
from ai import AIController

WIN_SCORE = 3

class PvAIGameplay:
  def __init__(self, screen, width, height, human_side, ai_difficulty="medium"):
    self.screen = screen
    self.width = width
    self.height = height
    self.human_side = human_side
    self.ai_side = "right" if human_side == "left" else "left"

    bg_path = os.path.join("assets", "Field", "Only Field.png")
    try:
      self.bg_img = pygame.image.load(bg_path).convert()
    except (pygame.error, FileNotFoundError):
      self.bg_img = pygame.Surface((self.width, self.height))
      self.bg_img.fill((0, 100, 0))
    self.scaled_bg = pygame.transform.smoothscale(self.bg_img, (self.width, self.height))

    self.human_img = self.load_player(human_side, (0,0,255))
    self.ai_img = self.load_player(self.ai_side, (255,0,0))

    self.ai_controller = AIController(ai_difficulty)

    if human_side == "left":
      self.human_rect = self.human_img.get_rect(center=(200, self.height // 2))
      self.ai_rect = self.ai_img.get_rect(center=(self.width - 200, self.height // 2))
    else:
      self.human_rect = self.human_img.get_rect(center=(self.width - 200, self.height // 2))
      self.ai_rect = self.ai_img.get_rect(center=(200, self.height // 2))
      
    self.player_size = self.human_rect.width

    self.ball = Ball(self.width, self.height, self.player_size, self.width // 2, self.height // 2)

    self.score = [0,0]
    self.goal_text = ""
    self.goal_text_timer = 0
    self.last_scorer = None
    self.last_goal_own = False
    self.winner = None
    self.win_timer = 0
    self.back_to_menu = False

    self._create_goals()
    self._create_play_area()
    self.running = True
    self.playing = True

    try:
      self.button_img = pygame.image.load(os.path.join("assets", "menu-button.png")).convert_alpha()
    except (pygame.error, FileNotFoundError):
      self.button_img = pygame.Surface((200, 50))
      self.button_img.fill((100, 100, 100))

    try:
      self.button_font = pygame.font.Font("assets/fonts/LuckiestGuy-Regular.ttf", 36)
    except (pygame.error, FileNotFoundError):
      self.button_font = pygame.font.Font(None, 28)

    self.back_button = None


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

  def _create_play_area(self):
    margin_x = self.width // 9.5
    margin_y = self.height // 10
    self.main_rect = pygame.Rect(margin_x, margin_y,
                               self.width - 2*margin_x,
                               self.height - 2*margin_y)
    self.play_area = [self.main_rect, self.goal_left, self.goal_right]

  def _create_goals(self):
    goal_height = max(120, self.height // 5)
    goal_thickness = max(32, self.width // 9)
    self.goal_left = pygame.Rect(0, self.height//2 - goal_height//2, goal_thickness, goal_height)
    self.goal_right = pygame.Rect(self.width-goal_thickness, self.height//2 - goal_height//2, goal_thickness, goal_height)

  def reset_ball(self):
    self.ball.x, self.ball.y = self.width // 2, self.height // 2
    self.ball.vx, self.ball.vy = 0.0, 0.0
    self.ball.last_touch = None
    self.ball.rect.center = (int(self.ball.x), int(self.ball.y))
    
  def reset_positions(self):
    self.ball.x, self.ball.y = self.width // 2, self.height // 2
    self.ball.vx, self.ball.vy = 0.0, 0.0
    self.ball.last_touch = None
    self.ball.rect.center = (int(self.ball.x), int(self.ball.y))

    if self.human_side == "left":
      self.human_rect = self.human_img.get_rect(center=(200, self.height // 2))
      self.ai_rect = self.ai_img.get_rect(center=(self.width - 200, self.height // 2))
    else:
      self.human_rect = self.human_img.get_rect(center=(self.width - 200, self.height // 2))
      self.ai_rect = self.ai_img.get_rect(center=(200, self.height // 2))


  def handle_input(self):
    keys = pygame.key.get_pressed()
    speed = 6
    

    if keys[pygame.K_w]: self.human_rect.y -= speed
    if keys[pygame.K_s]: self.human_rect.y += speed
    if keys[pygame.K_a]: self.human_rect.x -= speed
    if keys[pygame.K_d]: self.human_rect.x += speed
    self.human_rect.clamp_ip(self.screen.get_rect())
    

    self.ai_controller.update_ai_player(
        self.ai_rect, self.ball, self.human_rect,
        self.width, self.height, self.goal_left, self.goal_right, self.ai_side
    )

  def update(self):
    if self.winner is not None:
      return

    self.handle_input()
    self.ball.move(self.play_area, self.goal_left, self.goal_right)

    try:
      if self.human_side == "left":
        self.ball.kick(self.human_rect, 0)
        self.ball.kick(self.ai_rect, 1)
      else:
        self.ball.kick(self.human_rect, 1)
        self.ball.kick(self.ai_rect, 0)
    except TypeError:
      self.ball.kick(self.human_rect)
      self.ball.kick(self.ai_rect)

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
      own_goal = (self.ball.last_touch == conceding_team)
      self.score[scorer] += 1
      self.last_scorer = scorer
      self.last_goal_own = own_goal
      self.goal_text = "OWN GOAL!" if own_goal else "GOAL!"
      self.goal_text_timer = 120
      self.reset_ball()
      self.reset_positions()

      if self.score[0] >= WIN_SCORE or self.score[1] >= WIN_SCORE:
        self.winner = 0 if self.score[0] >= WIN_SCORE else 1
        self.ball.vx = self.ball.vy = 0.0
        self.back_button = None
        return


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

  def ensure_back_button(self):
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


  def draw_text(self, text, size, color, x, y):
    try:
      font = pygame.font.Font("assets/fonts/LuckiestGuy-Regular.ttf", size)
    except (pygame.error, FileNotFoundError):
      font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    return text_surface, text_rect

  def draw(self):
    self.screen.blit(self.scaled_bg, (0, 0))

    pygame.draw.rect(self.screen, (255,255,0), self.main_rect, 3)
    pygame.draw.rect(self.screen, (255,255,0), self.goal_left, 3)
    pygame.draw.rect(self.screen, (255,255,0), self.goal_right, 3)


    self.screen.blit(self.human_img, self.human_rect)
    self.screen.blit(self.ai_img, self.ai_rect)
    self.ball.draw(self.screen)

    human_color = (0,0,255) if self.human_side == "left" else (255,0,0)
    ai_color = (255,0,0) if self.human_side == "left" else (0,0,255)

    human_score_surf, human_rect = self.draw_text(str(self.score[0]), 60, human_color, self.width // 4, 50)
    ai_score_surf, ai_rect = self.draw_text(str(self.score[1]), 60, ai_color, 3 * self.width // 4, 50)
    self.screen.blit(human_score_surf, human_rect)
    self.screen.blit(ai_score_surf, ai_rect)

    if self.goal_text_timer > 0:
      txt, rect = self.draw_text(self.goal_text, 72, (255, 255, 0), self.width // 2, self.height // 2)
      self.screen.blit(txt, rect)
      self.goal_text_timer -= 1

    if self.winner is not None:
      winner_name = "HUMAN" if self.winner == 0 else "AI"
      winner_txt, winner_rect = self.draw_text(f"{winner_name} WINS!", 84, (255, 215, 0), self.width // 2, self.height // 2 - 80)
      self.screen.blit(winner_txt, winner_rect)
      self.ensure_back_button()
      if self.back_button:
        clicked = self.back_button.draw()
        self.draw_text_with_stroke(self.screen, self.back_button, "BACK TO MENU", self.button_font, (255,255,255), (0,0,0), stroke_width=4)
        if clicked:
          self.back_to_menu = True

  def resize(self, width, height, screen):
    self.width = width
    self.height = height
    self.screen = screen
    self.scaled_bg = pygame.transform.smoothscale(self.bg_img, (self.width, self.height))
    self._create_goals()
    self._create_play_area()

    self.human_img = self.load_player(self.human_side, (0,0,255) if self.human_side == "left" else (255,0,0))
    self.ai_img = self.load_player(self.ai_side, (255,0,0) if self.human_side == "left" else (0,0,255))
    self.human_rect = self.human_img.get_rect(center=self.human_rect.center)
    self.ai_rect = self.ai_img.get_rect(center=self.ai_rect.center)

    self.ball.width = width
    self.ball.height = height
    self.back_button = None
