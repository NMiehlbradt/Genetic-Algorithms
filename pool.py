import copy

from network import *
import numpy as np
import pandas as pd
import random


def elite_selector(fitnesses):
    best = np.argmax(fitnesses)
    return best, best, 0.5


def top_two_selector(fitnesses):
    sorted_ix = np.argsort(fitnesses)
    return sorted_ix[-1], sorted_ix[-2], 0.5


def weighted_selector(fitnesses):
    f_sq = fitnesses ** 2
    normalised = f_sq / np.sum(f_sq)
    a, b = random.choices(np.arange(fitnesses.size), normalised, k=2)
    return a, b, 0.5


class Pool:

    def __init__(self, population, topology,
                 crossover_selector=elite_selector,
                 mutation_rate=0.1,
                 carry_over=10):
        self.population = population

        self.candidates = [Network(topology) for _ in range(population)]
        self.fitnesses = np.zeros(population)
        self.generation = 0

        self.crossover_selector = crossover_selector
        self.mutation_rate = mutation_rate
        self.carry_over = carry_over

    def next_generation(self):
        scores = pd.DataFrame(self.fitnesses)
        print(f'--- Generation {self.generation} ---')
        print(scores.describe())
        print()

        old_candidates = self.candidates

        def do_crossover():
            a_ix, b_ix, ratio = self.crossover_selector(self.fitnesses)
            return crossover(old_candidates[a_ix], old_candidates[b_ix], ratio)

        self.candidates = [do_crossover().mutate(self.mutation_rate) for _ in range(self.population - self.carry_over)]
        # self.candidates.append(best_network)
        for i in np.argsort(self.fitnesses)[:self.carry_over:-1]:
            self.candidates.append(old_candidates[i])

        self.fitnesses = np.zeros(self.population)

        self.generation += 1
