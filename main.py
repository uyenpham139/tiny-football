import pygame
from menu import Menu
from option_menu import OptionMenu
from pvp import PvPGameplay

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
          pvp_gameplay = PvPGameplay(screen, width, height, side_p1, side_p2)  # no bg_img needed
          state = "game"
        else:
          state = "menu"
        option_menu.reset()

    elif state == "game":
      for event in events:
        if event.type == pygame.VIDEORESIZE:
          width, height = event.w, event.h
          screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
          if pvp_gameplay:
            pvp_gameplay.resize(width, height, screen)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
          playing = False
          state = "menu"

      if pvp_gameplay:
        pvp_gameplay.update()
        pvp_gameplay.draw()
        
      if pvp_gameplay and not pvp_gameplay.playing:
        state = "menu"

      if not playing:
        state = "menu"

    pygame.display.flip()
    clock.tick(60)

  pygame.quit()


if __name__ == "__main__":
  main()
