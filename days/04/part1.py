import sys
from pathlib import Path

import numpy as np
import pytest
from icecream import ic

# --> Puzzle solution


def is_xmas(data):
    return ("XMAS" == data) or ("SAMX" == data)


class Puzzle:
    def __init__(self, text):
        self.data = np.array(
            [[ch for ch in line] for line in text.splitlines()],
            dtype=str,
        )

    def stride(self, i, j, di, dj):
        nrow, ncol = self.data.shape

        result = []
        for x in range(4):
            if i < 0 or j < 0 or i >= nrow or j >= ncol:
                return ""

            result.append(self.data[i, j])
            i += di
            j += dj

        return "".join(result)

    def score(self):
        result = 0
        nrow, ncol = self.data.shape

        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                if di == 0 and dj == 0:
                    continue

                for row in range(nrow):
                    for col in range(ncol):
                        if self.data[row, col] == "X":
                            result += is_xmas(self.stride(row, col, di, dj))

        return result


def solve(input_data):
    puzzle = Puzzle(input_data)
    return puzzle.score()


# --> Test driven development helpers


# Test any examples given in the problem

sample_input = Path("input-sample.txt").read_text().strip()
EXAMPLES = [
    (sample_input, 18),
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
