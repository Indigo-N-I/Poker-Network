import sys
import pygame as pg
from pokerStuff import Cards
from Settings import position


def load(card, position):
    card.dealt(position)

def check_events(screen):
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            quit()

def loadCards():
    for i in range(1,7):
        card1 = Cards(i, 3)
        card2 = Cards(i, 2)

        position1 = position(i, 1)
        position2 = position(i,2)

        load(card1, position1)
        load(card2, position2)
