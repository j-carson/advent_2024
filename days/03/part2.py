import re
import sys
from pathlib import Path

import pytest
from icecream import ic
from parse import parse

# --> Puzzle solution


def solve(input_data):
    matches = re.findall(r"(mul\(\d{1,3},\d{1,3}\))|(do\(\))|(don't\(\))", input_data)
    score = 0
    active = True
    for match in matches:
        mul, do, dont = match
        if do:
            active = True
        elif dont:
            active = False
        elif mul and active:
            d1, d2 = parse("mul({:d},{:d})", mul)
            score += d1 * d2
    return score


# --> Test driven development helpers


# Test any examples given in the problem

sample_input = Path("input-sample2.txt").read_text().strip()
EXAMPLES = [
    (sample_input, 48),
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
