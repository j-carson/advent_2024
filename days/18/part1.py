import heapq as q
import sys
from pathlib import Path
from typing import NamedTuple

import numpy as np
import parse as p
import pytest
from icecream import ic

# --> Puzzle solution


MOVES = {">": (0, 1), "<": (0, -1), "^": (-1, 0), "v": (1, 0)}

POSSIBLE_TURNS = {">": {"^", "v"}, "<": {"^", "v"}, "^": {">", "<"}, "v": {">", "<"}}


def go(pos, direction):
    move = MOVES[direction]
    return pos[0] + move[0], pos[1] + move[1]


def get_input(input_data, grid_size, read_count):
    grid = np.full((grid_size, grid_size), ".")
    for line in input_data.splitlines()[:read_count]:
        j, i = p.parse("{:d},{:d}", line)
        grid[i, j] = "#"
    return grid


class Cursor(NamedTuple):
    steps: int
    facing: str
    pos: tuple[int, int]

    @property
    def key(self):
        return (*self.pos, self.facing)


class Maze:
    def __init__(self, grid):
        self.grid = grid
        self.goal = (grid.shape[0] - 1, grid.shape[1] - 1)

    def wall(self, pos):
        i, j = pos
        return (
            (i < 0)
            or (j < 0)
            or (i >= self.grid.shape[0])
            or (j >= self.grid.shape[0])
            or (self.grid[i, j] == "#")
        )

    def done(self, pos):
        return self.goal == pos

    def get_choices(self, cursor):
        result = []

        proposed = go(cursor.pos, cursor.facing)
        if not self.wall(proposed):
            result.append(Cursor(cursor.steps + 1, cursor.facing, proposed))

        # To make sure we don't spin forever, a turn implies stepping in that direction
        for turn in POSSIBLE_TURNS[cursor.facing]:
            proposed = go(cursor.pos, turn)
            if not self.wall(proposed):
                result.append(Cursor(cursor.steps + 1, turn, proposed))

        return result


def solve(input_data, grid_size, read_count):
    grid = get_input(input_data, grid_size, read_count)
    maze = Maze(grid)

    best_score = None
    visited_log = {}

    workq = []
    for turn in MOVES:
        cursor = Cursor(0, turn, (0, 0))
        q.heappush(workq, cursor)

    while len(workq):
        cursor = q.heappop(workq)
        if (best_score is not None) and (cursor.steps > best_score):
            continue

        choices = maze.get_choices(cursor)
        for choice in choices:
            if maze.done(choice.pos):
                if (best_score is None) or (choice.steps < best_score):
                    best_score = choice.steps
            else:
                # not done
                key = choice.key
                if key in visited_log:
                    if visited_log[key] > choice.steps:
                        visited_log[key] = choice.steps
                        q.heappush(workq, choice)
                else:
                    visited_log[key] = choice.steps
                    q.heappush(workq, choice)

    return best_score


# --> Test driven development helpers


# Test any examples given in the problem

sample_input = Path("input-sample.txt").read_text().strip()
EXAMPLES = [
    (sample_input, 7, 12, 22),
]


@pytest.mark.parametrize(
    "sample_data,grid_size,read_count,sample_solution", EXAMPLES, ids=("sample",)
)
def test_samples(sample_data, grid_size, read_count, sample_solution) -> None:
    assert solve(sample_data, grid_size, read_count) == sample_solution


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
    result = solve(my_input, 71, 1024)
    print(result)
