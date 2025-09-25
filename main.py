import pygame, os
from menu import Menu
from option_menu import OptionMenu
from pvp import PvPGameplay
from pvai import PvAIGameplay

WIDTH = 1600
HEIGHT = 900

def main():
  pygame.init()
  pygame.mixer.init() 
  width, height = WIDTH, HEIGHT
  screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
  pygame.display.set_caption("Tiny football")
  clock = pygame.time.Clock()


  try:
      pygame.mixer.music.load(os.path.join("assets", "sfx", "bg.mp3"))
      pygame.mixer.music.set_volume(0.5)
      pygame.mixer.music.play(-1)
  except pygame.error as e:
      print(f"Không thể tải nhạc nền: {e}")

  class DummySound: 
      def play(self): pass

  try:
      kick_sound = pygame.mixer.Sound(os.path.join("assets", "sfx", "kick.mp3"))
      goal_sound = pygame.mixer.Sound(os.path.join("assets", "sfx", "goal.mp3"))
  except pygame.error as e:
      print(f"Không thể tải hiệu ứng âm thanh: {e}")
      kick_sound = goal_sound = DummySound()

  sounds = {"kick": kick_sound, "goal": goal_sound}

  running = True
  playing = False
  state = "menu"

  menu = Menu(screen, width, height)
  option_menu = OptionMenu(screen, width, height)
  pvp_gameplay = None
  pvai_gameplay = None
  current_gameplay = None

  while running:
    events = pygame.event.get()

    for event in events:
      if event.type == pygame.QUIT:
        running = False
      
      if event.type == pygame.VIDEORESIZE:
          width, height = event.w, event.h
          screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
          if state == "menu":
              menu.resize(width, height, screen)
          elif state == "option":
              option_menu.resize(width, height, screen)
          elif state == "game" and current_gameplay:
              current_gameplay.resize(width, height, screen)
      
      if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and state == "game":
          playing = False
          state = "menu"
          
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
          pvp_gameplay = PvPGameplay(screen, width, height, side_p1, side_p2, sounds)
          current_gameplay = pvp_gameplay
          state = "game"
        elif option_menu.selected_mode == "pvai":
          human_side = option_menu.selected_side
          playing = True
          pvai_gameplay = PvAIGameplay(screen, width, height, human_side, "medium", sounds)
          current_gameplay = pvai_gameplay
          state = "game"
        else:
          state = "menu"
        option_menu.reset()

    elif state == "game":
      if current_gameplay:
        current_gameplay.handle_events(events)
        current_gameplay.update()
        current_gameplay.draw()
        
        if current_gameplay.back_to_menu:
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
