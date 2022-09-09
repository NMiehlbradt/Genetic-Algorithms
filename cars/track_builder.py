from __future__ import annotations

import math

import pgzrun
import numpy as np
from pygame import Rect
from pgzero import keyboard
from enum import Enum
from track import *

TITLE = 'Track'
WIDTH = 1080
HEIGHT = 720

Point = tuple[float, float]

black = (0, 0, 0)


class SnapType(Enum):
    NO_SNAP = 0
    GRID = 1
    TANGENT = 2

    def get_next(self):
        members = list(self.__class__)
        index = members.index(self) + 1
        if index >= len(members):
            index = 0
        return members[index]


class Tool(ABC):

    def __init__(self, prev_tool: Tool | None):
        self.pts = []
        if prev_tool is not None and len(prev_tool.pts) != 0:
            self.pts.append(prev_tool.pts[0])
        self.display_name = ''

    def reset(self):
        if len(self.pts) > 0:
            self.pts = [self.pts[-1]]
        else:
            self.pts = []

    @abstractmethod
    def add_point(self, pt) -> Segment | None:
        pass

    @abstractmethod
    def next_tool(self) -> Tool:
        pass

    @abstractmethod
    def display_preview(self, screen, current_mouse_pt):
        pass

    @abstractmethod
    def initial_points(self):
        pass


class LineTool(Tool):

    def __init__(self, prev_tool=None):
        super().__init__(prev_tool)
        self.display_name = 'Line Tool'

    def add_point(self, pt) -> Segment | None:
        self.pts.append(pt)
        if len(self.pts) == 2:
            start, end = self.pts
            self.reset()
            return Line(start, end)

    def next_tool(self) -> Tool:
        return BezierTool(self)

    def display_preview(self, screen, current_mouse_pt):
        if len(self.pts) == 1:
            screen.draw.line(self.pts[0], current_mouse_pt, black)

    def initial_points(self):
        return True


class BezierTool(Tool):

    def __init__(self, prev_tool=None):
        super().__init__(prev_tool)
        self.display_name = 'Bezier Tool'

    def add_point(self, pt) -> Segment | None:
        self.pts.append(pt)
        if len(self.pts) == 3:
            start, control, end = self.pts
            self.reset()
            return Bezier(start, control, end)

    def next_tool(self) -> Tool:
        return LineTool(self)

    def display_preview(self, screen, current_mouse_pt):
        if len(self.pts) == 1:
            screen.draw.line(self.pts[0], current_mouse_pt, black)
        elif len(self.pts) == 2:
            draw_bezier(screen, self.pts[0], self.pts[1], current_mouse_pt)

    def initial_points(self):
        return len(self.pts) <= 2


snapping_mode: SnapType = SnapType.GRID
current_tool: Tool = LineTool()

track_pieces: list[Segment] = []

mouse_pt: Point = (0, 0)

show_grid = False

track: Track | None = None


def snap_nearest(x, y):
    return round(x / 60) * 60, round(y / 60) * 60


def draw():

    screen.fill((255, 255, 255))

    if track is not None:
        track.display(screen)

    if show_grid:
        for i in range(9):
            for j in range(6):
                screen.draw.rect(Rect(i * 120, j * 120, 120, 120), black)

    screen.draw.circle(mouse_pt, 20, black)
    current_tool.display_preview(screen, mouse_pt)

    for segment in track_pieces:
        segment.display_segment(screen, False)

    screen.draw.text(current_tool.display_name, (20, 20), color=black)


def on_mouse_move(pos):
    global mouse_pt, snapping_mode, track_pieces
    if snapping_mode == SnapType.GRID:
        mouse_pt = snap_nearest(*pos)
    elif snapping_mode == SnapType.TANGENT:
        if len(track_pieces) != 0 and current_tool.initial_points():
            (sx, sy), (vx, vy) = track_pieces[-1].get_tangent_line()
            mag = math.sqrt(vx * vx + vy * vy)
            x, y = pos
            px, py = x - sx, y - sy

        else:
            mouse_pt = pos
    else:
        mouse_pt = pos


def on_mouse_down(pos):
    global mouse_pt, current_tool, track_pieces
    new_segment = current_tool.add_point(mouse_pt)
    if new_segment is not None:
        track_pieces.append(new_segment)


def on_key_down(key):
    global show_grid, current_tool, snapping_mode, track
    if key == keyboard.keys.R:
        # Reset
        pass
    if key == keyboard.keys.BACKSPACE:
        # Delete last point
        pass
    if key == keyboard.keys.SPACE:
        # Generate track
        if track is None:
            print('Generating Track')
            builder = TrackBuilder(track_pieces, 30)
            track = builder.make_track(WIDTH, HEIGHT)
        else:
            track = None
    if key == keyboard.keys.G:
        # Show or hide grid
        show_grid = not show_grid
    if key == keyboard.keys.S:
        # Change snapping mode
        snapping_mode = snapping_mode.get_next()
        print(snapping_mode)
    if key == keyboard.keys.T:
        # change tool type
        current_tool = current_tool.next_tool()


pgzrun.go()
