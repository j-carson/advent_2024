import heapq as q
import sys
from pathlib import Path
from typing import NamedTuple

import numpy as np
import pytest
from icecream import ic

# --> Puzzle solution

MOVES = {
    ">": (0, 1),
    "<": (0, -1),
    "^": (-1, 0),
    "v": (1, 0),
}


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


def parse(input_data):
    grid = np.array([list(i) for i in input_data.splitlines()])
    start_coords = np.where(grid == "S")
    start_pos = start_coords[0][0], start_coords[1][0]

    end_coords = np.where(grid == "E")
    end_pos = end_coords[0][0], end_coords[1][0]

    grid[start_pos] = "k"
    grid[end_pos] = "."

    return grid, start_pos, end_pos


def go(pos, direction):
    move = MOVES[direction]
    return pos[0] + move[0], pos[1] + move[1]


class Maze:
    def __init__(self, grid, end_pos):
        self.grid = grid
        self.goal = end_pos

    def wall(self, pos):
        return self.grid[pos] == "#"

    def done(self, pos):
        return self.goal == pos

    def get_choices(self, cursor):
        result = []

        proposed = go(cursor.pos, cursor.facing)
        if not self.wall(proposed):
            result.append(
                Choice(cursor.turns, cursor.steps + 1, cursor.facing, proposed)
            )

        # To make sure we don't spin forever, a turn implies stepping in that direction
        for turn in POSSIBLE_TURNS[cursor.facing]:
            proposed = go(cursor.pos, turn)
            if not self.wall(proposed):
                result.append(
                    Choice(cursor.turns + 1, cursor.steps + 1, turn, proposed)
                )

        return result


class Choice(NamedTuple):
    turns: int
    steps: int
    facing: str
    pos: tuple[int, int]

    @property
    def score(self):
        return 1000 * self.turns + self.steps

    @property
    def key(self):
        return (*self.pos, self.facing)


def solve(input_data):
    grid, start_pos, end_pos = parse(input_data)
    maze = Maze(grid, end_pos)
    cursor = Choice(0, 0, ">", start_pos)

    best_score = None
    visited_log = {}

    workq = []
    q.heappush(workq, cursor)

    while len(workq):
        cursor = q.heappop(workq)
        if (best_score is not None) and (cursor.score > best_score):
            continue

        choices = maze.get_choices(cursor)

        for choice in choices:
            if maze.done(choice.pos):
                if (best_score is None) or (choice.score < best_score):
                    best_score = choice.score
            else:
                # not done
                key = choice.key
                if key in visited_log:
                    if visited_log[key] > choice.score:
                        visited_log[key] = choice.score
                        q.heappush(workq, choice)
                else:
                    visited_log[key] = choice.score
                    q.heappush(workq, choice)

    return best_score


# --> Test driven development helpers


# Test any examples given in the problem

SAMPLE1 = Path("input-sample.txt").read_text().strip()
SAMPLE2 = Path("input-sample2.txt").read_text().strip()

EXAMPLES = [
    (SAMPLE1, 7036),
    (SAMPLE2, 11048),
]


@pytest.mark.parametrize("sample_data,sample_solution", EXAMPLES, ids=(1, 2))
def test_samples(sample_data, sample_solution) -> None:
    assert solve(sample_data) == sample_solution


# --> Setup and run

if __name__ == "__main__":
    #  Run the test examples with icecream debug-trace turned on
    ic.enable()
    ex = pytest.main(
        [
            __file__,
            "--capture=tee-sys",
        ]
    )
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
