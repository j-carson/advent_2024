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


def sideways(move_ch):
    return move_ch in {"<", ">"}


class BoxStuckException(Exception):
    """Box cannot move"""

    pass


# --> Puzzle solution


def fatten(ch):
    match ch:
        case "#":
            return ["#", "#"]
        case ".":
            return [".", "."]
        case "O":
            return ["[", "]"]
        case "@":
            return ["@", "."]


def parse(input_data):
    grid, moves = input_data.split("\n\n")

    new_grid = []
    for line in grid.splitlines():
        new_line = []
        for ch in line:
            new_line.extend(fatten(ch))
        new_grid.append(new_line)
    grid_array = np.array(new_grid)

    robot_coords = np.where(grid_array == "@")
    robot_pos = robot_coords[0][0], robot_coords[1][0]
    grid_array[robot_pos] = "."

    moves = "".join(moves.splitlines())
    return grid_array, robot_pos, moves


class Puzzle:
    def __init__(self, grid, robot_pos, moves):
        self.robot = Robot(robot_pos, moves)

        self.boxes = []
        box_coords = np.where(grid == "[")
        for i, j in zip(*box_coords):
            assert grid[i, j + 1] == "]"
            self.boxes.append(FatBox((i, j)))

        self.walls = set()
        wall_coords = np.where(grid == "#")
        for i, j in zip(*wall_coords):
            self.walls.add((i, j))

    def wall(self, pos):
        return pos in self.walls

    def get_box(self, pos):
        for box in self.boxes:
            if pos in box.pos2:
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
            box.propose(move_ch, grid)
        except BoxStuckException:
            return

        # No exception, I guess we made it!
        box.push(move_ch, grid)
        self.pos = proposed

    def run(self, grid):
        for move_ch in self.moves:
            self.step(move_ch, grid)


def coalesce(thing1, thing2):
    result = []
    if thing1 is not None:
        result.append(thing1)
        if (thing2 is not None) and (thing2 is not thing1):
            result.append(thing2)
        return result

    if thing2 is not None:
        result.append(thing2)
    return result


class FatBox:
    def __init__(self, pos):
        self.pos2 = {pos, (pos[0], pos[1] + 1)}

    def push(self, move_ch, grid):
        """Push the box"""
        self.backend(move_ch, grid, dry_run=False)

    def propose(self, move_ch, grid):
        """Propose a move without updating box's state"""
        self.backend(move_ch, grid, dry_run=True)

    def backend(self, move_ch, grid, dry_run):
        if sideways(move_ch):
            self.push_sideways(move_ch, grid, dry_run)
        else:
            self.push_vertical(move_ch, grid, dry_run)

    def push_sideways(self, move_ch, grid, dry_run):
        move = MOVES[move_ch]
        pos1, pos2 = self.pos2

        if move_ch == ">":
            leading_edge = max([pos1, pos2])
        else:
            leading_edge = min([pos1, pos2])

        proposed = leading_edge[0] + move[0], leading_edge[1] + move[1]

        # If we hit a wall, we can't go
        if grid.wall(proposed):
            raise BoxStuckException

        # is there another box?
        box = grid.get_box(proposed)
        if box is None:
            if not dry_run:
                self.pos2 = {
                    (pos1[0] + move[0], pos1[1] + move[1]),
                    (pos2[0] + move[0], pos2[1] + move[1]),
                }
            return

        # There is a box! Ask it to move or move it
        if dry_run:
            box.propose(move_ch, grid)
        else:
            box.push(move_ch, grid)
            # Well, that didn't raise an exception, so it must have worked!
            self.pos2 = {
                (pos1[0] + move[0], pos1[1] + move[1]),
                (pos2[0] + move[0], pos2[1] + move[1]),
            }

    def push_vertical(self, move_ch, grid, dry_run):
        move = MOVES[move_ch]

        pos1, pos2 = self.pos2
        proposed1 = pos1[0] + move[0], pos1[1] + move[1]
        proposed2 = pos2[0] + move[0], pos2[1] + move[1]

        if grid.wall(proposed1) or grid.wall(proposed2):
            raise BoxStuckException

        # Is there another box (could be 2!)
        box1 = grid.get_box(proposed1)
        box2 = grid.get_box(proposed2)
        if box1 is None and box2 is None:
            if not dry_run:
                self.pos2 = {proposed1, proposed2}
            return

        # Yikes, there's a box or maybe even two!
        boxes = coalesce(box1, box2)
        assert len(boxes) > 0

        if dry_run:
            for box in boxes:
                box.propose(move_ch, grid)
        else:
            for box in boxes:
                box.push(move_ch, grid)
            self.pos2 = {proposed1, proposed2}

    def score(self):
        score_pos = min(self.pos2)
        return score_pos[0] * 100 + score_pos[1]


def solve(input_data):
    puzzle = Puzzle(*parse(input_data))
    puzzle.robot.run(puzzle)
    return puzzle.score()


# --> Test driven development helpers


# Test any examples given in the problem

sample_input = Path("input-sample.txt").read_text().strip()
EXAMPLES = [
    (sample_input, 9021),
]


@pytest.mark.parametrize("sample_data,sample_solution", EXAMPLES, ids=("sample",))
def test_samples(sample_data, sample_solution) -> None:
    assert solve(sample_data) == sample_solution


# --> Setup and run

if __name__ == "__main__":
    #  Run the test examples with icecream debug-trace turned on
    ic.enable()
    ex = pytest.main([__file__, "--capture=tee-sys", "-v", "--pdb"])
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
