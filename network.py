import numpy as np
from typing import Sequence, Dict, Tuple
from pygame import Rect
from pgzero.screen import Screen


class Network:

    def __init__(self, layer_data: Sequence[int]):
        self.layer_data = layer_data
        self.layers = [np.zeros((i, 1)) for i in layer_data]
        self.weights = [np.random.randn(j, i) for i, j in zip(layer_data, layer_data[1:])]
        self.biases = [np.random.randn(i, 1) for i in layer_data[1:]]

        self.node_positions = self.calculate_node_positions()

    def simulate(self, input_data: Sequence[float]) -> np.ndarray:
        self.layers[0] = np.matrix(input_data).transpose()
        for i, weights in enumerate(self.weights):
            self.layers[i + 1] = weights * self.layers[i] + self.biases[i]
            self.layers[i + 1] = 1 / (1 + np.exp(-self.layers[i + 1]))

        return self.layers[-1]

    def mutate(self, mutation_rate):
        for layer in self.layers:
            layer_shape = layer.shape
            modifications = (np.random.uniform(size=layer_shape) < mutation_rate) * np.random.normal(size=layer_shape)
            layer += modifications

        for bias in self.biases:
            bias_shape = bias.shape
            modifications = (np.random.uniform(size=bias_shape) < mutation_rate) * np.random.normal(size=bias_shape)
            bias += modifications

    def calculate_node_positions(self) -> Dict[Tuple[int, int], Tuple[float, float]]:
        node_positions = {}

        x_spacing = 1 / len(self.layer_data)
        y_spacings = list(map(lambda x: 1 / x, self.layer_data))

        for layer, n_nodes in enumerate(self.layer_data):
            for i in range(n_nodes):
                node_positions[(layer, i)] = ((layer + 0.5) * x_spacing, (i + 0.5) * y_spacings[layer])

        return node_positions

    def draw(self, screen: Screen, x: float, y: float, w: float, h: float) -> None:
        screen.draw.filled_rect(Rect(x, y, w, h), (255, 255, 255))

        node_radius = min(min(map(lambda a: h / a, self.layer_data)), w / len(self.layer_data)) * 0.4

        for i, weights in enumerate(self.weights):
            rows, cols = weights.shape
            for r in range(rows):
                for c in range(cols):
                    s_x, s_y = self.node_positions[(i, c)]
                    e_x, e_y = self.node_positions[(i + 1, r)]
                    colour_mod = min(255, abs(weights[r, c])/2 * 255)
                    c = (255, colour_mod, colour_mod) if weights[r, c] < 0 else (colour_mod, 255, colour_mod)
                    screen.draw.line((x + s_x * w, y + s_y * h), (x + e_x * w, y + e_y * h), c)

        for i, n_nodes in enumerate(self.layer_data):
            for n in range(n_nodes):
                n_x, n_y = self.node_positions[(i, n)]
                c = self.layers[i][n] * 255
                screen.draw.filled_circle((x + n_x * w, y + n_y * h), node_radius, (c, c, c))
                screen.draw.circle((x + n_x * w, y + n_y * h), node_radius, (0, 0, 0))

    def print(self) -> None:
        for i in range(len(self.layer_data)-1):
            print(self.weights[i])
            print(self.biases[i])
