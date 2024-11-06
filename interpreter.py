# interpreter.py
from hex_extractor import HexExtractor
from instruction import Instruction
from routine import Routine

class Interpreter:
    def __init__(self, extractor, header):
        self.extractor = extractor
        self.header = header
        self.opcode_table = {0xe0: self.op_code__call}
        self.stack = []
        self.debug_instruction_index = 0

    def start_interpreting(self):
        starting_routine_address_from_header = self.header.initial_execution_point - 1
        starting_routine = Routine(self.extractor, starting_routine_address_from_header, [])
        print(f"first routine's address: {starting_routine_address_from_header}")
        print(f"routine's local vars: {starting_routine.local_vars}")
        self.run_routine(starting_routine)
    
    def run_routine(self, routine):
        while self.debug_instruction_index < 2:
            self.debug_instruction_index += 1
            next_instruction = routine.read_next_instruction()
            print(f"\troutine's first instruction's address: {routine.next_instruction_offset:02x}")
            print(f"\tnumber of local vars: {routine.num_local_vars}")
            print(f"\tnumber of local vars: {len(routine.local_vars)}")
            print(f"\toperand_type: {next_instruction.instruction_form}")
            print(f"\tnum_ops: {next_instruction.num_ops}")
            print(f"\topcode: {next_instruction.opcode}")
            print(f"\toperand_types: {next_instruction.operand_types}")
            self.interpret_instruction(next_instruction)

    def interpret_instruction(self, instruction: Instruction):
        self.opcode_table[instruction.full_opcode](instruction)
    
    def op_code__call(self, instruction):
        routine_to_call = instruction.operands[0] * 2
        print(f"\t\t__call instruction calls routine ({routine_to_call:05x})")
        operands_to_pass_on = instruction.operands[1:-1]
        # [instruction.operands[1], instruction.operands[2]]
        called_routine = Routine(self.extractor, routine_to_call, operands_to_pass_on)
        self.run_routine(called_routine)