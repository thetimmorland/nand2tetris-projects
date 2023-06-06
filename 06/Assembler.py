#!/usr/bin/env python3

from dataclasses import dataclass
import re


class LCommand:
    def __init__(self, s):
        self.symbol = s[1:-1]


class ACommand:
    def __init__(self, s):
        self.symbol = s[1:]


class CCommand:
    DEST = {
        None:   0,
        "M=":   1,
        "D=":   2,
        "MD=":  3,
        "A=":   4,
        "AM=":  5,
        "AD=":  6,
        "AMD=": 7
    }

    COMP = {
        "0":   0b0_101010,
        "1":   0b0_111111,
        "-1":  0b0_111010,
        "D":   0b0_001100,
        "A":   0b0_110000,
        "!D":  0b0_001101,
        "!A":  0b0_110001,
        "-D":  0b0_001111,
        "-A":  0b0_110011,
        "D+1": 0b0_011111,
        "A+1": 0b0_110111,
        "D-1": 0b0_001110,
        "A-1": 0b0_110010,
        "D+A": 0b0_000010,
        "D-A": 0b0_010011,
        "A-D": 0b0_000111,
        "D&A": 0b0_000000,
        "D|A": 0b0_010101,

        "M":   0b1_110000,
        "!M":  0b1_110001,
        "-M":  0b1_110011,
        "M+1": 0b1_110111,
        "M-1": 0b1_110010,
        "D+M": 0b1_000010,
        "D-M": 0b1_010011,
        "M-D": 0b1_000111,
        "D&M": 0b1_000000,
        "D|M": 0b1_010101,
    }

    JUMP = {
        None: 0,
        ";JGT": 1,
        ";JEQ": 2,
        ";JGE": 3,
        ";JLT": 4,
        ";JNE": 5,
        ";JLE": 6,
        ";JMP": 7,
    }

    def __init__(self, dest, comp, jump):
        self.dest = self.DEST[dest]
        self.comp = self.COMP[comp]
        self.jump = self.JUMP[jump]


def parse(s):
    s = re.sub("//.*", '', s) # remove comments
    r = re.compile("(\(.+\))|(@.+)|(.+=)?([^;]+)(;.+)?")

    commands = []
    for token in s.split():
        if s == "":
            continue

        match = r.fullmatch(token)
        l, a, c_dest, c_comp, c_jump = match.groups()

        if l is not None:
            commands.append(LCommand(l))
        elif a is not None:
            commands.append(ACommand(a))
        else:
            commands.append(CCommand(c_dest, c_comp, c_jump))

    return commands


class SymbolTable:
    symbols = {
        "SP":   0,
        "LCL":  1,
        "ARG":  2,
        "THIS": 3,
        "THAT": 4,

        "R0":  0,
        "R1":  1,
        "R2":  2,
        "R3":  3,
        "R4":  4,
        "R5":  5,
        "R6":  6,
        "R7":  7,
        "R8":  8,
        "R9":  9,
        "R10": 10,
        "R11": 11,
        "R12": 12,
        "R13": 13,
        "R14": 14,
        "R15": 15,

        "SCREEN": 0x4000,
        "KBD":    0x6000
    }

    def add_entry(self, symbol, addr):
        self.symbols[symbol] = addr

    def contains(self, symbol):
        return symbol.isdigit() or symbol in self.symbols

    def get_address(self, symbol):
        if symbol.isdigit():
            return int(symbol)

        return self.symbols[symbol]


def assemble(asm):
    commands = parse(asm)
    s_table = SymbolTable()

    label_addr = 0
    for command in commands:
        if isinstance(command, LCommand):
            s_table.add_entry(command.symbol, label_addr)
        else:
            label_addr += 1

    hack = ""
    var_addr = 16
    for command in commands:
        if isinstance(command, ACommand):
            if not s_table.contains(command.symbol):
                s_table.add_entry(command.symbol, var_addr)
                var_addr += 1

            address = s_table.get_address(command.symbol)
            hack += f"0{address:015b}\n"

        elif isinstance(command, CCommand):
            hack += f"111{command.comp:07b}{command.dest:03b}{command.jump:03b}\n"

    return hack


if __name__ == "__main__":
    import argparse
    from pathlib import Path

    argparser = argparse.ArgumentParser()
    argparser.add_argument("input_path", type=Path)
    args = argparser.parse_args()

    input_path = args.input_path.resolve()
    output_path = input_path.with_suffix(".hack")

    print(f"Assembling {input_path}")
    hack = assemble(input_path.read_text())
    output_path.write_text(hack)
    print(f"Wrote {output_path}")
