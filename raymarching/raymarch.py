import math

import numpy as np
import numpy.typing as npt
from typing import Callable


class RayMarchData:

    def __init__(self, distance: float, hit_point: np.ndarray):
        self.distance = distance
        self.hit_point = hit_point


class SDF:

    def __init__(self, sdf_function: Callable[[npt.ArrayLike], float]):
        self.sdf_function = sdf_function

    def query(self, point: npt.ArrayLike):
        return self.sdf_function(point)

    def translate(self, x: float, y: float):
        offset = np.array([x, y])
        original_function = self.sdf_function
        self.sdf_function = lambda p: original_function(p - offset)
        return self

    # TODO: Rotation of SDFs
    # def rotate(self, theta: float):
    #     return self

    def round(self, r: float):
        original_function = self.sdf_function
        self.sdf_function = lambda p: original_function(p) - r
        return self

    def annular(self, r: float):
        original_function = self.sdf_function
        self.sdf_function = lambda p: abs(original_function(p)) - r
        return self

    def __add__(self, other):
        return SDF(lambda p: min(self.query(p), other.query(p)))


def circle_sdf(radius: float) -> SDF:
    return SDF(lambda p: np.linalg.norm(p) - radius)


def line_segment_sdf(start: tuple[float, float], end: tuple[float, float]) -> SDF:
    a = np.array(start)
    b = np.array(end)

    def sdf(pos):
        pa = pos - a
        ba = b - a
        h = np.clip(np.dot(pa, ba) / np.dot(ba, ba), 0, 1)
        return np.linalg.norm(pa - ba * h)

    return SDF(sdf)


def bezier_sdf(start: tuple[float, float], control: tuple[float, float], end: tuple[float, float]) -> SDF:
    a1 = np.array(start)
    b1 = np.array(control)
    c1 = np.array(end)

    def sdf(pos) -> float:
        a2 = b1 - a1
        b2 = a1 - 2 * b1 + c1
        c2 = a2 * 2
        d = a1 - pos
        kk = 1 / np.dot(b2, b2)
        kx = kk * np.dot(a2, b2)
        ky = kk * (2 * np.dot(a2, a2) + np.dot(d, b2)) / 3
        kz = kk * np.dot(d, a2)
        p = ky - kx * kx
        p3 = p * p * p
        q = kx * (2 * kx * kx - 3 * ky) + kz
        h = q * q + 4 * p3
        if h >= 0:
            h = math.sqrt(h)
            x = (np.array([h, -h]) - q) / 2
            uv = np.sign(x) * np.power(np.abs(x), 1 / 3)
            t = min(max(uv[0] + uv[1] - kx, 0), 1)
            res = np.square(d + (c2 + b2 * t) * t).sum()
        else:
            z = math.sqrt(-p)
            v = math.acos(q / (p * z * 2)) / 3
            m = math.cos(v)
            n = math.sin(v) * 1.732050808
            t = np.clip(np.array([m + m, -n - m, n - m]), 0, 1)
            res = min(np.square(d + (c2 + b2 * t[0]) * t[0]).sum(), np.square(d + (c2 + b2 * t[1]) * t[1]).sum())

        return math.sqrt(res)

    return SDF(sdf)


def id_sdf() -> SDF:
    return SDF(lambda _: float('inf'))


def march(field: SDF, point: npt.ArrayLike, direction: npt.ArrayLike,
          epsilon: float = 1e-5, max_distance: float = 1000) -> RayMarchData:
    distance: float = 0
    mag = np.linalg.norm(direction)
    if mag == 0:
        return RayMarchData(max_distance, point)
    direction = direction / mag
    sample = abs(field.query(point + distance * direction))
    while sample > epsilon and distance < max_distance:
        distance += sample
        sample = abs(field.query(point + distance * direction))

    distance = min(distance, max_distance)
    return RayMarchData(distance, point + distance * direction)
