import sys
from functools import cache
from itertools import product
from pathlib import Path
from typing import NamedTuple, Self

import numpy as np
import numpy.typing as npt
import pytest
from icecream import ic

# --> Puzzle solution

MOVES = {">": (0, 1), "<": (0, -1), "^": (-1, 0), "v": (1, 0)}


class Coord(NamedTuple):
    i: int
    j: int


class KeyPress(NamedTuple):
    key: str
    n_press: int

    def __add__(self, other: Self):
        result = []
        if self.n_press > 0:
            result.append(self)
        if other.n_press > 0:
            result.append(other)
        return KeySequence(sequence=result)

    def __repr__(self):
        return f'KeyPress("{self.key}",{self.n_press})'


class KeySequence(NamedTuple):
    sequence: list[KeyPress]

    def __repr__(self):
        t = "".join(s.key * s.n_press for s in self.sequence)
        return f"KeySequence({t})"

    def append(self, press: KeyPress):
        if press.n_press > 0:
            self.sequence.append(press)

    def __len__(self):
        return sum(s.n_press for s in self.sequence)

    def __add__(self, other: Self):
        return KeySequence(self.sequence + other.sequence)


class Keypad:
    __slots__ = ["home", "layout"]

    def __init__(self, layout: npt.NDArray):
        self.layout = {
            layout[i, j]: Coord(i, j)
            for i, j in product(range(layout.shape[0]), range(layout.shape[1]))
        }
        self.home = self.layout["A"]

    @classmethod
    @cache
    def makepath(cls, source: Coord, target: Coord) -> KeySequence:
        """How to navigate from source to target"""

        offset_i = target.i - source.i
        offset_j = target.j - source.j

        j_path = cls.j_path(offset_j)
        i_path = cls.i_path(offset_i)

        # Check if the short-row is involved
        if source.i == cls.SHORTROW and target.j == 0:
            # We are on the short row, may need to go vertical first if heading to j=0
            return i_path + j_path

        if target.i == cls.SHORTROW and source.j == 0:
            # We are going to the the short row, need to go horizontal first leaving from j=0
            return j_path + i_path

        # these preferences follow a hint from Reddit...
        if offset_j < 0:
            return j_path + i_path
        return i_path + j_path

    @staticmethod
    def i_path(offset_i: int):
        if offset_i > 0:
            return KeyPress("v", offset_i)
        if offset_i < 0:
            return KeyPress("^", abs(offset_i))
        # if n_press is 0, it's always a no-op
        return KeyPress("", 0)

    @staticmethod
    def j_path(offset_j: int):
        if offset_j > 0:
            return KeyPress(">", offset_j)
        if offset_j < 0:
            return KeyPress("<", abs(offset_j))
        return KeyPress("", 0)


class KeypadNumeric(Keypad):
    LAYOUT = np.array(
        [
            ["7", "8", "9"],
            ["4", "5", "6"],
            ["1", "2", "3"],
            ["", "0", "A"],
        ]
    )
    SHORTROW = 3

    def __init__(self):
        super().__init__(self.LAYOUT)

    def get_navigation(self, sequence):
        all_steps = KeySequence([])
        curpos = self.home

        for ch in sequence:
            target = self.layout[ch]
            all_steps += self.makepath(curpos, target)
            all_steps.sequence.append(KeyPress("A", 1))
            curpos = target
        return all_steps


class KeypadArrows(Keypad):
    LAYOUT = np.array(
        [
            ["", "^", "A"],
            ["<", "v", ">"],
        ]
    )
    SHORTROW = 0

    def __init__(self):
        super().__init__(self.LAYOUT)

    def solve(self, sequence: KeySequence, indirection_level: int):
        if indirection_level == 0:
            return len(sequence)

        result = 0
        cur_pos = self.home
        for step in sequence.sequence:
            # Navigate from home to key in step
            result += self.get_navigation_length(
                cur_pos, self.layout[step.key], indirection_level - 1
            )
            # Push the button the correct number of times
            result += step.n_press
            # move the cursor
            cur_pos = self.layout[step.key]

        return result

    @cache
    def get_navigation_length(self, start, end, indirection_level):
        path = self.makepath(start, end)
        if indirection_level == 0:
            return len(path)

        # Now we need to go down another level

        ic(path)
        result = 0
        cur_pos = self.home
        for step in path.sequence:
            # Do the step
            result += self.get_navigation_length(
                cur_pos, self.layout[step.key], indirection_level - 1
            )
            result += step.n_press
            cur_pos = self.layout[step.key]

        if cur_pos != self.home:
            result += self.get_navigation_length(
                cur_pos, self.home, indirection_level - 1
            )
        return result


def test_keypad_numeric_1():
    pad = KeypadNumeric()
    base_sequence = pad.get_navigation("029A")
    assert len(base_sequence) == len("<A^A>^^AvvvA")

    arrows = KeypadArrows()
    length = arrows.solve(base_sequence, 0)
    assert length == len(base_sequence)


def test_keypad_numeric_2():
    pad = KeypadNumeric()
    base_sequence = pad.get_navigation("029A")

    arrows = KeypadArrows()
    length = arrows.solve(base_sequence, 1)
    assert length == len("v<<A>>^A<A>AvA<^AA>A<vAAA>^A")


LEVEL3_TESTS = [
    ("029A", "<vA<AA>>^AvAA<^A>A<v<A>>^AvA^A<vA>^A<v<A>^A>AAvA^A<v<A>A>^AAAvA<^A>A"),
    ("980A", "<v<A>>^AAAvA^A<vA<AA>>^AvAA<^A>A<v<A>A>^AAAvA<^A>A<vA>^A<A>A"),
    ("179A", "<v<A>>^A<vA<A>>^AAvAA<^A>A<v<A>>^AAvA^A<vA>^AA<A>A<v<A>A>^AAAvA<^A>A"),
    ("456A", "<v<A>>^AA<vA<A>>^AAvAA<^A>A<vA>^A<A>A<vA>^A<A>A<v<A>A>^AAvA<^A>A"),
    ("379A", "<v<A>>^AvA^A<vA<AA>>^AAvA<^A>AAvA^A<vA>^AA<A>A<v<A>A>^AAAvA<^A>A"),
]


@pytest.mark.parametrize("code,sample_soln", LEVEL3_TESTS)
def test_keypad_numeric_3(code, sample_soln):
    pad = KeypadNumeric()
    base_sequence = pad.get_navigation(code)

    arrows = KeypadArrows()
    length = arrows.solve(base_sequence, 2)
    assert length == len(sample_soln)


def test_part_1():
    pad = KeypadNumeric()
    arrows = KeypadArrows()
    total = 0
    for code in "029A 980A 179A 456A 379A".split():
        base_sequence = pad.get_navigation(code)
        length = arrows.solve(base_sequence, 2)
        total += score(code, length)
    assert total == 126384


def score(sequence, pathlen):
    return sequence_num(sequence) * pathlen


def sequence_num(sequence):
    return int(sequence.replace("A", ""))


def solve(input_text):
    total = 0
    pad = KeypadNumeric()
    arrows = KeypadArrows()

    for line in input_text.splitlines():
        base_sequence = pad.get_navigation(line)
        length = arrows.solve(base_sequence, 25)
        total += score(line, length)

    return total


# --> Setup and run

if __name__ == "__main__":
    #  Run the test examples with icecream debug-trace turned on
    ic.enable()
    ex = pytest.main([__file__, "--capture=tee-sys", "--maxfail=1", "--pdb"])
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
