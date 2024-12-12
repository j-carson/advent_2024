import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pytest
from icecream import ic

# --> Puzzle solution


def go(pos, direction):
    return pos[0] + direction[0], pos[1] + direction[1]


class Map:
    def __init__(self, data):
        self.grid = np.array([list(row) for row in data.splitlines()])
        ic(self.grid)
        self.max_i, self.max_j = self.grid.shape

        self.regions = np.zeros_like(self.grid, dtype=int)
        self.perimeters = defaultdict(int)
        self.areas = defaultdict(int)

        region_id = 1
        while np.sum(self.regions == 0) > 0:
            search_start = self.find_unvisited()
            if not search_start:
                return

            crop = self.grid[search_start]
            self.regions[search_start] = region_id
            self.areas[region_id] += 1
            self.search_region(search_start, region_id, crop)

            region_id += 1

        ic(self.regions)
        ic(self.perimeters)
        ic(self.areas)

    def in_bounds(self, pos):
        return (0 <= pos[0] < self.max_i) and (0 <= pos[1] < self.max_j)

    def find_unvisited(self):
        coords = np.where(self.regions == 0)
        return (coords[0][0], coords[1][0])

    def search_region(self, pos, region_id, crop):
        sides = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for side in sides:
            square = go(pos, side)
            if self.in_bounds(square):
                # Determine if square is same region
                # and unexplored
                if self.regions[square] == 0:
                    if self.grid[square] == crop:
                        self.regions[square] = region_id
                        self.areas[region_id] += 1
                        self.search_region(square, region_id, crop)
                    else:
                        self.perimeters[region_id] += 1
                # It's been visited, it can no longer add area
                # but it can still cause it's neighbors to have perimeter
                elif self.regions[square] != region_id:
                    self.perimeters[region_id] += 1
            else:
                self.perimeters[region_id] += 1

    def score(self):
        total = 0
        for key in self.perimeters.keys():
            total += self.perimeters[key] * self.areas[key]
        return total


def solve(input_data):
    m = Map(input_data)
    return m.score()


# --> Test driven development helpers


# Test any examples given in the problem

s1 = Path("input-sample.txt").read_text().strip()
s2 = Path("input-sample2.txt").read_text().strip()
s3 = Path("input-sample3.txt").read_text().strip()
EXAMPLES = [
    (s1, 140),
    (s2, 772),
    (s3, 1930),
]


@pytest.mark.parametrize("sample_data,sample_solution", EXAMPLES, ids=(1, 2, 3))
def test_samples(sample_data, sample_solution) -> None:
    assert solve(sample_data) == sample_solution


# --> Setup and run

if __name__ == "__main__":
    #  Run the test examples with icecream debug-trace turned on
    ic.enable()
    ex = pytest.main([__file__, "--capture=tee-sys", "-v", "--maxfail=1"])
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
