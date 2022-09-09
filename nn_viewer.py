import numpy as np
import pgzero.keyboard

from network import *
# from pgzero import keyboard
import pgzrun

TITLE = 'Neural Networks'

WIDTH = 1080
HEIGHT = 720

network = Network([2, 2, 2])

mouse_pos = (0, 0)


def on_key_down(key):
    if key == keys.D:
        network.mutate(0.1)



def on_mouse_move(pos):
    global mouse_pos
    mouse_pos = (pos[0] / WIDTH, pos[1] / HEIGHT)


def update():
    network.simulate(mouse_pos)


def draw():
    screen.fill((0, 0, 0))
    network.draw(screen, 10, 10, 1060, 700)


pgzrun.go()
