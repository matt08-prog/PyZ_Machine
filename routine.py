# routine.py
from hex_extractor import HexExtractor
from operand import Operand

class Routine:
    def __init__(self, extractor, initial_address):
        self.extractor = extractor
        self.initial_address = initial_address
        self.local_vars = self.read_routine_header()

        previous_operand_offset = initial_address + len(self.local_vars) * 2
        while True:
            print(f"operand_offset: {previous_operand_offset:02x}")
            operand = self.read_next_operand(previous_operand_offset)
            print(f"operand_type: {operand.operand_type}")
            break

    def read_routine_header(self):
        num_local_vars = self.extractor.read_byte(self.initial_address)
        print(f"num_local_vars: {num_local_vars}")
        local_vars = []
        for local_var_index in range(0, num_local_vars, 2):
            local_vars.append(self.extractor.read_word(self.initial_address + local_var_index))
        return local_vars
    
    def read_next_operand(self, adress_offset):
        return Operand(self.extractor, adress_offset)

