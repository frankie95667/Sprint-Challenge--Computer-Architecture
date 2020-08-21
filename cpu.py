"""CPU functionality."""

import sys
from datetime import datetime

NOP = 0b00000000

LD  = 0b10000011
LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001

AND = 0b10101000
NOT = 0b01101001
OR  = 0b10101010
XOR = 0b10101011

POP = 0b01000110
PUSH= 0b01000101
PRA = 0b01001000
CALL= 0b01010000
CMP = 0b10100111
DEC = 0b01100110
INC = 0b01100101
INT = 0b01010010
IRET= 0b00010011
JEQ = 0b01010101
JGE = 0b01011010
JGT = 0b01010111
JLE = 0b01011001 
JLT = 0b01011000
JMP = 0b01010100
JNE = 0b01010110
RET = 0b00010001
SHL = 0b10101100
SHR = 0b10101101
ST  = 0b10000100

# ALU
ADD = 0b10100000
SUB = 0b10100001
MUL = 0b10100010
DIV = 0b10100011
MOD = 0b10100100 

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0
        self.ie = 0
        self.fl = 0
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[7] = 0xF4
        self.running = False
    
    def ram_read(self, index):
        return self.ram[index]

    def ram_write(self, value, addr):
        self.ram[addr] = value

    def load(self, filename):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:
        f = open(filename)
        program = [line.split("#")[0] for line in f.read().split("\n") if line.split('#')[0] != '']
        
        for instruction in program:
            self.ram[address] = int(instruction, 2)
            address += 1
        


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "INC":
            self.reg[reg_a] += 1
        elif op == "DEC":
            self.reg[reg_a] -= 1
        elif op == "CMP":
            # 00000LGE
            val_a = self.reg[reg_a]
            val_b = self.reg[reg_b]
            if val_a == val_b:
                self.fl = 0b00000001
            elif val_a < val_b:
                self.fl = 0b00000100
            elif val_a > val_b:
                self.fl = 0b00000010
            else:
                self.fl = 0b00000000
        elif op == "AND":
            self.reg[reg_a] &= self.reg[reg_b]
        elif op == "OR":
            self.reg[reg_a] |= self.reg[reg_b]
        elif op == "XOR":
            self.reg[reg_a] ^= self.reg[reg_b]
        elif op == "NOT":
            self.reg[reg_a] = ~self.reg[reg_b]
        elif op == "SHL":
            self.reg[reg_a] <<= self.reg[reg_b]
        elif op == "SHR":
            self.reg[reg_a] >>= self.reg[reg_b]
        elif op == "MOD":
            self.reg[reg_a] = self.reg[reg_a] - (self.reg[reg_a] // self.reg[reg_b]) * self.reg[reg_b]
            # self.reg[reg_a] %= self.reg[reg_b]

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X %02X |" % (
            self.pc,
            self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        self.running = True
        while self.running:
            self.trace()
            IR = self.ram_read(self.pc)
            num_of_operands = (IR >> 6) + 1
            operand_a, operand_b = self.ram_read(self.pc + 1), self.ram_read(self.pc + 2)

            if IR == LDI:
                self.reg[operand_a] = operand_b
            elif IR == PRN:
                print(self.reg[operand_a])
            elif IR == PRA:
                print(chr(self.reg[operand_a]))
            elif IR == MUL:
                self.alu("MUL", operand_a, operand_b)
            elif IR == PUSH:
                self.alu("DEC", 7, None)
                self.ram_write(self.reg[operand_a], self.reg[7])
            elif IR == POP:
                self.reg[operand_a] = self.ram_read(self.reg[7])
                self.alu("INC", 7, None)
            elif IR == CALL:
                self.alu("DEC", 7, None)
                self.ram_write(self.pc + 2, self.reg[7])
                self.pc = self.reg[operand_a]
                num_of_operands = 0
            elif IR == RET:
                self.pc = self.ram_read(self.reg[7])
                self.alu("INC", 7, None)
                num_of_operands = 0
            elif IR == ST:
                self.ram_write(self.reg[operand_b], self.reg[operand_a])
            elif IR == JMP:
                self.pc = self.reg[operand_a]
                num_of_operands = 0
            elif IR == CMP:
                self.alu("CMP", operand_a, operand_b)
            elif IR == JEQ:
                if self.fl == 0b00000001:
                    self.pc = self.reg[operand_a]
                    num_of_operands = 0
            elif IR == JNE:
                if self.fl != 0b00000001:
                    self.pc = self.reg[operand_a]
                    num_of_operands = 0
            elif IR == AND:
                self.alu("AND", operand_a, operand_b)
            elif IR == OR:
                self.alu("OR", operand_a, operand_b)
            elif IR == XOR:
                self.alu("XOR", operand_a, operand_b)
            elif IR == NOT:
                self.alu("NOT", operand_a, operand_b)
            elif IR == SHL:
                self.alu("SHL", operand_a, operand_b)
            elif IR == SHR:
                self.alu("SHR", operand_a, operand_b)
            elif IR == MOD:
                if self.reg[operand_b] == 0:
                    self.running = False
                else:
                    self.alu("MOD", operand_a, operand_b)
            elif IR == HLT:
                self.running = False


            self.pc += num_of_operands

