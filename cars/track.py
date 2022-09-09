import pygame.surfarray
import tqdm

from raymarching import raymarch
from pgzero.screen import Screen
from abc import ABC, abstractmethod
import numpy as np
import pickle

Point = tuple[float, float]


def draw_bezier(screen, start, control, end, res=100, color=(0, 0, 0)):
    s = np.matrix(start)
    c = np.matrix(control)
    e = np.matrix(end)
    t = np.matrix(np.linspace(0, 1, res)).transpose()
    pts = c.repeat(res, 0) + np.square(1 - t) * (s - c) + np.square(t) * (e - c)
    for a, b in zip(pts, pts[1:, :]):
        screen.draw.line((a[0, 0], a[0, 1]), (b[0, 0], b[0, 1]), color)


class Segment(ABC):
    def __init__(self, sdf):
        self.sdf = sdf

    @abstractmethod
    def display_segment(self, screen: Screen, show_guide: bool):
        pass

    @abstractmethod
    def get_end_point(self) -> Point:
        pass

    @abstractmethod
    def get_start_point(self) -> Point:
        pass

    @abstractmethod
    def get_tangent_line(self) -> tuple[Point, Point]:
        pass


class Line(Segment):

    def __init__(self, start, end):
        super().__init__(raymarch.line_segment_sdf(start, end))
        self.start = start
        self.end = end

    def display_segment(self, screen, show_guide=False, colour=(0, 0, 0)):
        if show_guide:
            screen.draw.circle(self.start, 5, colour)
            screen.draw.circle(self.start, 5, colour)
        screen.draw.line(self.start, self.end, colour)

    def get_end_point(self) -> Point:
        return self.end

    def get_start_point(self) -> Point:
        return self.start

    def get_tangent_line(self) -> tuple[Point, Point]:
        (sx, sy), (ex, ey) = self.start, self.end
        return self.start, (ex - sx, ey - sy)


class Bezier(Segment):

    def __init__(self, start, control, end):
        super().__init__(raymarch.bezier_sdf(start, control, end))
        self.start = start
        self.control = control
        self.end = end

    def display_segment(self, screen, show_guide=False, colour=(0, 0, 0)):
        if show_guide:
            screen.draw.circle(self.start, 5, colour)
            screen.draw.circle(self.control, 5, colour)
            screen.draw.circle(self.end, 5, colour)
        draw_bezier(screen, self.start, self.control, self.end)

    def get_end_point(self) -> Point:
        return self.end

    def get_start_point(self) -> Point:
        return self.start

    def get_tangent_line(self) -> tuple[Point, Point]:
        (sx, sy), (ex, ey) = self.control, self.end
        return self.control, (ex - sx, ey - sy)


class Track:

    def __init__(self, sdf: raymarch.SDF, start: tuple[float, float], checkpoints, image):
        self.sdf = sdf
        self.start = start
        self.checkpoints = checkpoints
        self.image = image
        self.surf = pygame.surfarray.make_surface(image)

    def display(self, screen: Screen):
        screen.blit(self.surf, (0, 0))

    def check_progress(self, checkpoint) -> tuple[int, bool]:
        pass


def generate_image(width: int, height: int, sdf: raymarch.SDF, track_width: float):
    img = np.zeros((width, height, 3))
    for r, _r in tqdm.tqdm(enumerate(img), total=width):
        # print('{:.2f}% done'.format(r / width * 100))
        for c, _ in enumerate(_r):
            d = sdf.query((r, c))
            if d < 2-track_width:
                img[r, c, :] = [230, 230, 230]
            elif d < 0:
                img[r, c, :] = [10, 10, 15]
            elif d < 5:
                img[r, c, :] = [200, 200, 0]
            else:
                img[r, c, :] = [0, 150, 0]

    return img


class TrackBuilder:

    def __init__(self, track_segments: list[Segment], width: int, height: int, track_width: float):
        self.track_segments = track_segments
        self.start = track_segments[0].get_start_point()
        self.track_width = track_width

        sdf = self.track_segments[0].sdf
        for segment in self.track_segments[1:]:
            sdf += segment.sdf
        sdf.annular(self.track_width)

        self.track_img = generate_image(width, height, sdf, self.track_width)

    def make_track(self) -> Track:
        sdf = self.track_segments[0].sdf
        for segment in self.track_segments[1:]:
            sdf += segment.sdf
        sdf.annular(self.track_width)
        return Track(sdf, self.start, [], self.track_img)

    def save(self, filepath: str) -> None:
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)


def load_from_file(filepath) -> TrackBuilder:
    with open(filepath, 'rb') as f:
        track_builder: TrackBuilder = pickle.load(f)

    return track_builder
