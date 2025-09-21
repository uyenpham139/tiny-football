import pygame

class OptionMenu:
  def __init__(self, game):
    self.game = game
    self.option_displaying = False
    
    self.teams = ['Blue', 'Red']
    
    # Player states
    self.p1 = {"team": 0, "character": 0, "confirmed": False}
    self.p2 = {"team": 0, "character": 0, "confirmed": False}
    
    # Load font once
    try:
      self.button_font = pygame.font.Font("assets/fonts/LuckiestGuy-Regular.ttf", 50)
    except (pygame.error, FileNotFoundError):
      self.button_font = pygame.font.Font(None, 35)
      
  
  def draw(self):
    pass
      
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
          self.game.running = False
          self.option_displaying = False
        
        
  
  
  def display_option_menu(self):
    self.display_option_menu = True
    