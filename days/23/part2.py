import sys
from collections import defaultdict
from functools import cache
from itertools import combinations
from pathlib import Path

import pytest
from icecream import ic

# --> Puzzle solution


def solve(input_data):
    cxns = defaultdict(set)
    for line in input_data.splitlines():
        c1, c2 = line.split("-")
        assert len(c1) == 2
        assert len(c2) == 2

        # Connect everyone to themselves for convenience
        cxns[c1].add(c1)
        cxns[c1].add(c2)
        cxns[c2].add(c1)
        cxns[c2].add(c2)

    @cache
    def is_full_group(members):
        for m in members:
            for m2 in members:
                if m not in cxns[m2]:
                    return False
        return True

    # Biggest possible group would be...
    max_group = max(len(v) for v in cxns.values())

    for group_size in range(max_group, 0, -1):
        possible_keys = [k for k, v in cxns.items() if len(v) >= group_size]

        for key in possible_keys:
            connections = cxns[key]
            for other_members in combinations(connections, group_size):
                s = set(other_members)
                if key not in s:
                    continue
                if is_full_group(other_members):
                    return ",".join(sorted(other_members))

    return "oops!"


# --> Test driven development helpers


# Test any examples given in the problem

sample_input = Path("input-sample.txt").read_text().strip()
EXAMPLES = [
    (sample_input, "co,de,ka,ta"),
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
