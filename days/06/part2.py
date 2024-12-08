import sys
from collections import defaultdict
from itertools import product
from pathlib import Path

import numpy as np
import pytest
from icecream import ic

# --> Puzzle solution
DIRECTIONS = {
    "^": (-1, 0),
    "V": (1, 0),
    ">": (0, 1),
    "<": (0, -1),
}
TURNS = {
    "^": ">",
    "V": "<",
    ">": "V",
    "<": "^",
}


class Puzzle:
    __slots__ = [
        "cursor",
        "cursor_pos",
        "grid",
        "infinite_loop_check",
        "input_data",
        "starting_pos",
        "visited",
    ]

    def __init__(self, input_data=None, clone=None):
        if input_data is not None:
            self.input_data = input_data
            self.grid = np.array(
                [list(row) for row in input_data.splitlines()], dtype=str
            )
        if clone is not None:
            self.input_data = clone.input_data
            self.grid = clone.grid.copy()

        self.visited = np.zeros_like(self.grid, dtype=int)
        self.infinite_loop_check = defaultdict(set)

        x, y = np.where((self.grid != "#") & (self.grid != "."))
        self.starting_pos = (x[0], y[0])
        self.cursor_pos = (x[0], y[0])
        self.cursor = self.grid[self.cursor_pos]

        self.visited[self.cursor_pos] = 1
        self.infinite_loop_check[self.cursor_pos].add(self.cursor)

    def is_blocked(self, pos):
        return self.grid[pos] == "#"

    def in_bounds(self, pos):
        i, j = self.grid.shape
        return (0 <= pos[0] < i) and (0 <= pos[1] < j)

    def get_initial_visited(self):
        di, dj = DIRECTIONS[self.cursor]
        while True:
            new_cursor_pos = (self.cursor_pos[0] + di, self.cursor_pos[1] + dj)
            if self.in_bounds(new_cursor_pos):
                if self.is_blocked(new_cursor_pos):
                    self.cursor = TURNS[self.cursor]
                    di, dj = DIRECTIONS[self.cursor]
                else:
                    self.cursor_pos = new_cursor_pos
                    self.visited[new_cursor_pos] = 1
            else:
                return

    def is_infinite_loop(self):
        di, dj = DIRECTIONS[self.cursor]
        while True:
            new_cursor_pos = (self.cursor_pos[0] + di, self.cursor_pos[1] + dj)

            if self.in_bounds(new_cursor_pos):
                if self.is_blocked(new_cursor_pos):
                    self.cursor = TURNS[self.cursor]
                    di, dj = DIRECTIONS[self.cursor]
                else:
                    self.cursor_pos = new_cursor_pos

                if self.cursor in self.infinite_loop_check[self.cursor_pos]:
                    return 1
                self.infinite_loop_check[self.cursor_pos].add(self.cursor)
            else:
                return 0

    def part2(self):
        self.get_initial_visited()

        ni, nj = self.grid.shape
        score = 0
        for i, j in product(range(ni), range(nj)):
            if self.visited[i, j] and ((i, j) != self.starting_pos):
                new_puzzle = Puzzle(clone=self)
                new_puzzle.grid[i, j] = "#"
                score += new_puzzle.is_infinite_loop()

        return score


def solve(input_data):
    puzzle = Puzzle(input_data=input_data)
    return puzzle.part2()


# --> Test driven development helpers


# Test any examples given in the problem

sample_input = Path("input-sample.txt").read_text().strip()
EXAMPLES = [
    (sample_input, 6),
]


@pytest.mark.parametrize("sample_data,sample_solution", EXAMPLES, ids=("sample",))
def test_samples(sample_data, sample_solution) -> None:
    assert solve(sample_data) == sample_solution


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
    result = solve(my_input)
    print(result)
