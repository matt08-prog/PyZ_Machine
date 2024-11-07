# instruction.py
from hex_extractor import HexExtractor

class Instruction:
    def __init__(self, extractor, address):
        self.extractor = extractor
        self.starting_address = address
        # for short, always 1OP unless code = 1
        self.num_ops_dict = {0: 2, 1: 1, 2: 1, 3: 0}  # large, small, Variable, (Omitted)
        self.num_ops = 0 # -1 = var
        self.operand_types = []
        self.opcode = 0
        self.instruction_form = 1
        self.full_opcode = 0x00
        self.operands = []
        self.storage_target_address = self.starting_address # set after loading the last operand
        self.branch_target_address_target_address = self.starting_address # set after loading the last operand
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
                    self.operand_types.append(self.num_ops_dict[op_type])
                    self.num_ops += 1
        
        elif (full_opcode & 0b11000000 == 128):
            self.instruction_form = 0 # Short
            op_value = (full_opcode & 0b00110000) >> 4
            self.num_ops = self.num_ops_dict[op_value]
            self.operand_types.append(self.num_ops_dict[op_value])
            self.opcode = full_opcode & 0b00001111
        
        else:
            self.instruction_form = 1 # Long
            op_value = (full_opcode & 0b00110000) >> 4
            self.num_ops = 2
            self.operand_types = [int(full_opcode & 0b01000000 != 0) + 1, int(full_opcode & 0b00100000 != 0) + 1]
            self.opcode = full_opcode & 0b00011111

        self.full_opcode = full_opcode

        self.load_operands(initial_operands_offset)
    
    def load_operands(self, initial_operand_offset):
        operand_offset = initial_operand_offset
        for operand_type in self.operand_types:
            if (operand_type == 2): # large operand (2 bytes)
                self.operands.append(self.extractor.read_word(operand_offset))
                operand_offset += 2
            elif (operand_type == 1): # small operand (1 byte)
                self.operands.append(self.extractor.read_word(operand_offset))
                operand_offset += 1
            elif (operand_type == -1): # variable operand (1 byte)
                # implement loading a variable type operand
                operand_offset += 1
        self.storage_target_address = operand_offset
        self.branch_target_address = operand_offset + 1
