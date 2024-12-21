import sys
from pathlib import Path

import pytest
from icecream import ic

# --> Puzzle solution


def bitwise_xor(a, b):
    return a ^ b


class Computer:
    def __init__(self, A, B, C, program):
        self.A = A
        self.B = B
        self.C = C
        self.program = program
        self.cursor = 0
        self.outputs = []

    def combo(self, operand):
        match operand:
            case 4:
                return self.A
            case 5:
                return self.B
            case 6:
                return self.C
            case j:
                assert 0 <= j <= 3
                return j

    def output(self, val):
        self.outputs.append(val)

    def run(self):
        while self.cursor < len(self.program):
            self.apply()

    def apply(self) -> int | None:
        opcode = self.program[self.cursor]
        operand = self.program[self.cursor + 1]

        match opcode:
            case 0:
                self.A = self.A // (2 ** self.combo(operand))
                self.cursor += 2
            case 1:
                self.B = bitwise_xor(self.B, operand)
                self.cursor += 2
            case 2:
                self.B = self.combo(operand) % 8
                self.cursor += 2
            case 3:
                if self.A == 0:
                    self.cursor += 2
                else:
                    self.cursor = operand
            case 4:
                self.B = bitwise_xor(self.B, self.C)
                self.cursor += 2
            case 5:
                self.output(self.combo(operand) % 8)
                self.cursor += 2
            case 6:
                self.B = self.A // (2 ** self.combo(operand))
                self.cursor += 2
            case 7:
                self.C = self.A // (2 ** self.combo(operand))
                self.cursor += 2
            case _:
                raise Exception("oops")


def solve(input_data):
    a, b, c, _, program = input_data.splitlines()

    A = int(a.split(":")[1])
    B = int(b.split(":")[1])
    C = int(c.split(":")[1])
    Program = [int(i) for i in (program.split(":")[1]).split(",")]
    ic(A, B, C, Program)

    puzzle = Computer(A, B, C, Program)
    puzzle.run()
    return ",".join([str(i) for i in puzzle.outputs])


# --> Test driven development helpers


# Test any examples given in the problem


def test_instruction2():
    puzzle = Computer(0, 0, 9, [2, 6])
    puzzle.run()
    assert puzzle.B == 1


def test_instruction5():
    puzzle = Computer(10, 0, 0, [5, 0, 5, 1, 5, 4])
    puzzle.run()
    assert puzzle.outputs == [0, 1, 2]


def test_instruction05():
    puzzle = Computer(2024, 0, 0, [0, 1, 5, 4, 3, 0])
    puzzle.run()
    assert puzzle.outputs == [4, 2, 5, 6, 7, 7, 7, 7, 3, 1, 0]
    assert puzzle.A == 0


def test_instruction1():
    puzzle = Computer(0, 29, 0, [1, 7])
    puzzle.run()
    assert puzzle.B == 26


def test_instruction4():
    puzzle = Computer(0, 2024, 43690, [4, 0])
    puzzle.run()
    assert puzzle.B == 44354


sample_input = Path("input-sample.txt").read_text().strip()
EXAMPLES = [
    (sample_input, "4,6,3,5,6,3,5,2,1,0"),
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
