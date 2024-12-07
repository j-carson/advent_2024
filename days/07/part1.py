import sys
from functools import cache
from pathlib import Path

import pytest
from icecream import ic

# --> Puzzle solution


@cache
def solve_item(goal, term, vals):
    try_add = term + vals[0]
    try_multiply = term * vals[0]

    if len(vals) == 1:
        if any(
            (
                try_add == goal,
                try_multiply == goal,
            )
        ):
            return goal
        return 0

    if try_add <= goal:
        solve_add = solve_item(goal, try_add, vals[1:])
        if solve_add == goal:
            return goal

    if try_multiply <= goal:
        solve_multiply = solve_item(goal, try_multiply, vals[1:])
        if solve_multiply == goal:
            return goal

    return 0


class Puzzle:
    def __init__(self, line: str):
        goal, rest = line.split(":")
        self.goal = int(goal)
        self.rest = tuple(int(i) for i in rest.split())

    def score(self):
        return solve_item(self.goal, self.rest[0], self.rest[1:])


def solve(input_data):
    score = 0
    for line in input_data.splitlines():
        score += Puzzle(line).score()
    return score


# --> Test driven development helpers


# Test any examples given in the problem

sample_input = Path("input-sample.txt").read_text().strip()
EXAMPLES = [
    (sample_input, 3749),
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
