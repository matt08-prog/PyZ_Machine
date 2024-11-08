# routine.py
from hex_extractor import HexExtractor
from instruction import Instruction
# from interpreter import Interpreter

class Routine:
    def __init__(self, extractor, initial_address, passed_arguments, routine_interpreter):
        self.extractor = extractor
        self.initial_address = initial_address
        self.routine_interpreter = routine_interpreter
        self.num_local_vars = 0
        self.local_vars = self.read_routine_header()
        self.load_in_passed_arguments(passed_arguments)
        self.next_instruction_offset = initial_address + 1 + (len(self.local_vars) * 2)
        self.should_return = False
        self.return_value = False

    def read_routine_header(self):
        self.num_local_vars = self.extractor.read_byte(self.initial_address)
        local_vars = []
        for local_var_index in range(0, self.num_local_vars*2, 2):
            local_vars.append(self.extractor.read_word(self.initial_address + local_var_index))
        return local_vars
    
    def load_in_passed_arguments(self, passed_arguments):
        for arg_index in range(len(passed_arguments)):
            self.local_vars[arg_index] = passed_arguments[arg_index]
    
    def read_next_instruction(self):
        next_instruction = Instruction(self.extractor, self.next_instruction_offset, self.routine_interpreter, self)
        return next_instruction

