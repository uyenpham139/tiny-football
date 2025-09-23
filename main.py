import pygame
from game import Game
from menu import Menu
from option_menu import OptionMenu

def main():
  game = Game()
  menu = Menu(game)
  option_menu = OptionMenu(game)

  state = "menu"  # can be "menu", "option", "game"

  while game.running:
    if state == "menu":
      menu.events()
      menu.draw()
      if menu.start_selected:
        state = "option"
        menu.start_selected = False
      elif menu.quit_selected:
        game.running = False

    elif state == "option":
      option_menu.events()
      option_menu.draw()
      if option_menu.option_completed:
        if option_menu.selected_mode:
          game.playing = True
          state = "game"
        else:
          # Return to menu without starting game
          state = "menu"
        option_menu.reset()

    elif state == "game":
      game.events()
      game.draw()
      if not game.playing:
        state = "menu"

    game.clock.tick(60)

  pygame.quit()

if __name__ == "__main__":
  main()
