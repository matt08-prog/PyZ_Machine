# interpreter.py
from hex_extractor import HexExtractor
from instruction import Instruction
from routine import Routine

def binary_to_signed_int(binary_str): # should be moved to global variable file with helper functions
    # Remove any spaces from the binary string
    binary_str = binary_str.replace(" ", "")
    
    # Get the length of the binary string
    num_bits = len(binary_str)
    
    # Convert to integer
    num = int(binary_str, 2)
    
    # If the leftmost bit is 1, it's a negative number in two's complement
    if num & (1 << (num_bits - 1)):
        num -= 1 << num_bits
    
    return num

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
        self.opcode_table = {0xe0: self.op_code__call, 0x54: self.op_code__add, 0x74: self.op_code__add, 0x61: self.op_code_jump_if_equal}
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
        self.run_routine(starting_routine) # This starting routine should never return a value
    
    def run_routine(self, routine):
        while self.debug_instruction_index < 5:
            self.debug_instruction_index += 1
            next_instruction = routine.read_next_instruction()
            print(f"\troutine's next instruction address: {routine.next_instruction_offset:02x}")
            print(f"\tnumber of local vars: {routine.num_local_vars}")
            print(f"\tinstruction_form: {self.debug_instruction_from_dict[next_instruction.instruction_form]}")
            print(f"\tnum_ops: {next_instruction.num_ops}")
            print(f"\topcode: {next_instruction.opcode}")
            print(f"\toperand_types: {next_instruction.operand_types}")
            print(f"\taddress_of_store_target (if it exists): {next_instruction.storage_target_address:02x}")
            print(f"\taddress_of_branch_target (if it exists): {next_instruction.branch_target_address:02x}")
            self.interpret_instruction(next_instruction, routine)
            if routine.should_return:
                if routine.return_value in [True, False]:
                    break
                else:
                    raise Exception("routine returned a non True/False value")
        return routine.return_value # Routine returned with a true of a false

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
        # result_storage_target = self.extractor.read_byte(instruction.storage_target_address)
        called_routine = Routine(self.extractor, routine_to_call, operands_to_pass_on, self)

        # update address of next instruction based on if there was a store byte or branch byte
        associated_routine.next_instruction_offset = instruction.storage_target_address + 1

        # self.store_result(self.run_routine(called_routine), result_storage_target, associated_routine)
        self.store_result(self.run_routine(called_routine), instruction.storage_target, associated_routine)

    def op_code__add(self, instruction, associated_routine):
        result_storage_target = self.extractor.read_byte(instruction.storage_target_address)
        print(f"\t\t__add instruction puts ({instruction.operands[0]:04x} + {instruction.operands[1]:04x}) into {result_storage_target:04x}")
        
        # update address of next instruction based on if there was a store byte or branch byte
        associated_routine.next_instruction_offset = instruction.storage_target_address + 1

        self.store_result(instruction.operands[0] + instruction.operands[1], result_storage_target, associated_routine)

    def op_code_jump_if_equal(self, instruction, associated_routine):
        branch_info_num_bytes = (0b01000000 & instruction.storage_target == 0) + 1
        invert_branch_condition = (0b10000000 & instruction.storage_target == 0)
        address_after_last_branch_info_byte = instruction.storage_target_address + branch_info_num_bytes
        branch_offset = -1

        will_return = False
        will_branch = False

        print(f"branch_info_num_bytes: {branch_info_num_bytes}")
        test_condition = (instruction.operands[0] == instruction.operands[1])
        if (test_condition and not invert_branch_condition) or (not test_condition and invert_branch_condition):
            if branch_info_num_bytes == 1:
                branch_offset = 0b00111111 & instruction.storage_target # first byte after list of operands
            elif branch_info_num_bytes == 2:
                unsigned_branch_offset = ((0b00111111 & instruction.storage_target) << 8) | (instruction.branch_target)
                branch_offset = binary_to_signed_int(bin(unsigned_branch_offset)[2:])# treat value as signed
            else:
                raise Exception("branch info num bytes not between 1 and 2")

            if branch_offset == 0:
                associated_routine.return_value = False
                associated_routine.should_return = True
                will_return = True
            elif branch_offset == 1:
                associated_routine.return_value = True
                associated_routine.should_return = True
                will_return = True
            else:
                will_branch = True
                associated_routine.next_instruction_offset = address_after_last_branch_info_byte + branch_offset - 2
        else:
            associated_routine.next_instruction_offset = address_after_last_branch_info_byte
        if branch_info_num_bytes == 1:
            print(f"branch info byte: {instruction.storage_target:02x}")
        else:
            print(f"branch info bytes: {((instruction.storage_target<<8) | instruction.branch_target):04x}")

        print(f"num branch info bytes: {branch_info_num_bytes}")
        print(f"branch condition inverted: {invert_branch_condition}")
        print(f"test condition passed: {test_condition}")
        print(f"branch offset: {branch_offset}")
        print(f"result of branch calculation: {associated_routine.next_instruction_offset:05x}")
        print(f"Will branch: {will_branch}")
        print(f"Will return: {will_return}")
