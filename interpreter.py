# interpreter.py
from hex_extractor import HexExtractor
from instruction import Instruction
from routine import Routine

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Interpreter:
    def __init__(self, extractor, header):
        self.extractor = extractor
        self.header = header
        self.opcode_table = {0xe0: self.op_code__call, 0x54: self.op_code__add, 0x74: self.op_code__add}
        self.stack = []
        self.global_vars = [0x00] * 240

        self.debug_instruction_index = 0
        self.debug_instruction_from_dict = {0: "short", 1: "long", 2: "variable"}
        # print(f"{bcolors.WARNING}Original contents of global vars: {self.global_vars}{bcolors.ENDC}")


    def start_interpreting(self):
        starting_routine_address_from_header = self.header.initial_execution_point - 1
        starting_routine = Routine(self.extractor, starting_routine_address_from_header, [], self)
        print(f"first routine's address: {starting_routine_address_from_header}")
        print(f"routine's local vars: {starting_routine.local_vars}")
        self.run_routine(starting_routine)
    
    def run_routine(self, routine):
        return_value = 0
        while self.debug_instruction_index < 4:
            self.debug_instruction_index += 1
            next_instruction = routine.read_next_instruction()
            print(f"\troutine's first instruction's address: {routine.next_instruction_offset:02x}")
            print(f"\tnumber of local vars: {routine.num_local_vars}")
            print(f"\tinstruction_form: {self.debug_instruction_from_dict[next_instruction.instruction_form]}")
            print(f"\tnum_ops: {next_instruction.num_ops}")
            print(f"\topcode: {next_instruction.opcode}")
            print(f"\toperand_types: {next_instruction.operand_types}")
            print(f"\taddress_of_store_target (if it exists): {next_instruction.storage_target_address:02x}")
            print(f"\taddress_of_branch_target (if it exists): {next_instruction.branch_target_address:02x}")
            self.interpret_instruction(next_instruction, routine)
        return return_value

    def interpret_instruction(self, instruction: Instruction, associated_routine: Routine):
        self.opcode_table[instruction.full_opcode](instruction, associated_routine)
    
    def store_result(self, result_to_store, storage_target, current_routine):
        if (storage_target == 0x00):
            self.stack.append(result_to_store)
        elif (storage_target > 0x00 and storage_target < 0x10): # 0x01 to 0xf0 are meant for local vars
            current_routine.local_vars[storage_target - 1] = result_to_store
        elif (storage_target > 0x0f and storage_target < 0x100): # 0x10 to 0xff are meant for global_vars
            self.global_vars[storage_target - 0x10] = result_to_store

    def op_code__call(self, instruction, associated_routine):
        routine_to_call = instruction.operands[0] * 2
        print(f"\t\t__call instruction calls routine ({routine_to_call:05x})")
        operands_to_pass_on = instruction.operands[1:-1]
        result_storage_target = self.extractor.read_byte(instruction.storage_target_address)
        called_routine = Routine(self.extractor, routine_to_call, operands_to_pass_on, self)

        # update address of next instruction based on if there was a store byte or branch byte
        associated_routine.next_instruction_offset = instruction.storage_target_address + 1

        self.store_result(self.run_routine(called_routine), result_storage_target, associated_routine)

    def op_code__add(self, instruction, associated_routine):
        result_storage_target = self.extractor.read_byte(instruction.storage_target_address)
        print(f"\t\t__add instruction puts ({instruction.operands[0]:04x} + {instruction.operands[1]:04x}) into {result_storage_target:04x}")
        
        # update address of next instruction based on if there was a store byte or branch byte
        associated_routine.next_instruction_offset = instruction.storage_target_address + 1

        self.store_result(instruction.operands[0] + instruction.operands[1], result_storage_target, associated_routine)