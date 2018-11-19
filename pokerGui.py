import game_logic as gl
import sys, pygame
from Settings import Settings
from pokerStuff import Cards

def run_game():
    pygame.init()
    settings = Settings()
    screen = pygame.display.set_mode((settings.screen_width,settings.screen_height))

    pygame.display.set_caption("Poker")

    gl.loadCards()


    while True:
        gl.check_events(screen)


run_game()
