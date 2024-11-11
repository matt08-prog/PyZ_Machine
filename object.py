# object.py
from hex_extractor import HexExtractor
from instruction import Instruction
# from interpreter import Interpreter

class Object:
    def __init__(self, object_number, attribute_table=[], p=0, s=0, c=0, props=[]):
        self.object_number = object_number

        # Attributes 0 to 31 are flags (at any given time, they are either on (1) or off (0))
        # stored topmost bit first: e.g., attribute 0 is stored in bit 7 of the first byte, attribute 31 is stored in bit 0 of the fourth.
        self.attribute_flags = attribute_table
        self.parent = p # object number
        self.sibling = s # object number
        self.child = c # object number
        self.properties = props

        self.properties_table = []
        # print(f"object_number: {object_number} has attributes: {attribute_table}")
        # print(f"\tHas p: {self.parent}")
        # print(f"\tHas s: {self.child}")
        # print(f"\tHas c: {self.sibling}")

    def put_value_in_property(self, property_number, value):
        object_has_given_property = False
        for prop in self.properties:
            if prop["property_number"] == property_number:
                prop["property_data"].append(value)
                object_has_given_property = True
                break
        
        if not object_has_given_property:
            raise Exception(f"Object number {self.object_number}: does not have {property_number}, halting execution")

    
    # def load_property(self, starting_address):
    #     property = {}
    #     size_byte = self.extractor.read_byte(starting_address + property_offset)
    #     if size_byte == 0:
    #         print(f"property size byte = 0")
    #         return {}
    #     property_number = size_byte & 0b00011111
    #     num_property_bytes = (size_byte >> 5) + 1
    #     propertu = {
    #     "property_number": property_number,
    #     # stored as an array
    #     "property_data": self.extractor.read_bytes_as_array(starting_address + 1 + property_offset, num_property_bytes)
    #         }
    #     print(f"num prop bytes {num_property_bytes}")
    #     print(f"prop_num: {property_number}")
    #     property_offset += num_property_bytes + 1 
