import sys
from pathlib import Path

import numpy as np
import pytest
from icecream import ic

MOVES = {
    "<": (0, -1),
    ">": (0, 1),
    "^": (-1, 0),
    "v": (1, 0),
}


class BoxStuckException(Exception):
    """Box cannot move"""

    pass


# --> Puzzle solution


def parse(input_data):
    grid, moves = input_data.split("\n\n")
    grid_array = np.array([list(line) for line in grid.splitlines()])

    robot_coords = np.where(grid_array == "@")
    robot_pos = robot_coords[0][0], robot_coords[1][0]
    grid_array[robot_pos] = "."

    moves = "".join(moves.splitlines())
    return grid_array, robot_pos, moves


class Puzzle:
    def __init__(self, grid, robot_pos, moves):
        self.robot = Robot(robot_pos, moves)

        self.boxes = []
        box_coords = np.where(grid == "O")
        for i, j in zip(*box_coords):
            self.boxes.append(Box((i, j)))

        self.walls = set()
        wall_coords = np.where(grid == "#")
        for i, j in zip(*wall_coords):
            self.walls.add((i, j))

    def wall(self, pos):
        return pos in self.walls

    def get_box(self, pos):
        for box in self.boxes:
            if box.pos == pos:
                return box
        return None

    def score(self):
        return sum([box.score() for box in self.boxes])


class Robot:
    def __init__(self, pos, moves):
        self.moves = moves
        self.pos = pos

    def step(self, move_ch, grid):
        move = MOVES[move_ch]
        proposed = self.pos[0] + move[0], self.pos[1] + move[1]

        # If we hit a wall, we can't go
        if grid.wall(proposed):
            return

        # is there a box?
        box = grid.get_box(proposed)
        if box is None:
            # No box! just go
            self.pos = proposed
            return

        try:
            box.push(move_ch, grid)
        except BoxStuckException:
            return

        # No exception, I guess we made it!
        self.pos = proposed

    def run(self, grid):
        for move_ch in self.moves:
            self.step(move_ch, grid)


class Box:
    def __init__(self, pos):
        self.pos = pos

    def push(self, move_ch, grid):
        move = MOVES[move_ch]
        proposed = self.pos[0] + move[0], self.pos[1] + move[1]

        # If we hit a wall, we can't go
        if grid.wall(proposed):
            raise BoxStuckException

        # is there another box?
        box = grid.get_box(proposed)
        if box is None:
            # No box! just go
            self.pos = proposed
            return

        # There is a box! Push it too!
        box.push(move_ch, grid)

        # Well, that didn't raise an exception, so it must have worked!
        self.pos = proposed

    def score(self):
        return self.pos[0] * 100 + self.pos[1]


def solve(input_data):
    puzzle = Puzzle(*parse(input_data))
    puzzle.robot.run(puzzle)
    return puzzle.score()


# --> Test driven development helpers


# Test any examples given in the problem

sample_input = Path("input-sample.txt").read_text().strip()
EXAMPLES = [
    (sample_input, 10092),
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
