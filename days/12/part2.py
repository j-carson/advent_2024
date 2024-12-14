import sys
from collections import defaultdict
from pathlib import Path
from typing import NamedTuple, Self

import numpy as np
import pytest
from icecream import ic

# --> Puzzle solution


class Coord(NamedTuple):
    i: int
    j: int

    def go(self, direction: Self):
        return Coord(self.i + direction.i, self.j + direction.j)

    def in_bounds(self, len_i, len_j):
        return (0 <= self.i < len_i) and (0 <= self.j < len_j)


class Segment(NamedTuple):
    location: int
    start: int
    end: int
    travel: int

    @property
    def ordering(self):
        return (self.location, self.start, self.end)


class Map:
    def __init__(self, data):
        self.grid = np.array([list(row) for row in data.splitlines()])

        self.max_i, self.max_j = self.grid.shape
        self.regions = np.zeros_like(self.grid, dtype=int)
        self.horizontal_perimeters = defaultdict(set)
        self.vertical_perimeters = defaultdict(set)
        self.areas = defaultdict(int)
        self.n_sides = defaultdict(int)

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

        self.collapse_permiters_to_sides()

        ic(self.grid)
        ic(self.regions)

    def find_unvisited(self):
        coords = np.where(self.regions == 0)
        return Coord(coords[0][0], coords[1][0])

    def search_region(self, pos: Coord, region_id, crop):
        sides = [Coord(0, 1), Coord(0, -1), Coord(1, 0), Coord(-1, 0)]

        for side in sides:
            square = side.go(pos)
            if square.in_bounds(self.max_i, self.max_j) and (self.grid[square] == crop):
                if self.regions[square] == 0:
                    self.regions[square] = region_id
                    self.areas[region_id] += 1
                    self.search_region(square, region_id, crop)
            else:
                match side:
                    case Coord(0, 1):
                        self.vertical_perimeters[region_id].add(
                            Segment(
                                pos.j + 1,
                                pos.i,
                                pos.i + 1,
                                1,
                            )
                        )

                    case Coord(0, -1):
                        self.vertical_perimeters[region_id].add(
                            Segment(
                                pos.j,
                                pos.i,
                                pos.i + 1,
                                -1,
                            )
                        )

                    case Coord(1, 0):
                        self.horizontal_perimeters[region_id].add(
                            Segment(
                                pos.i + 1,
                                pos.j,
                                pos.j + 1,
                                1,
                            )
                        )

                    case Coord(-1, 0):
                        self.horizontal_perimeters[region_id].add(
                            Segment(
                                pos.i,
                                pos.j,
                                pos.j + 1,
                                -1,
                            )
                        )

    def segments_on_the_same_side(self, seg1: Segment, seg2: Segment):
        if seg1.location != seg2.location:
            return False

        if seg1.travel != seg2.travel:
            return False

        if not (seg1.start == seg2.end or seg1.end == seg2.start):
            return False

        return True

    def collapse_permiters_to_sides(self):
        for region_id in self.areas.keys():
            current_segment = None
            horiz = sorted(
                self.horizontal_perimeters[region_id], key=lambda s: s.ordering
            )
            for segment in horiz:
                if (not current_segment) or (
                    not self.segments_on_the_same_side(current_segment, segment)
                ):
                    self.n_sides[region_id] += 1
                current_segment = segment

            current_segment = None
            vert = sorted(self.vertical_perimeters[region_id], key=lambda s: s.ordering)
            for segment in vert:
                if (not current_segment) or (
                    not self.segments_on_the_same_side(current_segment, segment)
                ):
                    self.n_sides[region_id] += 1
                current_segment = segment

            ic(region_id, self.n_sides[region_id])

    def score(self):
        total = 0
        for key in self.areas.keys():
            total += self.n_sides[key] * self.areas[key]
        return total


def solve(input_data):
    m = Map(input_data)
    return m.score()


# --> Test driven development helpers


# Test any examples given in the problem

s1 = Path("input-sample.txt").read_text().strip()
s2 = Path("input-sample2.txt").read_text().strip()
s3 = Path("input-sample3.txt").read_text().strip()
s4 = Path("input-sample4.txt").read_text().strip()
s5 = Path("input-sample5.txt").read_text().strip()
EXAMPLES = [
    (s1, 80),
    (s2, 436),
    (s3, 1206),
    (s4, 236),
    (s5, 368),
]


@pytest.mark.parametrize("sample_data,sample_solution", EXAMPLES, ids=(1, 2, 3, 4, 5))
def test_samples(sample_data, sample_solution) -> None:
    assert solve(sample_data) == sample_solution


# --> Setup and run

if __name__ == "__main__":
    #  Run the test examples with icecream debug-trace turned on
    ic.enable()
    ex = pytest.main([__file__, "--capture=tee-sys", "-v", "--pdb", "--maxfail=1"])
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
