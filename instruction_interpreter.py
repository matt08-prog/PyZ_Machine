# instruction_interpreter.py
from hex_extractor import HexExtractor
from instruction import Instruction
from routine import Routine

 # should be moved to global variable file with helper functions
 #      should also be merged with two functions below it into one function that lets you specify the number of bits
def binary_word_16_bits_to_signed_int(binary_value):
    print(f"\t\t\tbinary_to_signed_int")
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
    num_bits = 16
    
    # Convert to integer
    num = int(binary_str, 2)
    
    # If the leftmost bit is 1, it's a negative number in two's complement
    if num & (1 << (num_bits - 1)):
        # The only time we should ever get here is if this is the first time the interpreter is looking at this value
        num -= 1 << num_bits
    print(f"\t\t\tfinal value: {num}")
    return num

def binary_14_bits_to_signed_int(binary_value): # should be moved to global variable file with helper functions
    print(f"\t\t\tbinary_to_signed_int")
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
    num_bits = 14
    
    # Convert to integer
    num = int(binary_str, 2)
    
    # If the leftmost bit is 1, it's a negative number in two's complement
    if num & (1 << (num_bits - 1)):
        # The only time we should ever get here is if this is the first time the interpreter is looking at this value
        num -= 1 << num_bits
    print(f"\t\t\tfinal value: {num}")
    return num


def byte_to_signed_int(binary_value): # should be moved to global variable file with helper functions
    print(f"\t\t\tbinary_to_signed_int")
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
    num_bits = 14
    
    # Convert to integer
    num = int(binary_str, 2)
    
    # If the leftmost bit is 1, it's a negative number in two's complement
    if num & (1 << (num_bits - 1)):
        # The only time we should ever get here is if this is the first time the interpreter is looking at this value
        num -= 1 << num_bits
    print(f"\t\t\tfinal value: {num}")
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
    def __init__(self, extractor, header, routine_interpreter, object_loader, abreviator):
        self.extractor = extractor
        self.header = header
        self.routine_interpreter = routine_interpreter
        self.object_loader = object_loader
        self.abreviator = abreviator

        self.time_stamp = 0

        # this opcode table should actually call functions from a seperate op_code interpreter class
        self.opcode_table = {
            0xe0: self.op_code__call, 

            0x54: self.op_code__add, 
            0x74: self.op_code__add,

            0x55: self.op_cod__sub,

            0xc9: self.op_code__and,

            0xa0: self.op_code__jump_if_zero,
            0x61: self.op_code__jump_if_equal,
            0x41: self.op_code__jump_if_equal,
            0x05: self.op_code__increment_and_check,
            0x8c: self.op_code__jump,

            0x4F: self.op_code__load_word,
            0x0F: self.op_code__load_word,
            0xe1: self.op_code__store_word,

            0x0d: self.op_code__store,
            0x2d: self.op_code__store,

            0xe3: self.op_code__put_prop,
            0x46: self.op_code__jump_if_object_a_is_direct_child_of_object_b,
            0x4a: self.op_code__test_attribute,
            0x4b: self.op_code__set_attribute,
            0x51: self.op_code__get_property,
            0xa3: self.op_code__get_parent_of_object,
            0x4c: self.op_code__clear_attribute,
            0x6e: self.op_code__add_object,
            0xaa: self.op_code__print_object,

            0xab: self.op_code__return,
            0xb0: self.op_code__return_true,

            0xb2: self.op_code__print,
            0xe6: self.op_code__print_num,
            0xbb: self.op_code__new_line
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

    def op_code__and (self, instruction, associated_routine):
        result_to_store = instruction.operands[0] & instruction.operands[1]

        self.routine_interpreter.store_result(result_to_store, instruction.storage_target, associated_routine)
        associated_routine.next_instruction_offset = instruction.branch_target_address
        print(f"\t\t{bcolors.OKCYAN}__new_line\n{bcolors.ENDC}")

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
                branch_offset = binary_14_bits_to_signed_int(unsigned_branch_offset)# treat value as signed
            else:
                raise Exception("branch info num bytes not between 1 and 2")

            if branch_offset == 0:
                associated_routine.return_value = False
                associated_routine.should_return = True
                will_return = True
                print(f"\t\t{bcolors.WARNING}__Jump_if_equal returns False{bcolors.ENDC}")
            elif branch_offset == 1:
                associated_routine.return_value = True
                associated_routine.should_return = True
                will_return = True
                print(f"\t\t{bcolors.WARNING}__Jump_if_equal returns True{bcolors.ENDC}")
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
                branch_offset = binary_14_bits_to_signed_int(unsigned_branch_offset)# treat value as signed
            else:
                raise Exception("branch info num bytes not between 1 and 2")

            if branch_offset == 0:
                associated_routine.return_value = False
                associated_routine.should_return = True
                will_return = True
                print(f"\t\t{bcolors.WARNING}__Jump_if_zero returns False{bcolors.ENDC}")
            elif branch_offset == 1:
                associated_routine.return_value = True
                associated_routine.should_return = True
                will_return = True
                print(f"\t\t{bcolors.WARNING}__Jump_if_zero returns True{bcolors.ENDC}")
            else:
                will_branch = True
                associated_routine.next_instruction_offset = address_after_last_branch_info_byte + branch_offset - 2
                print(f"\t\t{bcolors.WARNING}__Jump_if_zero branches to {associated_routine.next_instruction_offset:05x}{bcolors.ENDC}")
        else:
            # update address of next instruction
            associated_routine.next_instruction_offset = address_after_last_branch_info_byte
            print(f"\t\t{bcolors.WARNING}__Jump_if_zero does not branch{bcolors.ENDC}")
        
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
        unsigned_branch_offset = instruction.operands[0]
        signed_branch_offset = binary_word_16_bits_to_signed_int(unsigned_branch_offset)

        # update address of next instruction
        print(f"\t\t{bcolors.WARNING}__Jump unconditional jumped to {(instruction.storage_target_address + signed_branch_offset - 2):05x} given an offset of {signed_branch_offset} - 2 = {signed_branch_offset - 2}{bcolors.ENDC}")
        associated_routine.next_instruction_offset = instruction.storage_target_address + signed_branch_offset - 2
        

    ##//*-/*-/*-/*-/*-/*-/*-/*-/*-/*- May need to look this over to ensure its implemented correctly
    # Puts whatever value is at array[word-index*2] into the given target
    def op_code__load_word(self, instruction, associated_routine):
        # operand 0 is the start of array and operand 1 is the index of the array
        address_to_fetch = instruction.operands[0] + 2 * instruction.operands[1]
        result_to_store = self.extractor.read_byte(address_to_fetch)
        
        self.routine_interpreter.store_result(result_to_store, instruction.storage_target, associated_routine)
        print(f"\t\t{bcolors.WARNING}__load_word loaded {result_to_store:02x} froma address {address_to_fetch:05x} into {instruction.storage_target:02x}{bcolors.ENDC}")
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

    def op_code__store(self, instruction, associated_routine):
        value_to_store = instruction.operands[1]
        variable_store_destination = instruction.operands[0]

        self.routine_interpreter.store_result(value_to_store, variable_store_destination, associated_routine)
        associated_routine.next_instruction_offset = instruction.storage_target_address
        print(f"\t\t{bcolors.WARNING}__store stored {value_to_store:02x} into {variable_store_destination:05x}{bcolors.ENDC}")

    def op_code__put_prop(self, instruction, associated_routine):
        object_number = instruction.operands[0]
        property_number = instruction.operands[1]
        value = instruction.operands[2]

        self.object_loader.put_value_in_property(object_number, property_number, value)
        associated_routine.next_instruction_offset = instruction.storage_target_address
        print(f"\t\t{bcolors.OKCYAN}__put_prop returned routine with {instruction.operands[0]:02x}{bcolors.ENDC}")

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
                print(f"\t\t{bcolors.WARNING}__test_attribute returns False{bcolors.ENDC}")
            elif branch_offset == 1:
                associated_routine.return_value = True
                associated_routine.should_return = True
                will_return = True
                print(f"\t\t{bcolors.WARNING}__test_attribute returns True{bcolors.ENDC}")
            else:
                will_branch = True
                associated_routine.next_instruction_offset = address_after_last_branch_info_byte + branch_offset - 2
                print(f"\t\t{bcolors.WARNING}__test_attribute jumped to {associated_routine.next_instruction_offset:05x}{bcolors.ENDC}")
        else:
            # update address of next instruction
            associated_routine.next_instruction_offset = address_after_last_branch_info_byte
            print(f"\t\t{bcolors.WARNING}__test_attribute does not branch{bcolors.ENDC}")
        
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
    
    def op_code__set_attribute(self, instruction, associated_routine):
        object_number = instruction.operands[0]
        attribute = instruction.operands[1]
        self.object_loader.set_attribute(object_number, attribute)
        associated_routine.next_instruction_offset = instruction.storage_target_address
        print(f"\t\t{bcolors.WARNING}__set_attribute ensured object #{object_number} had attribute #{attribute}{bcolors.ENDC}")

    def op_code__get_property(self, instruction, associated_routine):
        object_number = instruction.operands[0]
        property_number = instruction.operands[1]
        property_data_array = self.object_loader.get_object_property(object_number, property_number)
        property_value = 0

        if len(property_data_array) == 1:
            property_value = property_data_array[0]
        else:
            property_value = (property_data_array[0] << 8) | property_data_array[1]

        storage_target = instruction.storage_target

        if (len(property_data_array) not in [1, 2]):
            print(f"\t\t{bcolors.FAIL}property #{property_number} (whose value is {property_value} has an erroneous length of {len(property_value)}){bcolors.ENDC}")
            exit(-1)

        print(f"\t\t{bcolors.WARNING}__get_property found object #{object_number} has property #{property_number} (whose value is {property_value} ({property_value:04x})){bcolors.ENDC}")
        self.routine_interpreter.store_result(property_value, storage_target, associated_routine)
        associated_routine.next_instruction_offset = instruction.branch_target_address

    def op_code__get_parent_of_object(self, instruction, associated_routine):
        object_number = instruction.operands[0]
        parent_object_number = self.object_loader.get_object_parent(object_number)
        storage_target = instruction.storage_target
        self.routine_interpreter.store_result(parent_object_number, storage_target, associated_routine)
        associated_routine.next_instruction_offset = instruction.branch_target_address
        print(f"\t\t{bcolors.WARNING}__get_parent_of_object found object #{object_number} has parent #{parent_object_number}{bcolors.ENDC}")

    def op_code__clear_attribute(self, instruction, associated_routine):
        object_number = instruction.operands[0]
        attribute = instruction.operands[1]
        self.object_loader.remove_attribute(object_number, attribute)
        associated_routine.next_instruction_offset = instruction.storage_target_address
        print(f"\t\t{bcolors.WARNING}__clear_attribute ensured object #{object_number} does not have attribute #{attribute}{bcolors.ENDC}")

    def op_code__jump_if_object_a_is_direct_child_of_object_b(self, instruction, associated_routine):
        object_a_number = instruction.operands[0]
        object_b_number = instruction.operands[0]
        unsigned_branch_offset = instruction.branch_target_address
        signed_branch_offset = binary_14_bits_to_signed_int(unsigned_branch_offset)

        if self.object_loader.is_obj_a_the_direct_child_of_obj_b(object_a_number, object_b_number):
            associated_routine.next_instruction_offset = instruction.storage_target_address + signed_branch_offset
            print(f"\t\t{bcolors.WARNING}__jump_if_object_a_is_direct_child_of_object_b jumped to {associated_routine.next_instruction_offset:05x}{bcolors.ENDC}")
        else:
            associated_routine.next_instruction_offset = instruction.branch_target_address
            print(f"\t\t{bcolors.WARNING}__jump_if_object_a_is_direct_child_of_object_b did not jump {bcolors.ENDC}")

    def op_code__add_object(self, instruction, associated_routine):
        object_to_be_moved = instruction.operands[0]
        object_destination = instruction.operands[1]
        self.object_loader.insert_object(object_to_be_moved, object_destination)
        print(f"\t\t{bcolors.WARNING}__add_object moved object {object_to_be_moved} to {object_destination}{bcolors.ENDC}")
        associated_routine.next_instruction_offset = instruction.storage_target_address

    def op_code__print_object (self, instruction, associated_routine):
        object_number = instruction.operands[0]
        object_description = self.object_loader.get_object_description(object_number)

        print(f"\t\t{bcolors.OKCYAN}__print_object printed object #{object_number} as: \n{object_description[0]}{bcolors.ENDC}")
        associated_routine.next_instruction_offset = instruction.storage_target_address

    def op_code__return(self, instruction, associated_routine):
        associated_routine.should_return = True
        associated_routine.return_value = instruction.operands[0]
        print(f"\t\t{bcolors.HEADER}__return returned routine with {instruction.operands[0]:02x}{bcolors.ENDC}")
    
    def op_code__return_true(self, instruction, associated_routine):
        associated_routine.should_return = True
        associated_routine.return_value = 1 # AKA True
        print(f"\t\t{bcolors.HEADER}__return returned routine with True (AKA 1){bcolors.ENDC}")

    def op_code__print(self, instruction, associated_routine):
        HexExtractor_read_string_object = self.extractor.read_string(instruction.storage_target_address, self.abreviator.abreviations_table)
        string_to_print = HexExtractor_read_string_object[0]
        final_address_after_string = HexExtractor_read_string_object[1]
        associated_routine.next_instruction_offset = final_address_after_string
        print(f"\t\t{bcolors.OKCYAN}__print printed\n{string_to_print}{bcolors.ENDC}")


    def op_code__new_line(self, instruction, associated_routine):
        associated_routine.next_instruction_offset = instruction.storage_target_address
        print(f"\t\t{bcolors.OKCYAN}__new_line\n{bcolors.ENDC}")

    
    def op_code__print_num (self, instruction, associated_routine):
        value_to_print = byte_to_signed_int(instruction.operands[0])
        
        associated_routine.next_instruction_offset = instruction.storage_target_address
        print(f"\t\t{bcolors.OKCYAN}__print printed the value {instruction.operands[0]:04x} as \n{value_to_print}{bcolors.ENDC}")

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
                print(f"\t\t{bcolors.WARNING}__increment_and_check returns False{bcolors.ENDC}")
            elif branch_offset == 1:
                associated_routine.return_value = True
                associated_routine.should_return = True
                will_return = True
                print(f"\t\t{bcolors.WARNING}__increment_and_check returns True{bcolors.ENDC}")
            else:
                will_branch = True
                associated_routine.next_instruction_offset = address_after_last_branch_info_byte + branch_offset - 2
                print(f"\t\t{bcolors.WARNING}__increment_and_check branches to {associated_routine.next_instruction_offset:05x}{bcolors.ENDC}")
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

    # def op_code__ (self, instruction, associated_routine):