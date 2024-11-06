# operand.py
from hex_extractor import HexExtractor

class Operand:
    def __init__(self, extractor, address):
        self.extractor = extractor
        self.address = address
        self.operand_type = self.get_operand_type()
        # for short, always 1OP unless code = 1
        self.num_ops_dict = {0: 2, 1: 1, 2: 1, 3: 0}  # large, small, Variable, (Omitted)
        self.num_ops = 0 # -1 = var
        self.operand_types = []
        self.op_code = 0
        

    def get_operand_type(self):
        operand_type = 1 # 0 = Short, 1 = Long, 2 = Variable
        operand_first_byte = self.extractor.read_word(self.address)
        print(f"{operand_first_byte:02x}")

        if (operand_first_byte & 0b11000000 == 192):
            operand_type = 2 # Variable
            if (operand_first_byte & 0b00100000 == 0):
                self.num_ops = 2
            else:
                self.num_ops = -1
            self.op_code = operand_first_byte & 0b00011111
        elif (operand_first_byte & 0b11000000 == 128):
            operand_type = 0 # Short
            op_value = (operand_first_byte & 0b00110000) >> 4
            self.num_ops = self.num_ops_dict[op_value]
            self.operand_types.append(self.num_ops_dict[op_value])
            self.op_code = operand_first_byte & 0b00001111
        else:
            operand_type = 1 # Long
            op_value = (operand_first_byte & 0b00110000) >> 4
            self.num_ops = 2
            self.operand_types = [operand_first_byte & 0b01000000 == 0, operand_first_byte & 0b00100000 == 0]
            self.op_code = operand_first_byte & 0b00011111
            

        return operand_type
        
        
    
