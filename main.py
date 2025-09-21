import pygame
from game import Game

def main():
    game = Game()

    while game.running:
        if not game.playing:
            game.curr_menu.display_menu()
        else:
            game.game_loop()
    
    pygame.quit()

if __name__ == "__main__":
    main()