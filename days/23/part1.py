import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import pytest
from icecream import ic

# --> Puzzle solution


def solve(input_data):
    cache = defaultdict(set)
    for line in input_data.splitlines():
        c1, c2 = line.split("-")
        assert len(c1) == 2
        assert len(c2) == 2

        cache[c1].add(c2)
        cache[c2].add(c1)

    finds = set()
    for key, connections in cache.items():
        if key[0] == "t":
            for o1, o2 in combinations(connections, 2):
                if o1 in cache[o2]:
                    sort_triple = "".join(sorted([key, o1, o2]))
                    finds.add(sort_triple)

    ic(finds)
    return len(finds)


# --> Test driven development helpers


# Test any examples given in the problem

sample_input = Path("input-sample.txt").read_text().strip()
EXAMPLES = [
    (sample_input, 7),
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
