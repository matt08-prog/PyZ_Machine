# operand.py
from hex_extractor import HexExtractor

class Operand:
    def __init__(self, extractor, address):
        self.extractor = extractor
        self.address = address
        self.operand_type = self.get_operand_type()

    def get_operand_type(self):
        operand_type = 1 # 0 - Short, 1 - Long, 2 - Variable
        operand_first_byte = self.extractor.read_word(self.address)
        print(f"{operand_first_byte:02x}")

        if (operand_first_byte & 0b11000000 == 192):
            operand_type = 2
        elif (operand_first_byte & 0b11000000 == 128):
            operand_type = 0

        return operand_type
        
        
    
