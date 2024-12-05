import sys
from collections import defaultdict
from pathlib import Path

import pytest
from icecream import ic
from parse import parse

# --> Puzzle solution


class PageOrdering:
    def __init__(self, text):
        self.mentioned_pages = set()
        self.must_be_before = defaultdict(set)
        self.must_be_after = defaultdict(set)

        for row in text.splitlines():
            before, after = parse("{:d}|{:d}", row)

            self.mentioned_pages.add(before)
            self.mentioned_pages.add(after)

            self.must_be_before[after].add(before)
            self.must_be_after[before].add(after)

    def validate(self, row):
        numbers = [int(i) for i in row.split(",")]
        center = numbers[len(numbers) // 2]

        forbidden = set()
        for n in numbers:
            if n not in self.mentioned_pages:
                continue
            if n in forbidden:
                return 0
            for i in self.must_be_before[n]:
                forbidden.add(i)
        return center

    def repair(self, row):
        numbers = [int(i) for i in row.split(",")]
        fixed = False

        while not fixed:
            forbidden = set()
            fixed = True
            for i, n in enumerate(numbers):
                if n not in self.mentioned_pages:
                    continue
                if n in forbidden:
                    numbers[i] = numbers[i - 1]
                    numbers[i - 1] = n
                    fixed = False
                    break
                for ii in self.must_be_before[n]:
                    forbidden.add(ii)

        return numbers[len(numbers) // 2]


def solve(input_data):
    section1, section2 = input_data.split("\n\n")
    page_orders = PageOrdering(section1)
    score = 0
    for row in section2.splitlines():
        if page_orders.validate(row) == 0:
            score += page_orders.repair(row)
    return score


# --> Test driven development helpers


# Test any examples given in the problem

sample_input = Path("input-sample.txt").read_text().strip()
EXAMPLES = [
    (sample_input, 123),
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
