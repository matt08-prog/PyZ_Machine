# instruction_interpreter.py
from hex_extractor import HexExtractor
from instruction import Instruction
from routine import Routine

def binary_to_signed_int(binary_value): # should be moved to global variable file with helper functions
    print(f"\t\t\t binary value: {binary_value}")
    binary_str = bin(binary_value)
    if binary_str[0] == "-":
        return binary_value
    else:
        binary_str = binary_str[2:]

    # Remove any spaces from the binary string
    binary_str = binary_str.replace(" ", "")
    
    print(f"\t\t\t binary string: {binary_str}")
    # Get the length of the binary string
    num_bits = len(binary_str)
    
    # Convert to integer
    num = int(binary_str, 2)
    
    # If the leftmost bit is 1, it's a negative number in two's complement
    if num & (1 << (num_bits - 1)):
        # The only time we should ever get here is if this is the first time the interpreter is looking at this value
        num -= 1 << num_bits
    
    return num

def add_16bit_signed(a, b):
    # Ensure inputs are within 16-bit signed range
    a = a & 0xFFFF
    b = b & 0xFFFF
    
    # Perform addition
    result = (a + b) & 0xFFFF
    
    # Handle sign extension
    if result & 0x8000:
        result = result - 0x10000
    
    return result

def sub_16bit_signed(a, b):
    # Ensure inputs are within 16-bit signed range
    a = a & 0xFFFF
    b = b & 0xFFFF
    
    # Perform addition
    result = (a - b) & 0xFFFF
    
    # Handle sign extension
    if result & 0x8000:
        result = result - 0x10000
    
    return result

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


class InstructionInterpreter:
    def __init__(self, extractor, header, routine_interpreter):
        self.extractor = extractor
        self.header = header
        self.routine_interpreter = routine_interpreter

        self.time_stamp = 0

        # this opcode table should actually call functions from a seperate op_code interpreter class
        self.opcode_table = {
            0xe0: self.op_code__call, 

            0x54: self.op_code__add, 
            0x74: self.op_code__add,

            0x55: self.op_cod__sub,

            0xa0: self.op_code__jump_if_zero,

            0x61: self.op_code__jump_if_equal,

            0x8c: self.op_code__jump,

            0x4F: self.op_code__load_word,

            0xe1: self.op_code__store_word
            }
        

    def interpret_instruction(self, instruction: Instruction, associated_routine: Routine):
        if instruction.full_opcode not in self.opcode_table.keys():
            print(f"{bcolors.FAIL}opcode ({instruction.full_opcode:02x}) not yet implemented{bcolors.ENDC}")
            exit(-1)
        self.opcode_table[instruction.full_opcode](instruction, associated_routine)











    def op_code__call(self, instruction, associated_routine):
        routine_to_call = instruction.operands[0] * 2
        print(f"\t\t{bcolors.WARNING}__call instruction calls routine ({routine_to_call:05x}){bcolors.ENDC}")

        operands_to_pass_on = instruction.operands[1:]
        # result_storage_target = self.extractor.read_byte(instruction.storage_target_address)
        called_routine = Routine(self.extractor, routine_to_call, operands_to_pass_on, self.routine_interpreter)

        # update address of next instruction based on if there was a store byte or branch byte
        associated_routine.next_instruction_offset = instruction.storage_target_address + 1

        # self.store_result(self.run_routine(called_routine), result_storage_target, associated_routine)
        self.routine_interpreter.store_result(self.routine_interpreter.run_routine(called_routine), instruction.storage_target, associated_routine)

    def op_code__add(self, instruction, associated_routine):
        result_storage_target = self.extractor.read_byte(instruction.storage_target_address)
        
        # update address of next instruction based on if there was a store byte or branch byte
        associated_routine.next_instruction_offset = instruction.storage_target_address + 1

        augend = instruction.operands[0]
        addend = instruction.operands[1]
        # sum = (augend + addend) & 0xFFFF


        sum = add_16bit_signed(augend, addend)

        self.routine_interpreter.store_result(sum, result_storage_target, associated_routine)
        print(f"\t\t{bcolors.WARNING}__add instruction puts {augend:04x} + {addend:04x} = {sum:04x} into {result_storage_target:04x}{bcolors.ENDC}")

    def op_cod__sub(self, instruction, associated_routine):
        result_storage_target = self.extractor.read_byte(instruction.storage_target_address)
        
        # update address of next instruction based on if there was a store byte or branch byte
        associated_routine.next_instruction_offset = instruction.storage_target_address + 1

        minuend = instruction.operands[0]
        subtrahend = instruction.operands[1]
        # difference = (minuend - subtrahend) & 0xFF

        difference = sub_16bit_signed(minuend, subtrahend)

        self.routine_interpreter.store_result(difference, result_storage_target, associated_routine)
        print(f"\t\t{bcolors.WARNING}__sub instruction puts {minuend:04x} - {subtrahend:04x} = {difference:04x} into {result_storage_target:04x}{bcolors.ENDC}")


    def op_code__jump_if_equal(self, instruction, associated_routine):
        if len(instruction.operands) > 2 or len(instruction.operands) < 2:
            print(f"{bcolors.FAIL}op_code__jump_if_equal expected 2 operands but got {len(instruction.operands)}{bcolors.ENDC}")
            exit(-1)
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
                branch_offset = binary_to_signed_int(unsigned_branch_offset)# treat value as signed
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
                print(f"\t\t{bcolors.WARNING}__Jump_if_equal branches to {associated_routine.next_instruction_offset:05x}{bcolors.ENDC}")
        else:
            # update address of next instruction
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

    def op_code__jump_if_zero(self, instruction, associated_routine):
        branch_info_num_bytes = (0b01000000 & instruction.storage_target == 0) + 1
        invert_branch_condition = (0b10000000 & instruction.storage_target == 0)
        address_after_last_branch_info_byte = instruction.storage_target_address + branch_info_num_bytes
        branch_offset = -1

        will_return = False
        will_branch = False

        test_condition = (instruction.operands[0] == 0)
        if (test_condition and not invert_branch_condition) or (not test_condition and invert_branch_condition):
            if branch_info_num_bytes == 1:
                branch_offset = 0b00111111 & instruction.storage_target # first byte after list of operands
            elif branch_info_num_bytes == 2:
                unsigned_branch_offset = ((0b00111111 & instruction.storage_target) << 8) | (instruction.branch_target)
                branch_offset = binary_to_signed_int(unsigned_branch_offset)# treat value as signed
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
                print(f"\t\t{bcolors.WARNING}__Jump_if_equal branches to {associated_routine.next_instruction_offset:05x}{bcolors.ENDC}")
        else:
            # update address of next instruction
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

    def op_code__jump(self, instruction, associated_routine):
        unsigned_branch_offset = instruction.operands[0] - 2
        signed_branch_offset = binary_to_signed_int(unsigned_branch_offset)

        # update address of next instruction
        associated_routine.next_instruction_offset = instruction.storage_target_address + signed_branch_offset
        
        print(f"\t\t{bcolors.WARNING}__Jump unconditional jumped to {associated_routine.next_instruction_offset:05x}{bcolors.ENDC}")

    # Puts whatever value is at array[word-index*2] into the given target
    def op_code__load_word(self, instruction, associated_routine):
        # operand 0 is the start of array and operand 1 is the index of the array
        result_to_store = instruction.operands[0] + 2 * instruction.operands[1]
        self.routine_interpreter.store_result(result_to_store, instruction.storage_target, associated_routine)
        print(f"\t\t{bcolors.WARNING}__load_word loaded {result_to_store:02x} into {instruction.storage_target:02x}{bcolors.ENDC}")
        associated_routine.next_instruction_offset = instruction.storage_target_address + 1

    # Writes "value" to dynamic_memory[array[2*word-index]]
    def op_code__store_word(self, instruction, associated_routine):
        if len(instruction.operands) > 3 or len(instruction.operands) < 3:
            print(f"{bcolors.FAIL}op_code__store_word expected 3 operands but got {len(instruction.operands)}{bcolors.ENDC}")
            exit(-1)

        result_to_store = instruction.operands[2]
        # operand 0 is the start of array and operand 1 is the index of the array
        dynamic_address_to_store_word_at = instruction.operands[0] + 2 * instruction.operands[1]

        # error checking
        if dynamic_address_to_store_word_at > self.header.start_of_static_memory:
            print(f"{bcolors.FAIL}op_code__store_word attempted to store a word at ({dynamic_address_to_store_word_at:05x}) which is past the end of dynamic memory ({self.header.start_of_static_memory:05x}){bcolors.ENDC}")
            exit(-1)


        self.extractor.write_word(dynamic_address_to_store_word_at, result_to_store)
        print(f"\t\t{bcolors.WARNING}__store_word stored {result_to_store:02x} into {dynamic_address_to_store_word_at:05x}{bcolors.ENDC}")
        associated_routine.next_instruction_offset = instruction.storage_target_address
