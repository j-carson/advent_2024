import sys
from pathlib import Path

import numpy as np
import pytest
from icecream import ic

# --> Puzzle solution


class Trails:
    def __init__(self, input_data):
        self.grid = np.array(
            [[int(i) for i in list(row)] for row in input_data.splitlines()]
        )
        self.max_i, self.max_j = self.grid.shape
        start_coords = np.where(self.grid == 0)
        self.starts = set(zip(start_coords[0], start_coords[1]))

    def in_bounds(self, pos, step):
        new_pos = (pos[0] + step[0], pos[1] + step[1])
        if (0 <= new_pos[0] < self.max_i) and (0 <= new_pos[1] < self.max_j):
            return new_pos
        return None

    def step(self, pos, val):
        go_list = []
        for step in (
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1),
        ):
            if (new_pos := self.in_bounds(pos, step)) and (self.grid[new_pos] == val):
                go_list.append(new_pos)
        return go_list

    def walk_trails(self, start):
        worklist = [start]
        for i in range(1, 10):
            new_worklist = []
            for item in worklist:
                new_worklist.extend(self.step(item, i))
            if not len(new_worklist):
                return 0
            worklist = new_worklist
        return len(worklist)

    def score(self):
        total = 0
        for item in self.starts:
            total += self.walk_trails(item)
        return total


def solve(input_data):
    trails = Trails(input_data)
    return trails.score()


# --> Test driven development helpers


# Test any examples given in the problem

sample_input = Path("input-sample.txt").read_text().strip()
EXAMPLES = [
    (sample_input, 81),
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
