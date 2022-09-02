import pgzrun
from pygame import Rect
import numpy as np
import raymarch

TITLE = 'Raymarching test'
WIDTH = 1080
HEIGHT = 720

mouse_pos = (0, 0)
origin = (50, 50)

pa = (100, 100)
pb = (540, 700)
pc = (980, 50)

# sdf = raymarch.circle_sdf(50).translate(200, 200)
sdf = raymarch.bezier_sdf(pa, pb, pc)
intersect_pt = (0, 0)


def on_mouse_move(pos):
    global mouse_pos
    mouse_pos = pos


def on_mouse_down(pos):
    global origin
    origin = pos


def update():
    global intersect_pt
    direction = np.array(mouse_pos) - np.array(origin)
    intersect_pt = raymarch.march(sdf, origin, direction).hit_point


def draw_bezier(start, control, end, res=100):
    s = np.matrix(start)
    c = np.matrix(control)
    e = np.matrix(end)
    t = np.matrix(np.linspace(0, 1, res)).transpose()
    pts = c.repeat(res, 0) + np.square(1 - t) * (s - c) + np.square(t) * (e - c)
    for a, b in zip(pts, pts[1:, :]):
        screen.draw.line((a[0, 0], a[0, 1]), (b[0, 0], b[0, 1]), (0, 0, 0))


def draw():
    screen.fill((255, 255, 255))
    # screen.draw.rect(Rect(500, 300, 200, 150), (0, 0, 0))
    # screen.draw.circle((200, 200), 50, (0, 0, 0))
    screen.draw.line(origin, intersect_pt, (0, 0, 0))
    draw_bezier(pa, pb, pc)


pgzrun.go()
