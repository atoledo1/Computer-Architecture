"""CPU functionality."""
import sys

# set instructions in binary
HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010


class CPU:
    """Main CPU class."""
    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8 # eight general purpose registers
        self.ram = [0] * 256 # inital ram to hold 256 bytes of memory
        self.pc = 0  # PROGRAM COUNTER
        self.ir = 0  # INSTRUCTION REGISTER
        self.mar = 0  # MEMORY ADDRESS REGISTER
    def ram_write(self, value, address):
        """
        Writes the value to the address passed in.
        Gets the address through the pc register
        """
        self.ram[address] = value
    def ram_read(self, address):
        """ 
        Accept the address to read and returns the value stored there.
        Get the address through the pc register.
        """
        return self.ram[address]
    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:
        if len(sys.argv) != 2:
            print("usage: ls8.py filename")
            sys.exit(1)

        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    line = line.strip()  # strip deletes empty line/space when printing

                    if line == "" or line[0] == "#":
                        continue  # pushes program through if line is empty

                    try:
                        str_value = line.split("#")[0]
                        value = int(str_value, 2)  # BASE 2, BECAUSE its BINARY
                    except ValueError:
                        print(f"Invalid number: {str_value}")
                        sys.exit(1)
                    self.ram[address] = value
                    address += 1
        except FileNotFoundError:
            print(f"File not found: {sys.argv[1]}")
            sys.exit(2)
            
    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')
        for i in range(8):
            print(" %02X" % self.reg[i], end='')
        print()
    def run(self):
        """Run the CPU."""
        halted = False
        # while running, get instruction from program counter address memory
        while not halted:
            instruction = self.ram[self.pc]
            # get next 2 bytes of data as placeholders for instruction to use
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            # check for different instruction cases
            if instruction == HLT:  # Halt instruction, exits emulator
                halted = True
                self.pc = 0  # set steps counter back to zero
            elif instruction == LDI:  # set value of the register to an integer
                # operand_a is the register number
                # operand_b is the value to set the register to
                self.reg[operand_a] = operand_b
                self.pc += 3
            elif instruction == PRN:  # prints numeric value stored in given register
                # operand_a is the register number
                print(self.reg[operand_a])
                self.pc += 2
            elif instruction == MUL:  # Multiplies reg_a * reg_b
                self.alu("MUL", operand_a, operand_b)
                self.pc += 3
            else:
                print(f"Instruction '{instruction}' not found")    
            

































