import sys
from itertools import product
from pathlib import Path
from typing import NamedTuple

import numpy as np
import pytest
from icecream import ic

# --> Puzzle solution

MOVES = {">": (0, 1), "<": (0, -1), "^": (-1, 0), "v": (1, 0)}
POSSIBLE_TURNS = {
    ">": {
        "^",
        "v",
    },
    "<": {
        "^",
        "v",
    },
    "^": {
        ">",
        "<",
    },
    "v": {
        ">",
        "<",
    },
}


def go(pos, direction):
    move = MOVES[direction]
    return pos[0] + move[0], pos[1] + move[1]


def manhattan(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


class Cursor(NamedTuple):
    pos: tuple[int, int]
    direction: str


class Cheat(NamedTuple):
    start_pos: tuple[int, int]
    end_pos: tuple[int, int]


class Maze:
    def __init__(self, grid):
        start = np.where(grid == "S")
        self.start_pos = start[0][0], start[1][0]
        end = np.where(grid == "E")
        self.end_pos = end[0][0], end[1][0]

        max_i, max_j = grid.shape
        self.walls = {
            (i, j) for i, j in product(range(max_i), range(max_j)) if grid[i, j] == "#"
        }

        self.path = self.fill_initial_path()

    def wall(self, pos):
        return pos in self.walls

    def fill_initial_path(self):
        path = []

        # Find a legal direction for the first step
        for move in MOVES:
            if not self.wall(go(self.start_pos, move)):
                cursor = Cursor(self.start_pos, move)
                break
        else:
            raise Exception("oops")
        path.append(cursor.pos)

        while cursor.pos != self.end_pos:
            proposed = go(cursor.pos, cursor.direction)
            if not self.wall(proposed):
                cursor = Cursor(proposed, cursor.direction)
                path.append(cursor.pos)
            else:
                for move in POSSIBLE_TURNS[cursor.direction]:
                    proposed = go(cursor.pos, move)
                    if not self.wall(proposed):
                        cursor = Cursor(proposed, move)
                        path.append(cursor.pos)
                        break
                else:
                    raise Exception("oops")

        assert path[0] == self.start_pos
        assert path[-1] == self.end_pos

        return path

    def count_cheats(self, threshold, max_distance, exact):
        count = 0
        max_path = len(self.path)

        for idx, start in enumerate(self.path):
            tidx_iter = range(idx + threshold, max_path)

            for tidx in tidx_iter:
                end = self.path[tidx]
                distance = manhattan(start, end)
                if distance > max_distance:
                    continue

                savings = tidx - idx - distance
                if exact and (savings == threshold):
                    count += 1
                elif (not exact) and (savings >= threshold):
                    count += 1

        return count

    def score(self, threshold, max_distance=20):
        return self.count_cheats(threshold, max_distance, exact=False)

    def count(self, threshold, max_distance=20):
        return self.count_cheats(threshold, max_distance, exact=True)


def read_input(input_data):
    return np.array([list(row) for row in input_data.splitlines()], dtype="str")


def solve(input_data, threshold):
    grid = read_input(input_data)
    puzzle = Maze(grid)
    return puzzle.score(threshold)


# --> Test driven development helpers


# Test any examples given in the problem

sample_input = Path("input-sample.txt").read_text().strip()
EXAMPLES = [
    (50, 32),
    (52, 31),
    (54, 29),
    (56, 39),
    (58, 25),
    (60, 23),
    (62, 20),
    (64, 19),
    (66, 12),
    (68, 14),
    (70, 12),
    (72, 22),
    (74, 4),
    (76, 3),
]


@pytest.mark.parametrize("threshold,sample_solution", EXAMPLES)
def test_samples(threshold, sample_solution) -> None:
    grid = read_input(sample_input)
    puzzle = Maze(grid)
    assert puzzle.count(threshold) == sample_solution


# --> Setup and run

if __name__ == "__main__":
    #  Run the test examples with icecream debug-trace turned on
    ic.enable()
    ex = pytest.main([__file__, "--capture=tee-sys", "-v"])
    if ex not in {pytest.ExitCode.OK, pytest.ExitCode.NO_TESTS_COLLECTED}:
        print(f"tests FAILED ({ex})")
        sys.exit(1)
    else:
        print("tests PASSED")

    #  Actual input data generally has more iterations, turn off log
    ic.disable()
    my_input = Path("input.txt").read_text().strip()
    result = solve(my_input, 100)
    print(result)
