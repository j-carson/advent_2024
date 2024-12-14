from itertools import count
from pathlib import Path

import numpy as np
from icecream import ic
from parse import parse

# --> Puzzle solution


class Robot:
    def __init__(self, px, py, vx, vy):
        self.pos = (px, py)
        self.velocity = (vx, vy)

    def step(self, grid_width, grid_height):
        self.pos = (
            (self.pos[0] + self.velocity[0]) % grid_width,
            (self.pos[1] + self.velocity[1]) % grid_height,
        )
        return self.pos

    def manhattan(self, ref_i, ref_j):
        """Guess that when the picture is shown, the robots are mostly
        towards the center of the grid"""
        return np.abs(self.pos[0] - ref_i) + np.abs(self.pos[1] - ref_j)


class Puzzle:
    def __init__(self, grid_width, grid_height):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.robots = []

    def load_robots(self, input_text):
        for line in input_text.splitlines():
            px, py, vx, vy = parse("p={:d},{:d} v={:d},{:d}", line)
            self.robots.append(Robot(px, py, vx, vy))

    def hunt_for_tree(self):
        quad_size = self.grid_width // 2, self.grid_height // 2

        score_to_beat = sum(r.manhattan(*quad_size) for r in self.robots)
        time_to_beat = 0
        no_progress = 0

        for time in count(1):
            score = 0
            for r in self.robots:
                r.step(self.grid_width, self.grid_height)
                score += r.manhattan(*quad_size)
            if score < score_to_beat:
                score_to_beat = score
                time_to_beat = time
                ic(time, score)
                no_progress = 0
            else:
                no_progress += 1

            if no_progress > 10_000:
                break

        return time_to_beat


def solve(input_data, grid_width, grid_height):
    puzzle = Puzzle(grid_width, grid_height)
    puzzle.load_robots(input_data)
    return puzzle.hunt_for_tree()


# --> Setup and run

if __name__ == "__main__":
    #  Actual input data generally has more iterations, turn off log
    my_input = Path("input.txt").read_text().strip()
    result = solve(my_input, 101, 103)
