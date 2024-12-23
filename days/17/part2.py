from collections import defaultdict
from pathlib import Path

import numpy as np
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
    _, _, _, _, program_string = input_data.splitlines()
    program = [int(i) for i in (program_string.split(":")[1]).split(",")]

    cache = defaultdict(list)
    cache[0] = [0]

    for input_len in range(1, len(program) + 1):
        goal = program[-input_len:]
        for i in range(8):
            for item in cache[input_len - 1]:
                A = (item << 3) + i
                puzzle = Computer(A, 0, 0, program)
                puzzle.run()
                if np.all(puzzle.outputs == goal):
                    cache[input_len].append(A)

        assert len(cache[input_len])
    ic(cache[input_len])
    return min(cache[input_len])


if __name__ == "__main__":
    my_input = Path("input.txt").read_text().strip()
    result = solve(my_input)
    print(result)
