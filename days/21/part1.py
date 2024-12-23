import sys
from pathlib import Path
from typing import NamedTuple

import numpy as np
import pytest
from icecream import ic

# --> Puzzle solution

MOVES = {">": (0, 1), "<": (0, -1), "^": (-1, 0), "v": (1, 0)}


class Coord(NamedTuple):
    i: int
    j: int

    def go(self, move):
        offset = MOVES[move]
        return Coord(self.i + offset[0], self.j + offset[1])


class Keypad:
    def __init__(self, layout: np.array):
        self.layout = layout
        self.over = self.whereis("A")
        self.invalid = self.whereis("")
        self.shortrow = self.invalid.i

    def whereis(self, target: str):
        coords_i, coords_j = np.where(self.layout == target)
        return Coord(coords_i[0], coords_j[0])

    def create_path_for(self, sequence):
        path = []
        for item in sequence:
            target = self.whereis(item)
            path.extend(self.makepath(target))
            path.extend("A")
            self.over = target
        return path

    def makepath(self, target: Coord):
        offset_i = target.i - self.over.i
        offset_j = target.j - self.over.j

        j_path = self.j_path(offset_j)
        i_path = self.i_path(offset_i)

        # Moving in only one direction -- nothing to optimize here
        if offset_i == 0:
            return j_path
        if offset_j == 0:
            return i_path

        # Check if the short-row is involved
        if self.over.i == self.shortrow and target.j == 0:
            # We are on the short row, may need to go vertical first if heading to j=0
            return i_path + j_path

        if target.i == self.shortrow and self.over.j == 0:
            # We are going to the the short row, need to go horizontal first leaving from j=0
            return j_path + i_path

        # OK, we get a free choice -- these preferences follow a hint from Reddit...
        pat = i_path[0], j_path[0]
        match pat:
            case "^", "<":
                return j_path + i_path
            case "^", ">":
                return i_path + j_path
            case "v", "<":
                return j_path + i_path
            case "v", ">":
                return i_path + j_path
            case _:
                raise Exception("oops!")

    def i_path(self, offset_i: int):
        if offset_i > 0:
            return ["v"] * offset_i
        if offset_i < 0:
            return ["^"] * abs(offset_i)
        return []

    def j_path(self, offset_j: int):
        if offset_j > 0:
            return [">"] * offset_j
        if offset_j < 0:
            return ["<"] * abs(offset_j)
        return []


class KeypadNumeric(Keypad):
    def __init__(self):
        super().__init__(
            np.array(
                [
                    ["7", "8", "9"],
                    ["4", "5", "6"],
                    ["1", "2", "3"],
                    ["", "0", "A"],
                ]
            ),
        )


def test_keypad_numeric():
    pad = KeypadNumeric()
    path = pad.create_path_for("029A")
    ic("".join(path))
    assert len(path) == len("<A^A>^^AvvvA")


class KeypadArrows(Keypad):
    def __init__(self):
        super().__init__(
            np.array(
                [
                    ["", "^", "A"],
                    ["<", "v", ">"],
                ]
            ),
        )


def test_keypad_arrows():
    pad = KeypadNumeric()
    path = pad.create_path_for("029A")
    pad2 = KeypadArrows()
    path2 = pad2.create_path_for(path)
    ic("".join(path2))
    assert len(path2) == len("v<<A>>^A<A>AvA<^AA>A<vAAA>^A")


@pytest.mark.parametrize(
    "sequence,example_result",
    [
        (
            "029A",
            "<vA<AA>>^AvAA<^A>A<v<A>>^AvA^A<vA>^A<v<A>^A>AAvA^A<v<A>A>^AAAvA<^A>A",
        ),
        ("980A", "<v<A>>^AAAvA^A<vA<AA>>^AvAA<^A>A<v<A>A>^AAAvA<^A>A<vA>^A<A>A"),
        (
            "179A",
            "<v<A>>^A<vA<A>>^AAvAA<^A>A<v<A>>^AAvA^A<vA>^AA<A>A<v<A>A>^AAAvA<^A>A",
        ),
        ("456A", "<v<A>>^AA<vA<A>>^AAvAA<^A>A<vA>^A<A>A<vA>^A<A>A<v<A>A>^AAvA<^A>A"),
        ("379A", "<v<A>>^AvA^A<vA<AA>>^AAvA<^A>AAvA^A<vA>^AA<A>A<v<A>A>^AAAvA<^A>A"),
    ],
)
def test_two_keypads(sequence, example_result):
    pad = KeypadNumeric()
    path = pad.create_path_for(sequence)

    pad2 = KeypadArrows()
    path2 = pad2.create_path_for(path)

    pad3 = KeypadArrows()
    path3 = pad3.create_path_for(path2)

    path3_string = "".join(path3)
    ic(path3_string)
    assert len(path3) == len(example_result)


def score(sequence, pathlen):
    return sequence_num(sequence) * pathlen


def sequence_num(sequence):
    return int(sequence.replace("A", ""))


def solve_one(sequence):
    key1 = KeypadNumeric()
    path1 = key1.create_path_for(sequence)

    key2 = KeypadArrows()
    path2 = key2.create_path_for(path1)

    key3 = KeypadArrows()
    path3 = key3.create_path_for(path2)

    return score(sequence, len(path3))


def solve(input_text):
    score = 0
    for line in input_text.splitlines():
        score += solve_one(line)
    return score


# --> Test driven development helpers


# Test any examples given in the problem

sample_input = Path("input-sample.txt").read_text().strip()
EXAMPLES = [
    (sample_input, 126384),
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
