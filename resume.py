import pygame, os
from button import Button

class PauseMenu:
  def __init__(self, screen, width, height):
    self.screen = screen
    self.width = width
    self.height = height
    
    self.board_img = self._load_image(os.path.join("assets", "pause", "resume-board.png"), (self.width / 3.5, self.height / 1.5))
    self.resume_img = self._load_image(os.path.join("assets", "pause", "resume-button.png"))
    self.quit_img = self._load_image(os.path.join("assets", "pause", "quit-button.png"))

    self.board_rect = self.board_img.get_rect(center=(self.width / 2, self.height / 2))
    self._create_buttons()

  def _load_image(self, path, scale=None, default_size=(100,50)):
    try:
        img = pygame.image.load(path).convert_alpha()
        if scale:
            img = pygame.transform.smoothscale(img, (int(scale[0]), int(scale[1])))
        return img
    except (pygame.error, FileNotFoundError):
        print(f"Warning: Cannot load image at {path}. Using a placeholder.")
        surf = pygame.Surface(scale if scale else default_size, pygame.SRCALPHA); surf.fill((128, 128, 128, 200))
        return surf

  def _create_buttons(self):
    btn_width = self.board_rect.width / 1.5 
    
    resume_w, resume_h = self.resume_img.get_size()
    quit_w, quit_h = self.quit_img.get_size()
    
    scaled_resume_h = int(resume_h * btn_width / max(1, resume_w))
    scaled_quit_h = int(quit_h * btn_width / max(1, quit_w))
    
    scaled_resume_img = pygame.transform.smoothscale(self.resume_img, (int(btn_width), scaled_resume_h))
    scaled_quit_img = pygame.transform.smoothscale(self.quit_img, (int(btn_width), scaled_quit_h))

    spacing = 30
    total_button_height = scaled_resume_h + scaled_quit_h + spacing
    
    start_y = self.board_rect.centery - (total_button_height / 2)
    
    resume_y = start_y
    quit_y = start_y + scaled_resume_h + spacing
    
    button_x = self.board_rect.centerx - (btn_width / 2)
    
    self.resume_button = Button(button_x, resume_y, scaled_resume_img, self.screen)
    self.quit_button = Button(button_x, quit_y, scaled_quit_img, self.screen)

  def draw(self):
    action = None
    overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    self.screen.blit(overlay, (0, 0))

    self.screen.blit(self.board_img, self.board_rect)
    if self.resume_button.draw():
        action = 'resume'
    if self.quit_button.draw():
        action = 'quit'
    return action

  def resize(self, width, height, screen):
    self.width = width
    self.height = height
    self.screen = screen
    self.board_img = self._load_image(os.path.join("assets", "pause", "resume-board.png"), (self.width / 3.5, self.height / 1.5))
    self.board_rect = self.board_img.get_rect(center=(self.width / 2, self.height / 2))
    self._create_buttons()
