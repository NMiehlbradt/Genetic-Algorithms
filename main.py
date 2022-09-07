import numpy as np

from flappy_bird import FlappyGame
from network import Network
import pgzrun

TITLE = 'Neural Networks'

WIDTH = 1080
HEIGHT = 720

game = FlappyGame(WIDTH, HEIGHT)


def on_key_down(key):
    game.birds[0].jumping = True


def update():
    game.update()


def draw():
    screen.fill((255, 255, 255))
    game.draw(screen)


pgzrun.go()
