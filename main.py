import pygame
from menu import Menu
from option_menu import OptionMenu
from pvp import PvPGameplay
from pvai import PvAIGameplay

# -------------------
# Config
# -------------------
WIDTH = 1600
HEIGHT = 900

# -------------------
# Main
# -------------------
def main():
  pygame.init()
  width, height = WIDTH, HEIGHT
  screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
  pygame.display.set_caption("Tiny football")
  clock = pygame.time.Clock()

  running = True
  playing = False
  state = "menu"

  menu = Menu(screen, width, height)
  option_menu = OptionMenu(screen, width, height)
  pvp_gameplay = None
  pvai_gameplay = None
  current_gameplay = None

  while running:
    events = pygame.event.get()  # central event pump

    # Handle global quit
    for event in events:
      if event.type == pygame.QUIT:
        running = False

    if state == "menu":
      menu.events(events)
      menu.draw()
      if menu.start_selected:
        state = "option"
        menu.start_selected = False
      elif menu.quit_selected:
        running = False

    elif state == "option":
      option_menu.events(events)
      option_menu.draw()
      if option_menu.option_completed:
        if option_menu.selected_mode == "pvp":
          side_p1 = option_menu.selected_side
          side_p2 = option_menu.selected_side_p2
          playing = True
          pvp_gameplay = PvPGameplay(screen, width, height, side_p1, side_p2)
          current_gameplay = pvp_gameplay
          state = "game"
        elif option_menu.selected_mode == "pvai":
          human_side = option_menu.selected_side
          playing = True
          pvai_gameplay = PvAIGameplay(screen, width, height, human_side, "medium")
          current_gameplay = pvai_gameplay
          state = "game"
        else:
          state = "menu"
        option_menu.reset()

    elif state == "game":
      for event in events:
        if event.type == pygame.VIDEORESIZE:
          width, height = event.w, event.h
          screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
          if current_gameplay:
            current_gameplay.resize(width, height, screen)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
          playing = False
          state = "menu"

      if current_gameplay:
        current_gameplay.update()
        current_gameplay.draw()
        
        if current_gameplay and current_gameplay.back_to_menu:
          playing = False
          state = "menu"
          pvp_gameplay = None
          pvai_gameplay = None
          current_gameplay = None

      if not playing:
        state = "menu"

    pygame.display.flip()
    clock.tick(60)

  pygame.quit()


if __name__ == "__main__":
  main()
