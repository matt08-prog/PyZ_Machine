# object.py
from hex_extractor import HexExtractor
from instruction import Instruction
# from interpreter import Interpreter

class Object:
    def __init__(self, object_number, attribute_table, p, s, c, props):
        self.object_number = object_number

        # Attributes 0 to 31 are flags (at any given time, they are either on (1) or off (0))
        # stored topmost bit first: e.g., attribute 0 is stored in bit 7 of the first byte, attribute 31 is stored in bit 0 of the fourth.
        self.attribute_flags = attribute_table
        self.parent = p # object number
        self.sibling = s # object number
        self.child = c # object number
        self.properties = props

        self.properties_table = []
        print(f"object_number: {object_number} has attributes: {attribute_table}")
        print(f"\tHas p: {self.parent}")
        print(f"\tHas s: {self.child}")
        print(f"\tHas c: {self.sibling}")