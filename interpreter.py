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
    def __init__(self, extractor, header, max_time_step):
        self.extractor = extractor
        self.header = header
        self.max_time_step = max_time_step

        self.time_stamp = 0

        # this opcode table should actually call functions from a seperate op_code interpreter class
        self.opcode_table = {
            0xe0: self.op_code__call, 

            0x54: self.op_code__add, 
            0x74: self.op_code__add, 

            0x61: self.op_code_jump_if_equal,

            0x4F: self.op_code__load_word
            }
        
        self.stack = []
        self.global_vars = [0x00] * 240

        self.debug_instruction_index = 0
        self.debug_instruction_form_dict = {0: "short", 1: "long", 2: "variable"}
        # self.operand_types_dict = {2: "Large Constant (2 bytes)", 1: "Small (1 byte)", -1: "Variable (1 byte)"}
        self.operand_types_dict = {2: "L", 1: "S", -1: "Var"}
        # print(f"{bcolors.WARNING}Original contents of global vars: {self.global_vars}{bcolors.ENDC}")
        # print(f"\t\t{bcolors.WARNING}{self.global_vars}{bcolors.ENDC}")


    def start_interpreting(self):
        starting_routine_address_from_header = self.header.initial_execution_point - 1
        starting_routine = Routine(self.extractor, starting_routine_address_from_header, [], self)
        print(f"first routine's address: {starting_routine_address_from_header}")
        print(f"routine's local vars: {starting_routine.local_vars}")
        self.run_routine(starting_routine) # This starting routine should never return a value
    
    def run_routine(self, routine):
        # print(f"number of local vars: {routine.num_local_vars}")
        print(f"routine's local vars: {list(map(hex, routine.local_vars))}")
        while True:
            self.time_stamp += 1
            if self.time_stamp >= self.max_time_step:
                # debug exit, otherwise it tries to return from all routines at end of simulation
                exit(-1)
            next_instruction = routine.read_next_instruction()
            print(f"time-{self.time_stamp} routine's next instruction address: {routine.next_instruction_offset:02x}")
            print(f"\tinstruction_form: {self.debug_instruction_form_dict[next_instruction.instruction_form]}")
            # print(f"\tnum_ops: {next_instruction.num_ops}")
            # print(f"\topcode: {next_instruction.opcode}")
            print(f"\toperand_types: [", end="")
            for operand_index in range(len(next_instruction.operand_types)):
                end_string = ", " if operand_index != len(next_instruction.operand_types) - 1 else "]\n" 
                print(f"{self.operand_types_dict[next_instruction.operand_types[operand_index]]}" , end=end_string)
            print(f"\toriginal operands: {next_instruction.debug_operands}")
            print(f"\t         operands: {list(map(hex, next_instruction.operands))}")
            # print(f"\taddress_of_store_target (if it exists): {next_instruction.storage_target_address:02x}")
            # print(f"\taddress_of_branch_target (if it exists): {next_instruction.branch_target_address:02x}")
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
            print(f"\t\t{bcolors.OKGREEN}Pushed {result_to_store:02x} onto the stack{bcolors.ENDC}")

        elif (storage_target > 0x00 and storage_target < 0x10): # 0x01 to 0xf0 are meant for local vars
            current_routine.local_vars[storage_target - 1] = result_to_store
            print(f"\t\t{bcolors.OKGREEN}{result_to_store:02x} placed in local var {storage_target - 1}{bcolors.ENDC}")

        elif (storage_target > 0x0f and storage_target < 0x100): # 0x10 to 0xff are meant for global_vars
            self.global_vars[storage_target - 0x10] = result_to_store
            print(f"\t\t{bcolors.OKGREEN}{result_to_store:02x} placed in global var {storage_target - 0x10}{bcolors.ENDC}")

    def op_code__call(self, instruction, associated_routine):
        routine_to_call = instruction.operands[0] * 2
        print(f"\t\t{bcolors.WARNING}__call instruction calls routine ({routine_to_call:05x}){bcolors.ENDC}")

        operands_to_pass_on = instruction.operands[1:]
        # result_storage_target = self.extractor.read_byte(instruction.storage_target_address)
        called_routine = Routine(self.extractor, routine_to_call, operands_to_pass_on, self)

        # update address of next instruction based on if there was a store byte or branch byte
        associated_routine.next_instruction_offset = instruction.storage_target_address + 1

        # self.store_result(self.run_routine(called_routine), result_storage_target, associated_routine)
        self.store_result(self.run_routine(called_routine), instruction.storage_target, associated_routine)

    def op_code__add(self, instruction, associated_routine):
        result_storage_target = self.extractor.read_byte(instruction.storage_target_address)
        print(f"\t\t{bcolors.WARNING}__add instruction puts ({instruction.operands[0]:04x} + {instruction.operands[1]:04x}) into {result_storage_target:04x}{bcolors.ENDC}")
        
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
                print(f"\t\t{bcolors.WARNING}__Jump_if_equal returns True{bcolors.ENDC}")
            elif branch_offset == 1:
                associated_routine.return_value = True
                associated_routine.should_return = True
                will_return = True
                print(f"\t\t{bcolors.WARNING}__Jump_if_equal returns false{bcolors.ENDC}")
            else:
                will_branch = True
                associated_routine.next_instruction_offset = address_after_last_branch_info_byte + branch_offset - 2
                print(f"\t\t{bcolors.WARNING}__Jump_if_equal branches to {associated_routine.next_instruction_offset}{bcolors.ENDC}")
        else:
            associated_routine.next_instruction_offset = address_after_last_branch_info_byte
        
        # Debug info:
        if branch_info_num_bytes == 1:
            print(f"\t\tbranch info byte: {instruction.storage_target:02x}")
        else:
            print(f"\t\tbranch info bytes: {((instruction.storage_target<<8) | instruction.branch_target):04x}")
        print(f"\t\tbranch condition inverted: {invert_branch_condition}")
        print(f"\t\ttest condition passed: {test_condition}")
        print(f"\t\tbranch offset: {branch_offset}")
        print(f"\t\tWill branch: {will_branch}")
        print(f"\t\tWill return: {will_return}")

    def op_code__load_word(self, instruction, associated_routine):
        # operand 0 is the start of array and operand 1 is the index of the array
        result_to_store = instruction.operands[0] + 2 * instruction.operands[1]
        self.store_result(result_to_store, instruction.storage_target, associated_routine)
        print(f"\t\t{bcolors.WARNING}__load_word loaded {result_to_store:02x} into {instruction.storage_target:02x}{bcolors.ENDC}")
        associated_routine.next_instruction_offset = instruction.storage_target_address + 1