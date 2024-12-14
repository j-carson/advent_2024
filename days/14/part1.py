import sys
from collections import defaultdict
from pathlib import Path

import pytest
from icecream import ic
from parse import parse

# --> Puzzle solution


class Robot:
    def __init__(self, px, py, vx, vy):
        self.start_pos = (px, py)
        self.velocity = (vx, vy)

    def step(self, grid_width, grid_height, time):
        x = self.start_pos[0] + self.velocity[0] * time
        y = self.start_pos[1] + self.velocity[1] * time
        return (x % grid_width, y % grid_height)


class Puzzle:
    def __init__(self, grid_width, grid_height):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.robots = []

    def load_robots(self, input_text):
        for line in input_text.splitlines():
            px, py, vx, vy = parse("p={:d},{:d} v={:d},{:d}", line)
            self.robots.append(Robot(px, py, vx, vy))

    def get_robot_positions(self, time):
        return [r.step(self.grid_width, self.grid_height, time) for r in self.robots]

    def score(self, positions):
        scores = defaultdict(int)
        quad_size = self.grid_width // 2, self.grid_height // 2

        for p in positions:
            x, y = p
            if x == quad_size[0] or y == quad_size[1]:
                continue

            quad = x < quad_size[0], y < quad_size[1]
            scores[quad] += 1

        score = 1
        for val in scores.values():
            score *= val
        return score


def solve(input_data, grid_width, grid_height, time):
    puzzle = Puzzle(grid_width, grid_height)
    puzzle.load_robots(input_data)
    positions = puzzle.get_robot_positions(time)
    return puzzle.score(positions)


# --> Test driven development helpers


# Test any examples given in the problem

sample_input = Path("input-sample.txt").read_text().strip()
EXAMPLES = [
    (sample_input, 11, 7, 100, 12),
]


@pytest.mark.parametrize(
    "sample_data,grid_w,grid_h,time,sample_solution", EXAMPLES, ids=("sample",)
)
def test_samples(sample_data, grid_w, grid_h, time, sample_solution) -> None:
    assert solve(sample_data, grid_w, grid_h, time) == sample_solution


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
    result = solve(my_input, 101, 103, 100)
    print(result)
