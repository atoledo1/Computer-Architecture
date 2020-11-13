"""CPU functionality."""
HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
SP = 0b00000111
ADD = 0b10100000
CALL = 0b01010000
RET = 0b00010001
# ~~~~SPRINT~~~~~
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # Step 1: Constructor
        self.reg = [0] * 8 # R0 - R7
        self.ram = [0] * 256 #  256 bites memory
        self.pc = 0

        self.running = False

        self.branchtable = {}
        self.branchtable[HLT] = self.hlt_instruction
        self.branchtable[LDI] = self.ldi_instruction
        self.branchtable[PRN] = self.prn_instruction
        self.branchtable[MUL] = self.mul_instruction
        self.branchtable[PUSH] = self.push_instruction
        self.branchtable[POP] = self.pop_instruction

        self.branchtable[ADD] = self.add_instruction
        self.branchtable[CALL] = self.call_instruction
        self.branchtable[RET] = self.ret_instruction

        # STEP 10
        self.reg[SP] = 0xF4

        # ~~~~SPRINT~~~~~
        self.branchtable[CMP] = self.cmp_instruction
        self.branchtable[JMP] = self.jmp_instruction
        self.branchtable[JEQ] = self.jeq_instruction
        self.branchtable[JNE] = self.jne_instruction
        # Flags:
        self.E = None
        self.L = None
        self.G = None

    # Step 2: RAM methods (ram_read & ram_write)
    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value


    # Step 7: un-hardcoded load()
    def load(self):

        if len(sys.argv) != 2:
            print("usage: comp.py filename")
            sys.exit(1)

        try:
            address = 0

            with open(sys.argv[1]) as f:
                for line in f:
                    t = line.split('#')
                    instruction = t[0].strip()

                    if instruction == "":
                        continue
                    
                    try:
                        instruction = int(instruction, 2) # can specify base as 2nd argument
                    except ValueError:
                        print(f"Invalid number '{instruction}'")
                        sys.exit(1)

                    # print(line, end='')
                    # print(n)
                    self.ram[address] = instruction
                    address += 1

        except FileNotFoundError:
            print(f"File not found: {sys.argv[1]}")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == 'ADD':
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        # Step 8: MUL -- multiply
        elif op == 'MUL':
            self.reg[reg_a] *= self.reg[reg_b]
        # ~~~~~~~~SPRINT~~~~~~~~~
        elif op == 'CMP':
            if self.reg[reg_a] == self.reg[reg_b]:
                self.E = 1
                self.L = 0
                self.G = 0
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.E = 0
                self.L = 1
                self.G = 0
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.E = 0
                self.L = 0
                self.G = 1

    

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()


    # Step 9: Beautify while loop in run():
    def run(self):
        """Run the CPU."""
        self.running = True

        while self.running:
            ir = self.ram[self.pc] # Instruction Register, copy of the currently-executing intruction
            
            if ir in self.branchtable:
                self.branchtable[ir]()
            else:
                print(f"Unknown instrution {ir}")
                sys.exit(3)


    # Step 4: Hlt instruction handler
    def hlt_instruction(self):
        self.running = False

    # Step 5: LDI instruction
    def ldi_instruction(self):
        reg_num = self.ram[self.pc+1]
        value = self.ram[self.pc+2]

        self.reg[reg_num] = value

        self.pc += 3

    # Step 6: PRN instruction
    def prn_instruction(self):
        reg_num = self.ram[self.pc+1]
        print(self.reg[reg_num])
        self.pc += 2


    # STEP 8: MUL instruction

    def mul_instruction(self):
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]

        self.alu("MUL", reg_a, reg_b)

        self.pc += 3

    # STEP 10: Stack System

    def push_instruction(self):
        # Decrement SP
        self.reg[SP] -= 1

        # Get the reg num to push
        reg_num = self.ram[self.pc + 1]

        # Get the value to push
        value = self.reg[reg_num]

        # Copy the value to the SP address
        top_of_stack_addr = self.reg[SP]
        self.ram[top_of_stack_addr] = value

        # print(memory[0xea:0xf4])

        self.pc += 2

    def pop_instruction(self):
        # Get reg to pop into
        reg_num = self.ram[self.pc + 1]

        # Get the top of stack addr
        top_of_stack_addr = self.reg[SP]

        # Get the value at the top of the stack
        value = self.ram[top_of_stack_addr]

        # Store the value in the register
        self.reg[reg_num] = value

        # Increment SP
        self.reg[SP] += 1

        self.pc += 2
    
    # STEP 11: CALL and RET (also ADD)
    def add_instruction(self):
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]

        self.alu("ADD", reg_a, reg_b)

        self.pc += 3


    def call_instruction(self):
        # Compute return addr
        return_addr = self.pc + 2

        # Push return addr on stack:
        # Decrement SP
        self.reg[SP] -= 1

        # Copy the value to the SP address
        top_of_stack_addr = self.reg[SP]
        self.ram[top_of_stack_addr] = return_addr

        # Get the value from the operand reg
        reg_num = self.ram[self.pc + 1]
        value = self.reg[reg_num]

        # Set the self.pc to that value 
        self.pc = value
        

    def ret_instruction(self):
        # Compute return addr 
        # Get the top of stack addr
        top_of_stack_addr = self.reg[SP]

        # Get the value at the top of the stack
        value = self.ram[top_of_stack_addr]

        # Increment the SP
        self.reg[SP] += 1

        # and set it to pc
        self.pc = value
    
    # ~~~~~~~~~SPRINT~~~~~~~~
    def cmp_instruction(self):
        # get the 2 registers
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]

        # use ALU to handle comparison between them and set FLAG values
        self.alu("CMP", reg_a, reg_b)

        # increment pc to reach next instructions
        self.pc += 3

    def jmp_instruction(self): 
        # get address of the given register and set it to pc
        reg_num = self.ram[self.pc + 1]
        self.pc = self.reg[reg_num]

    def jeq_instruction(self):
        if self.E:
            # if E == 1 : jump
            self.jmp_instruction()
        else:
            # otherwise, move on to the next intruction
            self.pc += 2
    
    def jne_instruction(self):
        if not self.E:
            # if E == 0: jump
            self.jmp_instruction()
        else:
            # otherwise, move on to the next instruction
            self.pc += 2















































