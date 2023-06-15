#!/usr/bin/env python3

import re


def translate(source):
    source = re.sub("//[^\n]*", "", source)

    code_writer = CodeWriter()
    for line in source.splitlines():
        words = line.split()
        if words:
            code_writer.append_vm_cmd(words)

    return code_writer.make_asm()


class CodeWriter:
    def __init__(self):
        self.next_addr = 0
        self.asm_cmds = []

    def append_vm_cmd(self, words):
        verb, *rest = words
        self.append_asm(f"// {' '.join(words)}")

        if verb in ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]:
            assert len(rest) == 0
            getattr(self, f"vm_{verb}")()
        elif verb in ["push", "pop"]:
            verb, segment, index = words
            getattr(self, f"vm_{verb}_{segment}")(index)

    def append_asm(self, *cmds):
        for cmd in cmds:
            self.asm_cmds.append(cmd)
            if not cmd.startswith("//"):
                self.next_addr += 1

    def make_asm(self):
        return "\n".join(self.asm_cmds) + "\n"

    def vm_unary_op(self, op):
        self.append_asm("@SP", "A=M-1", f"M={op}M")

    def vm_bin_op(self, op):
        self.append_asm("@SP", "M=M-1", "A=M", "D=M", "A=A-1", f"M=M{op}D")

    def vm_comp_op(self, jmp):
        self.append_asm("@SP", "M=M-1", "A=M", "D=M", "A=A-1", "D=D-M")
        self.append_asm(f"@{self.next_addr + 6}", f"D;{jmp}", "@0", "D=A")
        self.append_asm(f"@{self.next_addr + 4}", "0;JMP", "@1", "D=-A")
        self.append_asm("@SP", "A=M-1", "M=D")

    def vm_neg(self):
        self.vm_unary_op("-")

    def vm_not(self):
        self.vm_unary_op("!")

    def vm_add(self):
        self.vm_bin_op("+")

    def vm_sub(self):
        self.vm_bin_op("-")

    def vm_and(self):
        self.vm_bin_op("&")

    def vm_or(self):
        self.vm_bin_op("|")

    def vm_eq(self):
        self.vm_comp_op("JEQ")

    def vm_gt(self):
        self.vm_comp_op("JLT")

    def vm_lt(self):
        self.vm_comp_op("JGT")

    def vm_push_with_offset(self, label, index):
        self.append_asm(
            f"@{index}",
            "D=A",
            f"@{label}",
            "A=D+M",
            "D=M",
            "@SP",
            "M=M+1",
            "A=M-1",
            "M=D",
        )

    def vm_push_constant(self, index):
        self.append_asm(
            f"@{index}",
            "D=A",
            "@SP",
            "M=M+1",
            "A=M-1",
            "M=D",
        )

    def vm_push_local(self, index):
        self.vm_push_with_offset("LCL", index)

    def vm_push_argument(self, index):
        self.vm_push_with_offset("ARG", index)

    def vm_push_this(self, index):
        self.vm_push_with_offset("THIS", index)

    def vm_push_that(self, index):
        self.vm_push_with_offset("THAT", index)

    def vm_push_temp(self, index):
        self.append_asm(
            f"@{5+int(index)}",
            "D=M",
            "@SP",
            "M=M+1",
            "A=M-1",
            "M=D",
        )

    def vm_push_pointer(self, index):
        if index == "0":
            label = "THIS"
        else:
            label = "THAT"

        self.append_asm(
            f"@{label}",
            "D=M",
            "@SP",
            "M=M+1",
            "A=M-1",
            "M=D",
        )

    def vm_push_static(self, index):
        self.append_asm(
            f"@{16+int(index)}",
            "D=M",
            "@SP",
            "M=M+1",
            "A=M-1",
            "M=D",
        )

    def vm_pop_with_offset(self, label, index):
        self.append_asm(
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            "@R13",
            "M=D",
            f"@{index}",
            "D=A",
            f"@{label}",
            "D=D+M",
            "@R14",
            "M=D",
            "@R13",
            "D=M",
            "@R14",
            "A=M",
            "M=D",
        )

    def vm_pop_local(self, index):
        self.vm_pop_with_offset("LCL", index)

    def vm_pop_argument(self, index):
        self.vm_pop_with_offset("ARG", index)

    def vm_pop_this(self, index):
        self.vm_pop_with_offset("THIS", index)

    def vm_pop_that(self, index):
        self.vm_pop_with_offset("THAT", index)

    def vm_pop_temp(self, index):
        self.append_asm(
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            f"@{5+int(index)}",
            "M=D",
        )

    def vm_pop_pointer(self, index):
        if index == "0":
            label = "THIS"
        else:
            label = "THAT"

        self.append_asm(
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            f"@{label}",
            "M=D",
        )

    def vm_pop_static(self, index):
        self.append_asm(
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            f"@{16+int(index)}",
            "M=D",
        )


if __name__ == "__main__":
    import argparse
    from pathlib import Path

    argparser = argparse.ArgumentParser()
    argparser.add_argument("input_path", type=Path)
    args = argparser.parse_args()

    input_path = args.input_path.resolve()

    for vm_path in input_path.glob("*.vm"):
        asm = translate(vm_path.read_text())
        vm_path.with_suffix(".asm").write_text(asm)
