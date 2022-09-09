import random

from pgzero.screen import Screen
from pygame import Rect


class Bird:
    radius = 20

    def __init__(self, x, y, game):
        self.x = x
        self.y = y
        self.dy = 0
        self.dead = False

        self.jumping = False

        self.game = game

        self.dead_time = 0

    def update(self):
        if not self.dead:
            if self.jumping:
                self.dy -= 10
            self.dy += 0.8
            self.dy = min(max(self.dy, -15), 15)
            self.y += self.dy
            self.jumping = False

            if self.y > self.game.height or self.y < 0:
                self.dead = True

            for pipe in self.game.pipes:
                for rect in pipe.rectangles():
                    nx = min(max(self.x, rect.x), rect.x + rect.w)
                    ny = min(max(self.y, rect.y), rect.y + rect.h)
                    if (self.x - nx) ** 2 + (self.y - ny) ** 2 < self.radius ** 2:
                        self.dead = True

            if self.dead:
                self.dead_time = self.game.time

    def draw(self, screen: Screen):
        colour = (200, 200, 200) if self.dead else (0, 0, 0)
        if not self.dead:
            screen.draw.circle((self.x, self.y), Bird.radius, colour)

    def read_env(self):
        pipe = self.game.pipes[0]
        top, bottom = pipe.rectangles()
        return [self.y / self.game.height,
                (pipe.x - self.x) / self.game.width,
                top.bottom / self.game.height,
                bottom.top / self.game.height,
                self.dy / 15]


class Pipe:

    def __init__(self, x, y, width, opening, height):
        self.x = x
        self.y = y
        self.width = width
        self.opening = opening
        self.height = height

    def update(self, speed):
        self.x += speed

    def rectangles(self):
        return [Rect(self.x, 0, self.width, self.y - self.opening),
                Rect(self.x, self.y, self.width, self.height - self.y)]

    def draw(self, screen):
        for r in self.rectangles():
            screen.draw.rect(r, (0, 0, 0))


class FlappyGame:
    pipe_opening = 200
    pipe_spacing = 500
    pipe_width = 100
    pipe_speed = 2

    def __init__(self, width, height, n_players=1):

        self.width = width
        self.height = height

        self.pipes = [Pipe(width, height / 2, FlappyGame.pipe_width, FlappyGame.pipe_opening, self.height)]

        self.birds = [Bird(100, height / 2, self) for _ in range(n_players)]

        self.time = 0

    def update(self):
        for pipe in self.pipes:
            pipe.update(-FlappyGame.pipe_speed)
        self.pipes = list(filter(lambda p: p.x > -FlappyGame.pipe_width, self.pipes))
        if len(self.pipes) == 0 or self.pipes[-1].x < self.width - FlappyGame.pipe_spacing:
            h = random.randint(FlappyGame.pipe_opening, self.height)
            self.pipes.append(Pipe(self.width, h, FlappyGame.pipe_width, FlappyGame.pipe_opening, self.height))

        for bird in self.birds:
            bird.update()

        self.time += 1

    def draw(self, screen: Screen):

        for pipe in self.pipes:
            pipe.draw(screen)

        for bird in self.birds:
            bird.draw(screen)

    def all_dead(self):
        all_dead = True
        for bird in self.birds:
            all_dead = all_dead and bird.dead
        return all_dead
