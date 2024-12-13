import sys
from pathlib import Path

import pytest
import sympy
from icecream import ic
from parse import parse

# --> Puzzle solution


def valid(count):
    if count <= 100 and type(count) is sympy.core.numbers.Integer:
        return True
    return False


class Game:
    def __init__(self, game_text):
        buttona, buttonb, prize = game_text.splitlines()
        self.ax, self.ay = parse("Button A: X+{:d}, Y+{:d}", buttona)
        self.bx, self.by = parse("Button B: X+{:d}, Y+{:d}", buttonb)
        self.px, self.py = parse("Prize: X={:d}, Y={:d}", prize)

    def solve(self) -> int:
        A, B = sympy.symbols("A B")

        soln = sympy.solve(
            [
                sympy.Eq(self.ax * A + self.bx * B, self.px),
                sympy.Eq(self.ay * A + self.by * B, self.py),
            ]
        )
        if len(soln):
            n_a = soln[A]
            n_b = soln[B]
            if valid(n_a) and valid(n_b):
                return 3 * n_a + n_b
        return 0


def solve(input_data):
    games = input_data.split("\n\n")
    n_prizes = 0
    n_tokens = 0
    for game in games:
        if (score := Game(game).solve()) > 0:
            n_prizes += 1
            n_tokens += score
        ic(game, score)
    return n_tokens


# --> Test driven development helpers


# Test any examples given in the problem

sample_input = Path("input-sample.txt").read_text().strip()
EXAMPLES = [
    (sample_input, 480),
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
