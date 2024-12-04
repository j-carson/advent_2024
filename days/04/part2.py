import sys
from pathlib import Path

import numpy as np
import pytest
from icecream import ic

# --> Puzzle solution


class Puzzle:
    def __init__(self, text):
        self.data = np.array(
            [[ch for ch in line] for line in text.splitlines()],
            dtype=str,
        )

    def is_xmas(self, i, j):
        nrow, ncol = self.data.shape
        good = {"M", "S"}

        check1 = set()
        check2 = set()

        for di in (-1, 1):
            bi = i + di
            bj = j + di

            if bi < 0 or bj < 0 or bi >= nrow or bj >= ncol:
                return False
            check1.add(self.data[bi, bj])

            dj = -1 * di
            bi = i + di
            bj = j + dj
            if bi < 0 or bj < 0 or bi >= nrow or bj >= ncol:
                return False
            check2.add(self.data[bi, bj])

        return good == check1 == check2

    def score(self):
        result = 0
        nrow, ncol = self.data.shape

        result = 0
        for row in range(nrow):
            for col in range(ncol):
                if self.data[row, col] == "A":
                    result += self.is_xmas(row, col)

        return result


def solve(input_data):
    puzzle = Puzzle(input_data)
    return puzzle.score()


# --> Test driven development helpers


# Test any examples given in the problem

sample_input = Path("input-sample.txt").read_text().strip()
EXAMPLES = [
    (sample_input, 9),
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
