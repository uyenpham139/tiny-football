import pygame

class Button():
  def __init__(self, x, y, image, game):
    self.image = image
    self.game = game
    self.rect = self.image.get_rect()
    self.rect.topleft = (x, y)
    self.clicked = False
      
  def draw(self):
    action = False
    pos = pygame.mouse.get_pos()
    
    if self.rect.collidepoint(pos):
        if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
            self.clicked = True
            action = True
    
    if pygame.mouse.get_pressed()[0] == 0: 
        self.clicked = False

    self.game.screen.blit(self.image, (self.rect.x, self.rect.y))
    
    return action