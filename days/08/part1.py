import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np
import pytest
from icecream import ic

# --> Puzzle solution


class Antennas:
    def __init__(self, input_data):
        grid = np.array([list(line) for line in input_data.splitlines()], dtype=str)
        coords = np.where(grid != ".")
        self.shape = grid.shape
        self.locations = defaultdict(list)
        for i, j in zip(coords[0], coords[1]):
            self.locations[grid[i, j]].append((i, j))

        ic(self.shape)
        ic(self.locations)

    def acc_in_bounds(self, acc, pos):
        if (0 <= pos[0] < self.shape[0]) and (0 <= pos[1] < self.shape[1]):
            acc.add(pos)

    def score(self):
        acc = set()
        for freq, pos in self.locations.items():
            for loc1, loc2 in combinations(pos, 2):
                i1, j1 = loc1
                i2, j2 = loc2

                nodei1 = i1 + 2 * (i2 - i1)
                nodej1 = j1 + 2 * (j2 - j1)
                self.acc_in_bounds(acc, (nodei1, nodej1))

                nodei2 = i2 + 2 * (i1 - i2)
                nodej2 = j2 + 2 * (j1 - j2)
                self.acc_in_bounds(acc, (nodei2, nodej2))

        return len(acc)


def solve(input_data):
    return Antennas(input_data).score()


# --> Test driven development helpers


# Test any examples given in the problem

sample_input = Path("input-sample.txt").read_text().strip()
EXAMPLES = [
    (sample_input, 14),
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
