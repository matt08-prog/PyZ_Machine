# instruction_interpreter.py
import os
import threading
from hex_extractor import HexExtractor
from instruction import Instruction
from routine import Routine
from debuger import Debug
from unicodedata import normalize
import random
import time

debugger = Debug()

def debug(debug_string, severity_string="unclassified_severity", end_string="\n"):
    debugger.debug(debug_string, severity_string, end_string)

 # should be moved to global variable file with helper functions
 #      should also be merged with two functions below it into one function that lets you specify the number of bits
def binary_word_16_bits_to_signed_int(binary_value):
    debug(f"\t\t\tbinary_to_signed_int", "debug")
    debug(f"\t\t\t binary value: {binary_value}", "debug")
    binary_str = bin(binary_value)
    if binary_str[0] == "-":
        return binary_value
    else:
        binary_str = binary_str[2:]

    # Remove any spaces from the binary string
    binary_str = binary_str.replace(" ", "")
    
    debug(f"\t\t\t binary string: {binary_str}", "debug")
    # Get the length of the binary string
    num_bits = 16
    
    # Convert to integer
    num = int(binary_str, 2)
    
    # If the leftmost bit is 1, it's a negative number in two's complement
    if num & (1 << (num_bits - 1)):
        # The only time we should ever get here is if this is the first time the interpreter is looking at this value
        num -= 1 << num_bits
    debug(f"\t\t\tfinal value: {num:016b}", "debug")
    return num

def binary_14_bits_to_signed_int(binary_value): # should be moved to global variable file with helper functions
    # debug(f"\t\t\tbinary_to_signed_int")
    # debug(f"\t\t\t binary value: {binary_value}")
    binary_str = bin(binary_value)
    if binary_str[0] == "-":
        return binary_value
    else:
        binary_str = binary_str[2:]

    # Remove any spaces from the binary string
    binary_str = binary_str.replace(" ", "")
    
    # debug(f"\t\t\t binary string: {binary_str}")
    # Get the length of the binary string
    num_bits = 14
    
    # Convert to integer
    num = int(binary_str, 2)
    
    # If the leftmost bit is 1, it's a negative number in two's complement
    if num & (1 << (num_bits - 1)):
        # The only time we should ever get here is if this is the first time the interpreter is looking at this value
        num -= 1 << num_bits
    # debug(f"\t\t\tfinal value: {num}")
    return num


def byte_to_signed_int(binary_value): # should be moved to global variable file with helper functions
    # debug(f"\t\t\tbinary_to_signed_int")
    # debug(f"\t\t\t binary value: {binary_value}")
    binary_str = bin(binary_value)
    if binary_str[0] == "-":
        return binary_value
    else:
        binary_str = binary_str[2:]

    # Remove any spaces from the binary string
    binary_str = binary_str.replace(" ", "")
    
    # debug(f"\t\t\t binary string: {binary_str}")
    # Get the length of the binary string
    num_bits = 14
    
    # Convert to integer
    num = int(binary_str, 2)
    
    # If the leftmost bit is 1, it's a negative number in two's complement
    if num & (1 << (num_bits - 1)):
        # The only time we should ever get here is if this is the first time the interpreter is looking at this value
        num -= 1 << num_bits
    # debug(f"\t\t\tfinal value: {num}")
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

def mul_16bit_signed(a, b):
    # Ensure inputs are within 16-bit signed range
    a = a & 0xFFFF
    b = b & 0xFFFF
    
    # Perform addition
    result = (a * b) & 0xFFFF
    
    # Handle sign extension
    if result & 0x8000:
        result = result - 0x10000
    
    return result

def div_16bit_signed(a, b):
    # Ensure inputs are within 16-bit signed range
    a = a & 0xFFFF
    b = b & 0xFFFF
    
    # Perform addition
    result = int(a / b) & 0xFFFF
    
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

    def __init__(self, extractor, header, routine_interpreter, object_loader, abreviator, user_input):
        self.debugger = Debug()
        self.extractor = extractor
        self.header = header
        self.routine_interpreter = routine_interpreter
        self.object_loader = object_loader
        self.abreviator = abreviator
        self.user_input = user_input

        self.time_stamp = 0

        self.global_index = 0
        self.should_get_user_input = True


        # this opcode table should actually call functions from a seperate op_code interpreter class
        self.opcode_table = {
            0xe0: self.op_code__call, 

            0x14: self.op_code__add, 
            0x34: self.op_code__add, 
            0x54: self.op_code__add, 
            0x74: self.op_code__add, 
            0xd4: self.op_code__add,

            0x15: self.op_cod__sub,
            0x35: self.op_cod__sub,
            0x55: self.op_cod__sub,
            0x75: self.op_cod__sub,
            0xd5: self.op_cod__sub,

            0x56: self.op_cod__mul,
            0x36: self.op_cod__mul,

            0x17: self.op_cod__div,
            0x37: self.op_cod__div,
            0x57: self.op_cod__div,
            0x77: self.op_cod__div,
            0xd7: self.op_cod__div,

            0x95: self.op_code__increment,

            0xc9: self.op_code__and,
            0x49: self.op_code__and,

            0x07: self.op_code__test_bitmap_against_flags,
            0x27: self.op_code__test_bitmap_against_flags,
            0x47: self.op_code__test_bitmap_against_flags,
            0x67: self.op_code__test_bitmap_against_flags,
            0xc7: self.op_code__test_bitmap_against_flags,

            0xa0: self.op_code__jump_if_zero,
            0xc1: self.op_code__jump_if_equal,
            0x21: self.op_code__jump_if_equal,
            0x41: self.op_code__jump_if_equal,
            0x61: self.op_code__jump_if_equal,
            0x42: self.op_code__jump_if_less_than,
            0x23: self.op_code__jump_if_greater_than,
            0x43: self.op_code__jump_if_greater_than,
            0x63: self.op_code__jump_if_greater_than,
            0xc3: self.op_code__jump_if_greater_than,
            0x05: self.op_code__increment_and_check,
            0x25: self.op_code__increment_and_check,
            0x04: self.op_code__decrement_and_check,
            0x8c: self.op_code__jump,

            0x10: self.op_code__load_byte,
            0x30: self.op_code__load_byte,
            0x50: self.op_code__load_byte,
            0x70: self.op_code__load_byte,
            0x4F: self.op_code__load_word,
            0x0F: self.op_code__load_word,
            0x6F: self.op_code__load_word,
            0xe1: self.op_code__store_word,
            0xe2: self.op_code__store_byte,
            0xe8: self.op_code__push_value_to_stack,

            0x0d: self.op_code__store,
            0x2d: self.op_code__store,
            0x4d: self.op_code__store,
            0x6d: self.op_code__store,
            0xcd: self.op_code__store,

            0x8e: self.op_code__load,
            0x9e: self.op_code__load,
            0xae: self.op_code__load,

            0x26: self.op_code__jump_if_object_a_is_direct_child_of_object_b,
            0x46: self.op_code__jump_if_object_a_is_direct_child_of_object_b,
            0x66: self.op_code__jump_if_object_a_is_direct_child_of_object_b,

            0x0a: self.op_code__test_attribute,
            0x4a: self.op_code__test_attribute,
            0x0b: self.op_code__set_attribute,
            0x4b: self.op_code__set_attribute,
            0x0c: self.op_code__clear_attribute,
            0x4c: self.op_code__clear_attribute,

            0xe3: self.op_code__put_prop,
            0x51: self.op_code__get_property,
            0x12: self.op_code__get_address_of_property,
            0x32: self.op_code__get_address_of_property,
            0x52: self.op_code__get_address_of_property,
            0x72: self.op_code__get_address_of_property,
            0xd2: self.op_code__get_address_of_property,
            0xa1: self.op_code__get_sibling_of_object,
            0x92: self.op_code__get_child_of_object,
            0xa2: self.op_code__get_child_of_object,
            0x93: self.op_code__get_parent_of_object,
            0xa3: self.op_code__get_parent_of_object,
            0xa4: self.op_code__get_length_of_property,

            0x2e: self.op_code__add_object,
            0x6e: self.op_code__add_object,

            0xab: self.op_code__return,
            0x8b: self.op_code__return,
            0x9b: self.op_code__return,
            0xb0: self.op_code__return_true,
            0xb1: self.op_code__return_false,
            0xb8: self.op_code__return_popped_top_of_stack,

            0xb2: self.op_code__print,
            0xb3: self.op_code__print_then_return_true,
            0xe5: self.op_code__print_char,
            0xe6: self.op_code__print_num,
            0xad: self.op_code__print_string_at_packed_address,
            0xbb: self.op_code__new_line,
            0xaa: self.op_code__print_object,

            0xe4: self.op_code__read_line_of_user_input,
            0xe7: self.op_code__random,
            }

    def interpret_instruction(self, instruction: Instruction, associated_routine: Routine):
        if instruction.full_opcode not in self.opcode_table.keys():
            debug(f"opcode ({instruction.full_opcode:02x}) not yet implemented", "scroll")
            print(f"opcode ({instruction.full_opcode:02x}) not yet implemented")
            exit(-1)
        self.opcode_table[instruction.full_opcode](instruction, associated_routine)











    def op_code__call(self, instruction, associated_routine):
        routine_to_call = instruction.operands[0] * 2

        operands_to_pass_on = instruction.operands[1:]
        if routine_to_call != 0:
            debug(f"\t\t__call instruction calls routine ({routine_to_call:05x}), with operands ({operands_to_pass_on})", "WARNING")
            called_routine = Routine(self.extractor, routine_to_call, operands_to_pass_on, self.routine_interpreter)
            # update address of next instruction based on if there was a store byte or branch byte
            associated_routine.next_instruction_offset = instruction.storage_target_address + 1
            self.routine_interpreter.store_result(self.routine_interpreter.run_routine(called_routine), instruction.storage_target, associated_routine)
        else:
            debug(f"\t\t__call instruction returns False", "WARNING")
            # associated_routine.should_return = True
            associated_routine.return_value = False
            associated_routine.next_instruction_offset = instruction.branch_target_address
        # self.branch_if_test_condition_passes(instruction, associated_routine, True, False, "__call")

        # self.store_result(self.run_routine(called_routine), result_storage_target, associated_routine)

    def op_code__add(self, instruction, associated_routine):
        result_storage_target = self.extractor.read_byte(instruction.storage_target_address)
        
        # update address of next instruction based on if there was a store byte or branch byte
        associated_routine.next_instruction_offset = instruction.storage_target_address + 1

        augend = instruction.operands[0]
        addend = instruction.operands[1]
        # sum = (augend + addend) & 0xFFFF


        sum = add_16bit_signed(augend, addend)

        self.routine_interpreter.store_result(sum, result_storage_target, associated_routine)
        debug(f"\t\t__add instruction puts {augend:04x} + {addend:04x} = {sum:04x} into {result_storage_target:04x}", "WARNING")

    def op_code__test_bitmap_against_flags(self, instruction, associated_routine):
        bitmap = instruction.operands[0]
        flags = instruction.operands[1]

        test_condition = ((bitmap & flags) == flags)

        self.branch_if_test_condition_passes(instruction, associated_routine, test_condition, False, "__test_bitmap_against_flags")

    def op_cod__sub(self, instruction, associated_routine):
        result_storage_target = self.extractor.read_byte(instruction.storage_target_address)
        
        # update address of next instruction based on if there was a store byte or branch byte
        associated_routine.next_instruction_offset = instruction.storage_target_address + 1

        minuend = instruction.operands[0]
        subtrahend = instruction.operands[1]
        # difference = (minuend - subtrahend) & 0xFF

        difference = sub_16bit_signed(minuend, subtrahend)

        self.routine_interpreter.store_result(difference, result_storage_target, associated_routine)
        debug(f"\t\t__sub instruction puts {minuend:04x} - {subtrahend:04x} = {difference:04x} into {result_storage_target:04x}", "WARNING")

    def op_cod__mul(self, instruction, associated_routine):
        result_storage_target = self.extractor.read_byte(instruction.storage_target_address)
        
        # update address of next instruction based on if there was a store byte or branch byte
        associated_routine.next_instruction_offset = instruction.storage_target_address + 1

        multiplier = instruction.operands[0]
        multiplicand = instruction.operands[1]
        # difference = (minuend - subtrahend) & 0xFF

        product = mul_16bit_signed(multiplier, multiplicand)

        self.routine_interpreter.store_result(product, result_storage_target, associated_routine)
        debug(f"\t\t__sub instruction puts {multiplier:04x} - {multiplicand:04x} = {product:04x} into {result_storage_target:04x}", "WARNING")
    
    def op_cod__div(self, instruction, associated_routine):
        result_storage_target = self.extractor.read_byte(instruction.storage_target_address)
        
        # update address of next instruction based on if there was a store byte or branch byte
        associated_routine.next_instruction_offset = instruction.storage_target_address + 1

        dividend = instruction.operands[0]
        divisor = instruction.operands[1]

        if divisor == 0:
            print("__div performed division by zero, now exiting")
            os.exit(-1)

        quotient = div_16bit_signed(dividend, divisor)

        self.routine_interpreter.store_result(quotient, result_storage_target, associated_routine)
        debug(f"\t\t__div instruction puts {dividend:04x} - {divisor:04x} = {quotient:04x} into {result_storage_target:04x}", "WARNING")

    def op_code__increment(self, instruction, associated_routine):
        variable_address = instruction.operands[0]
        variable_value = 0x0000
        
        if instruction.operand_types[0] != -1: # if the first operand was not a variable, it should be treated as one
            variable_value = instruction.load_variable(variable_address)
        else:
            # The first operand was already treated like a variable
            variable_address = instruction.original_operands[0]
            variable_value = instruction.operands[0]

        incremented_variable_value = add_16bit_signed(variable_value, 1)

        self.routine_interpreter.store_result(incremented_variable_value, variable_address, associated_routine)

        associated_routine.next_instruction_offset = instruction.storage_target_address
        debug(f"\t\t__increment incremented {variable_address:02x} from {variable_value:02x} to {incremented_variable_value:02x}", "WARNING")

    def op_code__and (self, instruction, associated_routine):
        result_to_store = instruction.operands[0] & instruction.operands[1]

        self.routine_interpreter.store_result(result_to_store, instruction.storage_target, associated_routine)
        associated_routine.next_instruction_offset = instruction.branch_target_address
        debug(f"\t\top_code__and placed result ({instruction.operands[0]:04x} & {instruction.operands[1]:04x} = {result_to_store:04x} ({result_to_store})) in address {instruction.storage_target:05x}", "WARNING")

    def op_code__jump_if_equal(self, instruction, associated_routine):
        # if len(instruction.operands) > 3 or len(instruction.operands) < 2:
        #     debug(f"op_code__jump_if_equal expected 2 or 3 operands but got {len(instruction.operands)}", "FAIL")
        #     exit(-1)
        branch_info_num_bytes = (0b01000000 & instruction.storage_target == 0) + 1
        invert_branch_condition = (0b10000000 & instruction.storage_target == 0)
        address_after_last_branch_info_byte = instruction.storage_target_address + branch_info_num_bytes
        branch_offset = -1

        will_return = False
        will_branch = False

        # test_condition = (instruction.operands[0] == instruction.operands[1]) or (instruction.operands[0] == instruction.operands[-1])
        test_condition = instruction.operands[0] in instruction.operands[1:]
        if (test_condition and not invert_branch_condition) or (not test_condition and invert_branch_condition):
            if branch_info_num_bytes == 1:
                branch_offset = 0b00111111 & instruction.storage_target # first byte after list of operands
            elif branch_info_num_bytes == 2:
                unsigned_branch_offset = ((0b00111111 & instruction.storage_target) << 8) | (instruction.branch_target)
                branch_offset = binary_14_bits_to_signed_int(unsigned_branch_offset)# treat value as signed
            else:
                raise Exception("branch info num bytes not between 1 and 2")

            if branch_offset == 0:
                associated_routine.return_value = False
                associated_routine.should_return = True
                will_return = True
                debug(f"\t\t__Jump_if_equal returns False", "WARNING")
            elif branch_offset == 1:
                associated_routine.return_value = True
                associated_routine.should_return = True
                will_return = True
                debug(f"\t\t__Jump_if_equal returns True", "WARNING")
            else:
                will_branch = True
                associated_routine.next_instruction_offset = address_after_last_branch_info_byte + branch_offset - 2
                debug(f"\t\t__Jump_if_equal branches to {associated_routine.next_instruction_offset:05x}", "WARNING")
        else:
            # update address of next instruction
            associated_routine.next_instruction_offset = address_after_last_branch_info_byte
            debug(f"\t\t__Jump_if_equal does not branch", "WARNING")

        
        # Debug info:
        if branch_info_num_bytes == 1:
            debug(f"\t\tbranch info byte: {instruction.storage_target:02x}")
        else:
            debug(f"\t\tbranch info bytes: {((instruction.storage_target<<8) | instruction.branch_target):04x}")
        debug(f"\t\tbranch condition inverted: {invert_branch_condition}")
        debug(f"\t\ttest condition passed: {test_condition}")
        debug(f"\t\tbranch offset: {branch_offset}")
        debug(f"\t\tWill branch: {will_branch}")
        debug(f"\t\tWill return: {will_return}")

    def op_code__jump_if_less_than(self, instruction, associated_routine):
        if len(instruction.operands) > 2 or len(instruction.operands) < 2:
            debug(f"{bcolors.FAIL}op_code__jump_if_less_than expected 2 operands but got {len(instruction.operands)}")
            exit(-1)
        
        value_a = binary_word_16_bits_to_signed_int(instruction.operands[0])
        value_b = binary_word_16_bits_to_signed_int(instruction.operands[1])

        test_condition = (value_a < value_b)

        self.branch_if_test_condition_passes(instruction, associated_routine, test_condition, False, "__jump_if_less_than")

    def op_code__jump_if_greater_than(self, instruction, associated_routine):
        if len(instruction.operands) > 2 or len(instruction.operands) < 2:
            debug(f"{bcolors.FAIL}op_code__jump_if_greater_than expected 2 operands but got {len(instruction.operands)}")
            exit(-1)
        
        value_a = binary_word_16_bits_to_signed_int(instruction.operands[0])
        value_b = binary_word_16_bits_to_signed_int(instruction.operands[1])

        test_condition = (value_a > value_b)

        self.branch_if_test_condition_passes(instruction, associated_routine, test_condition, False, "__jump_if_greater_than")


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
                branch_offset = binary_14_bits_to_signed_int(unsigned_branch_offset)# treat value as signed
            else:
                raise Exception("branch info num bytes not between 1 and 2")

            if branch_offset == 0:
                associated_routine.return_value = False
                associated_routine.should_return = True
                will_return = True
                debug(f"\t\t__Jump_if_zero returns False", "WARNING")
            elif branch_offset == 1:
                associated_routine.return_value = True
                associated_routine.should_return = True
                will_return = True
                debug(f"\t\t__Jump_if_zero returns True", "WARNING")
            else:
                will_branch = True
                associated_routine.next_instruction_offset = address_after_last_branch_info_byte + branch_offset - 2
                debug(f"\t\t__Jump_if_zero branches to {associated_routine.next_instruction_offset:05x}", "WARNING")
        else:
            # update address of next instruction
            associated_routine.next_instruction_offset = address_after_last_branch_info_byte
            debug(f"\t\t__Jump_if_zero does not branch", "WARNING")
        
        # Debug info:
        if branch_info_num_bytes == 1:
            debug(f"\t\tbranch info byte: {instruction.storage_target:02x}")
        else:
            debug(f"\t\tbranch info bytes: {((instruction.storage_target<<8) | instruction.branch_target):04x}")
        debug(f"\t\tbranch condition inverted: {invert_branch_condition}")
        debug(f"\t\ttest condition passed: {test_condition}")
        debug(f"\t\tbranch offset: {branch_offset}")
        debug(f"\t\tWill branch: {will_branch}")
        debug(f"\t\tWill return: {will_return}")

    def op_code__jump(self, instruction, associated_routine):
        unsigned_branch_offset = instruction.operands[0]
        signed_branch_offset = binary_word_16_bits_to_signed_int(unsigned_branch_offset)

        # update address of next instruction
        debug(f"\t\t__Jump unconditional jumped to {(instruction.storage_target_address + signed_branch_offset - 2):05x} given an offset of {signed_branch_offset} - 2 = {signed_branch_offset - 2}", "WARNING")
        associated_routine.next_instruction_offset = instruction.storage_target_address + signed_branch_offset - 2
        

    # Puts whatever value is at array[word-index*2] into the given target
    def op_code__load_word(self, instruction, associated_routine):
        # operand 0 is the start of array and operand 1 is the index of the array
        address_to_fetch = instruction.operands[0] + 2 * instruction.operands[1]
        result_to_store = self.extractor.read_word(address_to_fetch)
        
        self.routine_interpreter.store_result(result_to_store, instruction.storage_target, associated_routine)
        debug(f"\t\t__load_word loaded 0x{result_to_store:02x} ({result_to_store}) from address {address_to_fetch:05x} into {instruction.storage_target:02x}", "WARNING")
        associated_routine.next_instruction_offset = instruction.storage_target_address + 1

    # Puts whatever value is at array[byte-index] into the given target
    def op_code__load_byte(self, instruction, associated_routine):
        # operand 0 is the start of array and operand 1 is the index of the array
        address_to_fetch = instruction.operands[0] + instruction.operands[1]
        result_to_store = self.extractor.read_byte(address_to_fetch)
        
        self.routine_interpreter.store_result(result_to_store, instruction.storage_target, associated_routine)
        debug(f"\t\t__load_byte loaded 0x{result_to_store:02x} ({result_to_store}) from address {address_to_fetch:05x} into {instruction.storage_target:02x}", "WARNING")
        associated_routine.next_instruction_offset = instruction.storage_target_address + 1

    # Writes "value" to dynamic_memory[array[2*word-index]]
    def op_code__store_word(self, instruction, associated_routine):
        if len(instruction.operands) > 3 or len(instruction.operands) < 3:
            debug(f"{bcolors.FAIL}op_code__store_word expected 3 operands but got {len(instruction.operands)}")
            exit(-1)

        result_to_store = instruction.operands[2]
        # operand 0 is the start of array and operand 1 is the index of the array
        dynamic_address_to_store_word_at = instruction.operands[0] + 2 * instruction.operands[1]

        # error checking
        if dynamic_address_to_store_word_at > self.header.start_of_static_memory:
            debug(f"{bcolors.FAIL}op_code__store_word attempted to store a word at ({dynamic_address_to_store_word_at:05x}) which is past the end of dynamic memory ({self.header.start_of_static_memory:05x})")
            exit(-1)


        self.extractor.write_word(dynamic_address_to_store_word_at, result_to_store)
        debug(f"\t\t__store_word stored {result_to_store:02x} into {dynamic_address_to_store_word_at:05x}", "WARNING")
        associated_routine.next_instruction_offset = instruction.storage_target_address

    def op_code__store_byte(self, instruction, associated_routine):
        if len(instruction.operands) > 3 or len(instruction.operands) < 3:
            debug(f"{bcolors.FAIL}op_code__store_word expected 3 operands but got {len(instruction.operands)}")
            exit(-1)

        result_to_store = instruction.operands[2]
        # operand 0 is the start of array and operand 1 is the index of the array
        dynamic_address_to_store_byte_at = instruction.operands[0] + instruction.operands[1]

        # error checking
        if dynamic_address_to_store_byte_at > self.header.start_of_static_memory:
            debug(f"{bcolors.FAIL}op_code__store_byte attempted to store a word at ({dynamic_address_to_store_byte_at:05x}) which is past the end of dynamic memory ({self.header.start_of_static_memory:05x})")
            exit(-1)

        self.extractor.write_byte(dynamic_address_to_store_byte_at, result_to_store)
        debug(f"\t\t__store_byte stored {result_to_store:02x} into {dynamic_address_to_store_byte_at:05x}", "WARNING")
        associated_routine.next_instruction_offset = instruction.storage_target_address

    def op_code__push_value_to_stack(self, instruction, associated_routine):
        value_to_store = instruction.operands[0]

        self.routine_interpreter.store_result(value_to_store, 0x00, associated_routine)
        debug(f"\t\t__push_value_to_stack pushed 0x{value_to_store:02x} to the stack", "WARNING")
        associated_routine.next_instruction_offset = instruction.storage_target_address

    def op_code__store(self, instruction, associated_routine):
        value_to_store = instruction.operands[1]
        variable_store_destination = instruction.operands[0]

        self.routine_interpreter.store_result(value_to_store, variable_store_destination, associated_routine)
        associated_routine.next_instruction_offset = instruction.storage_target_address
        debug(f"\t\t__store stored {value_to_store:02x} into {variable_store_destination:05x}", "WARNING")
    
    def op_code__load(self, instruction, associated_routine):
        value_to_store = instruction.operands[0]

        self.routine_interpreter.store_result(value_to_store, instruction.storage_target, associated_routine)
        associated_routine.next_instruction_offset = instruction.branch_target_address

    def op_code__put_prop(self, instruction, associated_routine):
        object_number = instruction.operands[0]
        property_number = instruction.operands[1]
        value = instruction.operands[2]

        self.object_loader.put_value_in_property(object_number, property_number, value)
        associated_routine.next_instruction_offset = instruction.storage_target_address
        debug(f"\t\t__put_prop placed property_number #{property_number} in object #{object_number}")
        if object_number == 64:
            pass


    def branch_if_test_condition_passes(self, instruction, associated_routine, test_condition, has_storage_target, op_code_name):
        # account for the few instructions which store a result and then possibly branch
        if has_storage_target:
            instruction.storage_target_address += 1
            instruction.branch_target_address += 1
            instruction.storage_target = self.extractor.read_byte(instruction.storage_target_address)
            instruction.branch_target = self.extractor.read_byte(instruction.branch_target_address)
        branch_info_num_bytes = (0b01000000 & instruction.storage_target == 0) + 1
        invert_branch_condition = (0b10000000 & instruction.storage_target == 0)
        address_after_last_branch_info_byte = instruction.storage_target_address + branch_info_num_bytes
        branch_offset = -1

        will_return = False
        will_branch = False

        # calculate branch offset before tesing branch_condition
        if branch_info_num_bytes == 1:
            branch_offset = 0b00111111 & instruction.storage_target # first byte after list of operands
        elif branch_info_num_bytes == 2:
            unsigned_branch_offset = ((0b00111111 & instruction.storage_target) << 8) | (instruction.branch_target)
            branch_offset = binary_14_bits_to_signed_int(unsigned_branch_offset)# treat value as signed
        else:
            raise Exception("branch info num bytes not between 1 and 2")
        
        if (test_condition and not invert_branch_condition) or (not test_condition and invert_branch_condition):

            if branch_offset == 0:
                associated_routine.return_value = False
                associated_routine.should_return = True
                will_return = True
                debug(f"\t\t{op_code_name} returns False", "WARNING")
            elif branch_offset == 1:
                associated_routine.return_value = True
                associated_routine.should_return = True
                will_return = True
                debug(f"\t\t{op_code_name} returns True", "WARNING")
            else:
                will_branch = True
                associated_routine.next_instruction_offset = address_after_last_branch_info_byte + branch_offset - 2
                debug(f"\t\t{op_code_name} jumped to {associated_routine.next_instruction_offset:05x}", "WARNING")
        else:
            # update address of next instruction
            associated_routine.next_instruction_offset = address_after_last_branch_info_byte
            debug(f"\t\t{op_code_name} does not branch", "WARNING")
        
        # Debug info:
        if branch_info_num_bytes == 1:
            debug(f"\t\tbranch info byte: {instruction.storage_target:02x}", "debug")
        else:
            debug(f"\t\tbranch info bytes: {((instruction.storage_target<<8) | instruction.branch_target):04x}", "debug")
        debug(f"\t\tbranch condition inverted: {invert_branch_condition}", "debug")
        debug(f"\t\ttest condition passed: {test_condition}", "debug")
        debug(f"\t\tbranch offset: {branch_offset}", "debug")
        debug(f"\t\tWill branch: {will_branch}", "debug")
        debug(f"\t\tWill return: {will_return}", "debug")


    def op_code__test_attribute(self, instruction, associated_routine):
        object_number = instruction.operands[0]
        attribute = instruction.operands[1]

        branch_info_num_bytes = (0b01000000 & instruction.storage_target == 0) + 1
        invert_branch_condition = (0b10000000 & instruction.storage_target == 0)
        address_after_last_branch_info_byte = instruction.storage_target_address + branch_info_num_bytes
        branch_offset = -1

        will_return = False
        will_branch = False

        test_condition = self.object_loader.test_attribute(object_number, attribute)
        debug(f"\t\t__test_attribute found that object #{object_number} does{"" if test_condition else " not"} have attribute #{attribute} ", "WARNING")
        if (test_condition and not invert_branch_condition) or (not test_condition and invert_branch_condition):
            if branch_info_num_bytes == 1:
                branch_offset = 0b00111111 & instruction.storage_target # first byte after list of operands
            elif branch_info_num_bytes == 2:
                unsigned_branch_offset = ((0b00111111 & instruction.storage_target) << 8) | (instruction.branch_target)
                branch_offset = binary_14_bits_to_signed_int(unsigned_branch_offset)# treat value as signed
            else:
                raise Exception("branch info num bytes not between 1 and 2")

            if branch_offset == 0:
                associated_routine.return_value = False
                associated_routine.should_return = True
                will_return = True
                debug(f"\t\t__test_attribute returns False", "WARNING")
            elif branch_offset == 1:
                associated_routine.return_value = True
                associated_routine.should_return = True
                will_return = True
                debug(f"\t\t__test_attribute returns True", "WARNING")
            else:
                will_branch = True
                associated_routine.next_instruction_offset = address_after_last_branch_info_byte + branch_offset - 2
                debug(f"\t\t__test_attribute jumped to {associated_routine.next_instruction_offset:05x}", "WARNING")
        else:
            # update address of next instruction
            associated_routine.next_instruction_offset = address_after_last_branch_info_byte
            debug(f"\t\t__test_attribute does not branch", "WARNING")
        
        # Debug info:
        if branch_info_num_bytes == 1:
            debug(f"\t\tbranch info byte: {instruction.storage_target:02x}", "debug")
        else:
            debug(f"\t\tbranch info bytes: {((instruction.storage_target<<8) | instruction.branch_target):04x}", "debug")
        debug(f"\t\tbranch condition inverted: {invert_branch_condition}", "debug")
        debug(f"\t\ttest condition passed: {test_condition}", "debug")
        debug(f"\t\tbranch offset: {branch_offset}", "debug")
        debug(f"\t\tWill branch: {will_branch}", "debug")
        debug(f"\t\tWill return: {will_return}", "debug")
    
    def op_code__set_attribute(self, instruction, associated_routine):
        object_number = instruction.operands[0]
        attribute = instruction.operands[1]
        self.object_loader.set_attribute(object_number, attribute)
        associated_routine.next_instruction_offset = instruction.storage_target_address
        debug(f"\t\t__set_attribute ensured object #{object_number} had attribute #{attribute}", "debug")
        # if object_number == 64:
        #     print(64)

    def op_code__get_property(self, instruction, associated_routine):
        object_number = instruction.operands[0]
        property_number = instruction.operands[1]
        property_data_array = self.object_loader.get_object_property_data(object_number, property_number)
        property_value = 0

        if len(property_data_array) == 1:
            property_value = property_data_array[0]
        else:
            property_value = (property_data_array[0] << 8) | property_data_array[1]

        storage_target = instruction.storage_target

        if (len(property_data_array) not in [1, 2]):
            debug(f"\t\t{bcolors.FAIL}property #{property_number} (whose value is {property_value} has an erroneous length of {len(property_value)})", "WARNING")
            exit(-1)

        debug(f"\t\t__get_property found object #{object_number} has property #{property_number} (whose value is 0x{property_value:04x} ({property_value}))", "WARNING")
        self.routine_interpreter.store_result(property_value, storage_target, associated_routine)
        associated_routine.next_instruction_offset = instruction.branch_target_address

    def op_code__get_address_of_property(self, instruction, associated_routine):
        object_number = instruction.operands[0]
        property_number = instruction.operands[1]
        property_address = self.object_loader.get_object_property_address(object_number, property_number)

        storage_target = instruction.storage_target

        debug(f"\t\t__get_address_of_property found object #{object_number} has property #{property_number} (whose address is 0x{property_address:04x} ({property_address}))", "WARNING")
        self.routine_interpreter.store_result(property_address, storage_target, associated_routine)
        associated_routine.next_instruction_offset = instruction.branch_target_address

    def op_code__get_length_of_property(self, instruction, associated_routine):
        property_address = instruction.operands[0]
        property_length = 0

        if property_address != 0:
            property_length = (self.extractor.read_byte(property_address - 1) >> 5) + 1

        storage_target = instruction.storage_target

        debug(f"\t\t__get_length_of_property found property at 0x{property_address:04x} has a length of {property_length} bytes", "WARNING")
        self.routine_interpreter.store_result(property_length, storage_target, associated_routine)
        associated_routine.next_instruction_offset = instruction.branch_target_address

    # Get next object in tree, branching if this exists, i.e. is not 0.
    def op_code__get_sibling_of_object(self, instruction, associated_routine):
        object_number = instruction.operands[0]
        sibling_object_number = self.object_loader.get_object_sibling(object_number)
        storage_target = instruction.storage_target
        self.routine_interpreter.store_result(sibling_object_number, storage_target, associated_routine)

        test_condition = (sibling_object_number != 0)
        if test_condition:
            debug(f"\t\t__get_sibling_of_object found object #{object_number} has sibling #{sibling_object_number}", "WARNING")
        self.branch_if_test_condition_passes(instruction, associated_routine, test_condition, True, "__get_sibling_of_object")

    # Get first object contained in given object, branching if this exists, i.e. is not nothing (i.e., is not 0).
    def op_code__get_child_of_object(self, instruction, associated_routine):
        object_number = instruction.operands[0]
        child_object_number = self.object_loader.get_object_child(object_number)
        storage_target = instruction.storage_target
        self.routine_interpreter.store_result(child_object_number, storage_target, associated_routine)

        test_condition = (child_object_number != 0)
        if test_condition:
            debug(f"\t\t__get_child_of_object found object #{object_number} has child #{child_object_number}", "WARNING")
        self.branch_if_test_condition_passes(instruction, associated_routine, test_condition, True, "__get_child_of_object")

    def op_code__get_parent_of_object(self, instruction, associated_routine):
        object_number = instruction.operands[0]
        parent_object_number = self.object_loader.get_object_parent(object_number)
        storage_target = instruction.storage_target
        self.routine_interpreter.store_result(parent_object_number, storage_target, associated_routine)
        associated_routine.next_instruction_offset = instruction.branch_target_address

        object_description = self.object_loader.get_object_description(object_number)
        if len(object_description) > 0:
            object_description = object_description[0]
        else:
            object_description = ""

        object_parent_description = self.object_loader.get_object_description(parent_object_number)
        if len(object_parent_description) > 0:
            object_parent_description = object_parent_description[0]
        else:
            object_parent_description = ""

        debug(f"\t\t__get_parent_of_object found object \"{object_description}\" (#{object_number}) has parent \"{object_parent_description}\" (#{parent_object_number})", "WARNING")
        pass

    def op_code__clear_attribute(self, instruction, associated_routine):
        object_number = instruction.operands[0]
        attribute = instruction.operands[1]
        self.object_loader.remove_attribute(object_number, attribute)
        associated_routine.next_instruction_offset = instruction.storage_target_address
        debug(f"\t\t__clear_attribute ensured object #{object_number} does not have attribute #{attribute}", "WARNING")
        # if object_number == 64:
        #     print(64)

    def op_code__jump_if_object_a_is_direct_child_of_object_b(self, instruction, associated_routine):
        object_a_number = instruction.operands[0]
        object_b_number = instruction.operands[1]

        test_condition = self.object_loader.is_obj_a_the_direct_child_of_obj_b(object_a_number, object_b_number)
        self.branch_if_test_condition_passes(instruction, associated_routine, test_condition, False, "__jump_if_object_a_is_direct_child_of_object_b")
        if test_condition:
            debug(f"\t\tobject #{object_a_number} is the direct child of object #{object_b_number} ", "WARNING")
        else:
            debug(f"\t\tobject #{object_a_number} is not the direct child of object #{object_b_number} ", "WARNING")
    
    def op_code__add_object(self, instruction, associated_routine):
        # self.global_index += 1
        object_to_be_moved = instruction.operands[0]
        object_destination = instruction.operands[1]
        self.object_loader.insert_object(object_to_be_moved, object_destination)
        debug(f"\t\t__add_object moved object \"{self.object_loader.get_object_description(object_to_be_moved)[0]}\" (#{object_to_be_moved}) to \"{self.object_loader.get_object_description(object_destination)[0]}\" (#{object_destination})", "WARNING")
        associated_routine.next_instruction_offset = instruction.storage_target_address
        # if self.global_index > 1:
        #     exit(-1)

    def op_code__print_object (self, instruction, associated_routine):
        object_number = instruction.operands[0]
        object_description = self.object_loader.get_object_description(object_number)

        # print(f"\t\t{bcolors.OKCYAN}__print_object printed object #{object_number} as: \n{object_description[0]}")
        debug(f"\t\t__print_object printed object #{object_number} as \n:{object_description[0]}", "BOLD")
        associated_routine.next_instruction_offset = instruction.storage_target_address

    def op_code__return(self, instruction, associated_routine):
        associated_routine.should_return = True
        associated_routine.return_value = instruction.operands[0]
        debug(f"\t\t__return returned routine with {instruction.operands[0]:02x}", "HEADER")
    
    def op_code__return_true(self, instruction, associated_routine):
        associated_routine.should_return = True
        associated_routine.return_value = 1 # AKA True
        debug(f"\t\t__return_true returned routine with True (AKA 1)", "HEADER")
    
    def op_code__return_false(self, instruction, associated_routine):
        associated_routine.should_return = True
        associated_routine.return_value = 0 # AKA False
        debug(f"\t\t__return_false returned routine with False (AKA 0)", "HEADER")

    def op_code__return_popped_top_of_stack(self, instruction, associated_routine):
        top_of_stack_to_return = instruction.load_variable(0, True) # get top of stack

        associated_routine.should_return = True
        associated_routine.return_value = top_of_stack_to_return # AKA False
        debug(f"\t\t__return_popped_top_of_stack returned top of stack ({top_of_stack_to_return})", "HEADER")



    def op_code__print(self, instruction, associated_routine):
        HexExtractor_read_string_object = self.extractor.read_string(instruction.storage_target_address, self.abreviator.abreviations_table)
        string_to_print = HexExtractor_read_string_object[0]
        final_address_after_string = HexExtractor_read_string_object[1]
        associated_routine.next_instruction_offset = final_address_after_string
        debug(f"\t\t__print printed\n:{string_to_print}", "CYAN")

    def op_code__print_then_return_true(self, instruction, associated_routine):
        HexExtractor_read_string_object = self.extractor.read_string(instruction.storage_target_address, self.abreviator.abreviations_table)
        string_to_print = HexExtractor_read_string_object[0]
        final_address_after_string = HexExtractor_read_string_object[1]
        associated_routine.next_instruction_offset = final_address_after_string
        associated_routine.should_return = True
        associated_routine.return_value = True

        debug(f"\t\t__print_then_return_true printed\n:{string_to_print}\n", "CYAN")


    def op_code__new_line(self, instruction, associated_routine):
        associated_routine.next_instruction_offset = instruction.storage_target_address
        debug(f"\t\t__new_line printed:\n", "CYAN")

    
    def op_code__print_num (self, instruction, associated_routine):
        value_to_print = byte_to_signed_int(instruction.operands[0])
        
        associated_routine.next_instruction_offset = instruction.storage_target_address
        debug(f"\t\t__print_num printed the value {instruction.operands[0]:04x} as \n:{value_to_print}", "CYAN")

    def op_code__print_char (self, instruction, associated_routine):
        value_to_print = self.extractor.read_char(instruction.operands[0])
        
        associated_routine.next_instruction_offset = instruction.storage_target_address
        debug(f"\t\t__print_char printed the value {instruction.operands[0]:04x} as \n:{value_to_print}", "CYAN")

    def op_code__print_string_at_packed_address (self, instruction, associated_routine):
        packed_address = instruction.operands[0] * 2
        z_string_to_print = self.extractor.read_string(packed_address)[0]
        
        debug(f"\t\t__print printed the following z-string {instruction.operands[0]:04x} from address {packed_address:05x}\n:{z_string_to_print}", "CYAN")
        associated_routine.next_instruction_offset = instruction.storage_target_address

    def op_code__decrement_and_check (self, instruction, associated_routine):
        variable_address = instruction.operands[0]
        variable_value = 0x0000
        
        if instruction.operand_types[0] != -1: # if the first operand was not a variable, it should be treated as one
            variable_value = instruction.load_variable(variable_address)
        else:
            # The first operand was already treated like a variable
            variable_address = instruction.original_operands[0]
            variable_value = instruction.operands[0]

        comaparitor = instruction.operands[1]

        incremented_variable_value = sub_16bit_signed(variable_value, 1)

        self.routine_interpreter.store_result(incremented_variable_value, variable_address, associated_routine)

        branch_info_num_bytes = (0b01000000 & instruction.storage_target == 0) + 1
        invert_branch_condition = (0b10000000 & instruction.storage_target == 0)
        address_after_last_branch_info_byte = instruction.storage_target_address + branch_info_num_bytes
        branch_offset = -1

        will_return = False
        will_branch = False

        test_condition = (incremented_variable_value < comaparitor)
        if (test_condition and not invert_branch_condition) or (not test_condition and invert_branch_condition):
            if branch_info_num_bytes == 1:
                branch_offset = 0b00111111 & instruction.storage_target # first byte after list of operands
            elif branch_info_num_bytes == 2:
                unsigned_branch_offset = ((0b00111111 & instruction.storage_target) << 8) | (instruction.branch_target)
                branch_offset = binary_14_bits_to_signed_int(unsigned_branch_offset)# treat value as signed
            else:
                raise Exception("branch info num bytes not between 1 and 2")

            if branch_offset == 0:
                associated_routine.return_value = False
                associated_routine.should_return = True
                will_return = True
                debug(f"\t\t__decrement_and_check returns False", "WARNING")
            elif branch_offset == 1:
                associated_routine.return_value = True
                associated_routine.should_return = True
                will_return = True
                debug(f"\t\t__decrement_and_check returns True", "WARNING")
            else:
                will_branch = True
                associated_routine.next_instruction_offset = address_after_last_branch_info_byte + branch_offset - 2
                debug(f"\t\t__decrement_and_check branches to {associated_routine.next_instruction_offset:05x}", "WARNING")
        else:
            # update address of next instruction
            debug(f"\t\t__decrement_and_check does not branch", "WARNING")
            associated_routine.next_instruction_offset = address_after_last_branch_info_byte
        
        # Debug info:
        if branch_info_num_bytes == 1:
            debug(f"\t\tbranch info byte: {instruction.storage_target:02x}")
        else:
            debug(f"\t\tbranch info bytes: {((instruction.storage_target<<8) | instruction.branch_target):04x}")
        debug(f"\t\tbranch condition inverted: {invert_branch_condition}")
        debug(f"\t\ttest condition passed: {test_condition}")
        debug(f"\t\tbranch offset: {branch_offset}")
        debug(f"\t\tWill branch: {will_branch}")
        debug(f"\t\tWill return: {will_return}")

    def op_code__increment_and_check (self, instruction, associated_routine):
        variable_address = instruction.operands[0]
        variable_value = 0x0000
        
        if instruction.operand_types[0] != -1: # if the first operand was not a variable, it should be treated as one
            variable_value = instruction.load_variable(variable_address)
        else:
            # The first operand was already treated like a variable
            variable_address = instruction.original_operands[0]
            variable_value = instruction.operands[0]

        comaparitor = instruction.operands[1]

        incremented_variable_value = add_16bit_signed(variable_value, 1)

        self.routine_interpreter.store_result(incremented_variable_value, variable_address, associated_routine)

        branch_info_num_bytes = (0b01000000 & instruction.storage_target == 0) + 1
        invert_branch_condition = (0b10000000 & instruction.storage_target == 0)
        address_after_last_branch_info_byte = instruction.storage_target_address + branch_info_num_bytes
        branch_offset = -1

        will_return = False
        will_branch = False

        test_condition = (incremented_variable_value > comaparitor)
        if (test_condition and not invert_branch_condition) or (not test_condition and invert_branch_condition):
            if branch_info_num_bytes == 1:
                branch_offset = 0b00111111 & instruction.storage_target # first byte after list of operands
            elif branch_info_num_bytes == 2:
                unsigned_branch_offset = ((0b00111111 & instruction.storage_target) << 8) | (instruction.branch_target)
                branch_offset = binary_14_bits_to_signed_int(unsigned_branch_offset)# treat value as signed
            else:
                raise Exception("branch info num bytes not between 1 and 2")

            if branch_offset == 0:
                associated_routine.return_value = False
                associated_routine.should_return = True
                will_return = True
                debug(f"\t\t__increment_and_check returns False", "WARNING")
            elif branch_offset == 1:
                associated_routine.return_value = True
                associated_routine.should_return = True
                will_return = True
                debug(f"\t\t__increment_and_check returns True", "WARNING")
            else:
                will_branch = True
                associated_routine.next_instruction_offset = address_after_last_branch_info_byte + branch_offset - 2
                debug(f"\t\t__increment_and_check branches to {associated_routine.next_instruction_offset:05x}", "WARNING")
        else:
            # update address of next instruction
            debug(f"\t\t__increment_and_check does not branch", "WARNING")
            associated_routine.next_instruction_offset = address_after_last_branch_info_byte
        
        # Debug info:
        if branch_info_num_bytes == 1:
            debug(f"\t\tbranch info byte: {instruction.storage_target:02x}")
        else:
            debug(f"\t\tbranch info bytes: {((instruction.storage_target<<8) | instruction.branch_target):04x}")
        debug(f"\t\tbranch condition inverted: {invert_branch_condition}")
        debug(f"\t\ttest condition passed: {test_condition}")
        debug(f"\t\tbranch offset: {branch_offset}")
        debug(f"\t\tWill branch: {will_branch}")
        debug(f"\t\tWill return: {will_return}")


    def op_code__random (self, instruction, associated_routine):
        
        range_value = instruction.operands[0]
        result_to_store = 0
        if range_value > 0:
            result_to_store = random.randrange(0, range_value)
        elif range_value < 0:
            random.seed(range_value)
        elif range_value == 0:
            random.seed(round(time.time() * 1000))
        storage_target = instruction.storage_target

        # assert(len(z_words) == len(user_input))

        
        self.routine_interpreter.store_result(result_to_store, storage_target, associated_routine)
        associated_routine.next_instruction_offset = instruction.branch_target_address
        debug(f"\t\t__random returned random value {result_to_store} from the range [0, {range_value}]", "WARNING")

    def op_code__read_line_of_user_input (self, instruction, associated_routine):
        text_memory_buffer_address = instruction.operands[0]
        parse_memory_buffer_address = instruction.operands[1]

        max_number_of_input_letters = self.extractor.read_byte(text_memory_buffer_address)
        # debug(f"\t\tmaximum number of input letters: {max_number_of_input_letters}","debug")

        # get user input
        # if not self.should_get_user_input:
            # user_input = "w"[0:max_number_of_input_letters].lower()
        # else:

        debug(f"waiting for user input", "scroll")

        # user_input = input()[0:max_number_of_input_letters].lower()
        user_input = self.user_input.get_user_input()

        # debug(f"\n","CYAN_no_z_string")
        print(f"recieved user input: {user_input}")
        cleaned_user_input = ascii(normalize("NFC", user_input)).replace("\\xa0", " ")[1:-1]

        # convert input to z_characters
        z_characters = self.extractor.string_to_z_characters(cleaned_user_input)

        z_word_and_text_buffer_index_list_object = self.extractor.z_characters_to_z_words_and_text_buffer_index_list(z_characters, cleaned_user_input)
        z_words = z_word_and_text_buffer_index_list_object[0]
        text_buffer_index_list = z_word_and_text_buffer_index_list_object[1]
        # debug(f"text_buffer_index_list {text_buffer_index_list}")
        # debug(f"z_chars {z_characters}","debug")
        # print(f"z_words {z_words}")
        def int_to_binary(n, width=15):
            return f'{n:0{width}b}'

        # print(f"z_words {list(map(lambda x: int_to_binary(x), z_words))}")
        # print(f"z_words {list(map(bin,z_words))}")
        actual_length_of_user_input = len(z_characters)


        self.extractor.write_byte(text_memory_buffer_address + 1, actual_length_of_user_input)
        self.extractor.write_array_of_words(text_memory_buffer_address + 2, z_words) # write z_words to text buffer starting at byte 3


        # debug(f"\t\t__read_line_of_user_input recieved input \"{cleaned_user_input}\" ", "WARNING")
        # print(f"\t\t__read_line_of_user_input recieved input \"{cleaned_user_input}\" ")
        # debug(f"length of user input ({len(cleaned_user_input)}) == lenth of z_words({len(z_characters)})", "debug")
        # print(f"length of user input ({len(cleaned_user_input)}) == lenth of z_words({len(z_characters)})")

        max_number_of_textual_words_to_be_parsed = self.extractor.read_byte(parse_memory_buffer_address)
        split_input = self.extractor.split_input_string(cleaned_user_input, text_buffer_index_list)
        # debug(f"\t\t__read_line_of_user_input split input as \"{split_input}\" ", "WARNING")
        # print(f"\t\t__read_line_of_user_input split input as \"{split_input}\" ")

        self.extractor.write_byte(parse_memory_buffer_address + 1, len(split_input))
        parse_buffer_index = 2
        for word_entry in split_input:
            dictionary_address = self.routine_interpreter.dictionary.get_dict_address(word_entry[0]) # not stored as packed because not always even
            # print(f"[{word_entry[0]}]'s dict address {(dictionary_address):05x}")
            self.extractor.write_word(parse_memory_buffer_address + parse_buffer_index, dictionary_address) # byte address of dictionary entry
            self.extractor.write_byte(parse_memory_buffer_address + parse_buffer_index + 2, len(word_entry[0])) # number of letters in the word
            self.extractor.write_byte(parse_memory_buffer_address + parse_buffer_index + 3, word_entry[1]) # position of the first char in text buffer
            parse_buffer_index += 4

        # parsed_input = self.routine_interpreter.dictionary.parse_split_input(split_input)
        associated_routine.next_instruction_offset = instruction.storage_target_address





    # def op_code__ (self, instruction, associated_routine):