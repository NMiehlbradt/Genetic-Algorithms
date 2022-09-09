from flappybird.flappy_bird import FlappyGame
import pgzrun
from network.pool import *

TITLE = 'Neural Networks'

WIDTH = 1080
HEIGHT = 720

pool = Pool(population=200,
            topology=[5, 5, 1],
            crossover_selector=weighted_selector,
            mutation_rate=0.01,
            carry_over=1)

game = FlappyGame(WIDTH, HEIGHT, n_players=pool.population)

tick_speed = 1


def on_key_down(key):
    global tick_speed
    if key == keys.DOWN:
        tick_speed -= 1
    if key == keys.UP:
        tick_speed += 1


def update():
    global game

    for _ in range(tick_speed):
        game.update()

        for i, (network, agent) in enumerate(zip(pool.candidates, game.birds)):
            if agent.dead:
                pool.fitnesses[i] = agent.dead_time
            else:
                v = network.simulate(agent.read_env())
                agent.jumping = v[0] > 0.5

        if game.all_dead():
            pool.next_generation()
            game = FlappyGame(WIDTH, HEIGHT, n_players=pool.population)


def draw():
    screen.fill((255, 255, 255))
    game.draw(screen)

    if not game.birds[-1].dead:
        pool.candidates[-1].draw(screen, WIDTH - 200, 10, 200, 100)
    else:
        for i, network in enumerate(pool.candidates):
            if not game.birds[i].dead:
                network.draw(screen, WIDTH - 200, 10, 200, 100)
                break


pgzrun.go()
