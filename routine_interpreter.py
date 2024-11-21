# routine_interpreter.py
from hex_extractor import HexExtractor
from instruction import Instruction
from routine import Routine
from instruction_interpreter import InstructionInterpreter
from debuger import debug

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

class RoutineInterpreter:
    def __init__(self, extractor, header, max_time_step, object_loader, abreviator, dictionary):
        self.extractor = extractor
        self.header = header
        self.max_time_step = max_time_step
        self.instruction_interpreter = InstructionInterpreter(self.extractor, self.header, self, object_loader, abreviator)
        self.dictionary = dictionary

        self.time_stamp = 0
        
        self.stack = []
        self.global_vars = [0x00] * 310
        self.global_vars = self.extractor.get_init_global_data(self.header.start_of_globals_table)
        # print(f"global_vars (length={len(self.global_vars)}): {list(map(hex, self.global_vars))}")
        self.debug_instruction_index = 0
        self.debug_instruction_form_dict = {0: "short", 1: "long", 2: "variable"}
        self.operand_types_dict = {2: "L", 1: "S", -1: "Var"}


    def start_interpreting(self):
        starting_routine_address_from_header = self.header.initial_execution_point - 1
        starting_routine = Routine(self.extractor, starting_routine_address_from_header, [], self)
        debug(f"first routine's address: {starting_routine_address_from_header}")
        debug(f"routine's local vars: {starting_routine.local_vars}")
        self.run_routine(starting_routine) # This starting routine should never return a value
    
    def run_routine(self, routine):
        # print(f"number of local vars: {routine.num_local_vars}")
        debug(f"routine's local vars: {list(map(hex, routine.local_vars))}", "debug")
        while True:
            self.time_stamp += 1
            if self.time_stamp > self.max_time_step and self.max_time_step != -1:
                # debug exit, otherwise it tries to return from all routines at end of simulation
                exit(-1)
            next_instruction = routine.read_next_instruction()


            debug(f"{routine.next_instruction_offset:02x} time-{self.time_stamp} routine's next instruction address", "time-stamp")
            debug(f"{routine.next_instruction_offset:02x}", "time-stamp-only")


            debug(f"\tinstruction_form: {self.debug_instruction_form_dict[next_instruction.instruction_form]}", "debug")
            # print(f"\tnum_ops: {next_instruction.num_ops}")
            # print(f"\topcode: {next_instruction.opcode}")
            debug(f"\toperand_types: [", "debug", "")
            if next_instruction.num_ops > 0: # some instruction like print have 0Ops
                for operand_index in range(len(next_instruction.operand_types)):
                    end_string = ", " if operand_index != len(next_instruction.operand_types) - 1 else "]\n" 
                    debug(f"{self.operand_types_dict[next_instruction.operand_types[operand_index]]}" , "debug", end_string)
            else:
                debug("]", "debug")
            debug(f"\toriginal operands: {next_instruction.debug_operands}", "debug")
            debug(f"\t         operands: {list(map(hex, next_instruction.operands))}", "debug")
            # print(f"\taddress_of_store_target (if it exists): {next_instruction.storage_target_address:02x}")
            # print(f"\taddress_of_branch_target (if it exists): {next_instruction.branch_target_address:02x}")
            self.instruction_interpreter.interpret_instruction(next_instruction, routine)
            if routine.should_return:
                break
        
        return routine.return_value # Routine returned

    def store_result(self, result_to_store, storage_target, current_routine):
            if (storage_target == 0x00):
                self.stack.append(result_to_store)
                debug(f"\t\tPushed 0x{result_to_store:02x} onto the stack", "GREEN")

            elif (storage_target > 0x00 and storage_target < 0x10): # 0x01 to 0xf0 are meant for local vars
                current_routine.local_vars[storage_target - 1] = result_to_store
                debug(f"\t\t0x{result_to_store:02x} placed in local var 0x{(storage_target - 1):03x} ({storage_target - 1})", "GREEN")

            elif (storage_target > 0x0f and storage_target < 0x100): # 0x10 to 0xff are meant for global_vars
                self.global_vars[storage_target - 0x10] = result_to_store
                debug(f"\t\t0x{result_to_store:02x} placed in global var 0x{(storage_target - 0x10):03x} {(storage_target - 0x10)}", "GREEN")
                if storage_target - 0x10 == 139:
                    debug(f"\t\t0x{result_to_store:02x} placed in global var 0x{(storage_target - 0x10):03x} {(storage_target - 0x10)}", "GREEN")
            else:
                debug(f"\t\tStorage target {storage_target} is out of bounds!", "GREEN")
                exit(-1)