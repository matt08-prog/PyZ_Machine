# object.py
from hex_extractor import HexExtractor
from instruction import Instruction
# from interpreter import Interpreter
from debuger import Debug

debugger = Debug()

def debug(debug_string, severity_string="unclassified_severity", end_string="\n"):
    debugger.debug(debug_string, severity_string, end_string)

class Object:
    def __init__(self, object_number, attribute_table=[], p=0, s=0, c=0, props=[], object_description=""):
        self.object_number = object_number
        # debug(f"\t\t__HEADER\n", "HEADER")
        # debug(f"\t\t__OKBLUE\n", "OKBLUE")
        # debug(f"\t\t__CYAN\n", "CYAN")
        # debug(f"\t\t__WARNING\n", "WARNING")
        # debug(f"\t\t__FAIL\n", "FAIL")
        # debug(f"\t\t__ENDC\n", "ENDC")
        # debug(f"\t\t__BOLD\n", "BOLD")
        # debug(f"\t\t__UNDERLINE\n", "UNDERLINE")
        # debug(f"\t\t__debug\n", "debug")
        # Attributes 0 to 31 are flags (at any given time, they are either on (1) or off (0))
        # stored topmost bit first: e.g., attribute 0 is stored in bit 7 of the first byte, attribute 31 is stored in bit 0 of the fourth.
        self.attribute_flags = attribute_table
        self.parent = p # object number
        self.sibling = s # object number
        self.child = c # object number
        self.properties = props
        self.object_description = object_description # string

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

    def get_property_data(self, property_number):
        property_value = -1
        for property in self.properties:
            if property["property_number"] == property_number:
                property_value = property["property_data"]

        return property_value

    def get_property_address(self, property_number):
        property_value = -1
        for property in self.properties:
            if property["property_number"] == property_number:
                property_value = property["property_address"]

        return property_value

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
