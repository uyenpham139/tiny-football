import pygame, os
# import random
from menu import Menu
# from resume import Resume
# from button import Button

print(__file__)
# Kích thước ban đầu
WIDTH = 1600
HEIGHT = 900
ZOMBIE_SIZE = 80
HIT_RADIUS = 45
MAX_ZOMBIES = 2
BG = os.path.join("assets", "Field", "Only Field.png")

class Game:
    def __init__(self):
        pygame.init()
        
        self.width, self.height = WIDTH, HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("Tiny football")
        self.clock = pygame.time.Clock()
        self.bg_img = pygame.image.load(BG).convert() 
        
        self.running, self.playing = True, False
        
        self.curr_menu = Menu(self)
    
    def draw_text(self, text, size, color, x, y):
        font = pygame.font.Font("assets/fonts/LuckiestGuy-Regular.ttf", size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        return text_surface, text_rect
    
    def draw(self):      
        bg_img = pygame.transform.scale(self.bg_img, (self.width, self.height))
        self.screen.blit(bg_img, (0,0))
        pygame.display.flip()
    
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.playing = False
            
            elif event.type == pygame.VIDEORESIZE:
                self.width, self.height = event.w, event.h
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
                self.playing = False
    
    def game_loop(self):
        self.start_time = pygame.time.get_ticks()
        while self.playing:
            self.events()
            self.draw()
            self.clock.tick(60)
    
    