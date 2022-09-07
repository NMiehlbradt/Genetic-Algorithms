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

    def update(self):
        if not self.dead:
            if self.jumping:
                self.dy -= 15
            self.dy += 0.8
            self.dy = max(min(self.dy, 15), -15)
            self.y += self.dy
            self.jumping = False

            if self.y > self.game.height or self.y < 0:
                self.dead = True

            for rect in self.game.pipes:
                nx = min(max(self.x, rect.x), rect.x+rect.w)
                ny = min(max(self.y, rect.y), rect.y + rect.h)
                if (self.x - nx) ** 2 + (self.y - ny) ** 2 < self.radius ** 2:
                    self.dead = True

    def draw(self, screen: Screen):
        colour = (200, 200, 200) if self.dead else (0, 0, 0)
        screen.draw.circle((self.x, self.y), Bird.radius, colour)


class FlappyGame:

    pipe_opening = 150
    pipe_spacing = 500
    pipe_width = 100
    pipe_speed = 2

    def __init__(self, width, height):

        self.width = width
        self.height = height

        self.pipes = [Rect(width, 0, FlappyGame.pipe_width, height/2 - FlappyGame.pipe_opening),
                      Rect(width, height/2, FlappyGame.pipe_width, height/2)]

        self.birds = [Bird(100, height/2, self)]

    def update(self):
        for rect in self.pipes:
            rect.x -= FlappyGame.pipe_speed
        self.pipes = list(filter(lambda r: r.x > -FlappyGame.pipe_width, self.pipes))
        if len(self.pipes) == 0 or self.pipes[-1].x < self.width - FlappyGame.pipe_spacing:
            h = random.randint(FlappyGame.pipe_opening, self.height)
            self.pipes.append(Rect(self.width, 0, FlappyGame.pipe_width, h - FlappyGame.pipe_opening))
            self.pipes.append(Rect(self.width, h, FlappyGame.pipe_width, self.height - h))

        for bird in self.birds:
            bird.update()

    def draw(self, screen: Screen):

        for rect in self.pipes:
            screen.draw.rect(rect, (0, 0, 0))
            screen.draw.rect(rect, (0, 0, 0))

        for bird in self.birds:
            bird.draw(screen)
