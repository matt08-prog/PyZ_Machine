# instruction.py
from hex_extractor import HexExtractor
from debuger import debug

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

class Instruction:
    def __init__(self, extractor, address, routine_interpreter, current_routine):
        self.extractor = extractor
        self.starting_address = address
        self.routine_interpreter = routine_interpreter
        self.current_routine = current_routine
        # for short, always 1OP unless code = 1
        self.num_ops_dict = {0: 2, 1: 1, 2: 1, 3: 0}  # large, small, Variable, (Omitted)
        self.variable_form_op_types = {0: 2, 1: 1, 2: -1}  # large, small, Variable, (Omitted)
        # large (2), small (1), var (-1)
        self.num_ops = 0 # -1 = var
        self.operand_types = []
        self.opcode = 0
        self.instruction_form = 1
        self.full_opcode = 0x00
        self.long_instruction_form_op_type_dict = {0: 1, 1: -1}
        self.short_instruction_form_op_type_dict = {0: 2, 1: 1, 2:-1, 3: 0} # large, small, Variable, (Omitted)
        self.debug_operands = []
        self.original_operands = []
        self.operands = []
        self.storage_target_address = self.starting_address # set after loading the last operand
        self.branch_target_address = self.starting_address # set after loading the last operand
        self.storage_target = 0 # set after loading the last operand
        self.branch_target = 0 # set after loading the last operand
        
        self.parse_instruction()

    def parse_instruction(self):
        self.instruction_form = 1 # 0 = Short, 1 = Long, 2 = Variable
        full_opcode = self.extractor.read_byte(self.starting_address) # address after final local variable
        operand_type_byte = self.extractor.read_byte(self.starting_address + 1) # list of 2-bit op_types for var length operand
        initial_operands_offset = self.starting_address + 1

        if (full_opcode & 0b11000000 == 192):
            self.instruction_form = 2 # Variable
            initial_operands_offset = self.starting_address + 2 # to account for the byte of operand types
            if (full_opcode & 0b00100000 == 0):
                self.num_ops = 2
            else:
                self.num_ops = 0 # this will be set when looking through next byte for operand types
            self.opcode = full_opcode & 0b00011111

            for op_type_index in range(0,8, 2):
                op_type = (operand_type_byte & (0b11000000 >> op_type_index)) >> 6 - op_type_index

                if (op_type == 3):
                    break
                else:
                    self.operand_types.append(self.variable_form_op_types[op_type])
                    self.num_ops += 1
        
        elif (full_opcode & 0b11000000 == 128):
            self.instruction_form = 0 # Short
            op_value = (full_opcode & 0b00110000) >> 4
            self.num_ops = self.num_ops_dict[op_value]
            self.operand_types.append(self.short_instruction_form_op_type_dict[op_value])
            self.opcode = full_opcode & 0b00001111
        
        else:
            self.instruction_form = 1 # Long
            op_value = (full_opcode & 0b00110000) >> 4
            self.num_ops = 2
            self.operand_types = [
                self.long_instruction_form_op_type_dict[(full_opcode & 0b01000000) >> 6], 
                self.long_instruction_form_op_type_dict[(full_opcode & 0b00100000) >> 5]]
            self.opcode = full_opcode & 0b00011111

        self.full_opcode = full_opcode

        self.load_operands(initial_operands_offset)
    
    def load_variable(self, load_target, should_pop_stack=False):
        if (load_target == 0x00):
            debug(f"\t\tload 0x{self.routine_interpreter.stack[-1]:02x} ({self.routine_interpreter.stack[-1]}) from top of stack", "FAIL")
            stack_value = self.routine_interpreter.stack[-1]
            if should_pop_stack:
                # print(f"length before poping {len(self.routine_interpreter.stack)}")
                self.routine_interpreter.stack.pop()
                # print(f"length after poping {len(self.routine_interpreter.stack)}")
            return stack_value
        elif (load_target > 0x00 and load_target < 0x10): # 0x01 to 0xf0 are meant for local vars
            debug(f"\t\tload 0x{self.current_routine.local_vars[load_target - 1]:02x} ({self.current_routine.local_vars[load_target - 1]}) from local var 0x{(load_target - 1):02x} ({(load_target - 1)})", "FAIL")
            return self.current_routine.local_vars[load_target - 1]
        elif (load_target > 0x0f and load_target < 0x100): # 0x10 to 0xff are meant for global_vars
            debug(f"\t\tload 0x{self.routine_interpreter.global_vars[load_target - 0x10]:02x} ({self.routine_interpreter.global_vars[load_target - 0x10]}) from global var 0x{(load_target - 0x10):02x} ({load_target - 0x10})", "FAIL")
            return self.routine_interpreter.global_vars[load_target - 0x10]
        else:
            debug(f"\t\tload variable {load_target} is out of bounds", "FAIL")
            exit(-1)

    def load_operands(self, initial_operand_offset):
        operand_offset = initial_operand_offset
        for operand_type in self.operand_types:
            self.original_operands.append(self.extractor.read_word(operand_offset))
            if (operand_type == 2): # large operand (2 bytes)
                self.debug_operands.append("same")
                self.operands.append(self.extractor.read_word(operand_offset))
                operand_offset += 2
            elif (operand_type == 1): # small operand (1 byte)
                self.operands.append(self.extractor.read_byte(operand_offset))
                self.debug_operands.append("same")
                operand_offset += 1
            elif (operand_type == -1): # variable operand (1 byte)
                self.debug_operands.append(hex(self.extractor.read_byte(operand_offset)))
                self.operands.append(self.load_variable(self.extractor.read_byte(operand_offset)))
                operand_offset += 1
        self.storage_target_address = operand_offset
        self.branch_target_address = operand_offset + 1
        self.storage_target = self.extractor.read_byte(self.storage_target_address)
        self.branch_target = self.extractor.read_byte(self.branch_target_address)
