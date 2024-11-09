# object_loader.py
from hex_extractor import HexExtractor
from instruction import Instruction
from object import Object
# from interpreter import Interpreter

class ObjectLoader:
    def __init__(self, extractor, header):
        self.extractor = extractor
        self.header = header
        self.start_of_properties_table = 0x00
        self.objects = self.load_objects()

    def load_objects(self):
        objects = []
        start_of_next_object = self.header.start_of_objects_table
        self.start_of_properties_table = self.extractor.read_word(start_of_next_object + 7)
        object_index = 1

        while start_of_next_object != self.start_of_properties_table:
        # while object_index < 5:
            objects.append(self.load_object(object_index, start_of_next_object))
            start_of_next_object += 9
            object_index += 1
        
        return objects

    def load_object(self, object_index, starting_address):
        attributes = []
        attribute_index = 0
        attribute_table = self.extractor.read_bytes(starting_address, 4)
        for byte_index in range(0, 24, 8):
            byte = ((0xFF000000 >> byte_index) & attribute_table) >> 24 - byte_index
            for bit in range(7, 0, -1):
                if (byte & (0b10000000 >> bit)) != 0:
                    attributes.append(attribute_index)
                attribute_index += 1
            attribute_index += 1
        
        parent_obj_num = self.extractor.read_byte(starting_address + 4)
        sibling_obj_num = self.extractor.read_byte(starting_address + 5)
        child_obj_num = self.extractor.read_byte(starting_address + 6)

        property_header_address = self.extractor.read_word(starting_address + 7)
        
        property_header = self.load_property_header(property_header_address)
        property_address = property_header["final_address"]
        properties = self.load_properties(property_address)


        z_object = Object(object_index, attributes, parent_obj_num, sibling_obj_num, child_obj_num, properties)

        return z_object

    def load_property_header(self, starting_address):
        num_descirption_words = self.extractor.read_byte(starting_address)
        description = self.extractor.read_string(starting_address + 1)
        final_address = starting_address + (num_descirption_words * 2) + 1
        print(description)
        return {"final_address": final_address}

    def load_properties(self, starting_address):
        properties = []
        property_index = 0
        while True:
            size_byte = self.extractor.read_byte(starting_address + property_index)
            if size_byte == 0:
                break
            property_number = size_byte & 0b00011111
            num_property_bytes = (size_byte >> 5) + 1
            properties.append({
            "property_number": property_number,
            # stored as an array
            "property_data": self.extractor.read_bytes_as_array(starting_address + 1 + property_index, num_property_bytes)
                })
            print(f"num prop bytes {num_property_bytes}")
            print(f"prop_num: {property_number}")
            property_index += num_property_bytes + 1 
        return properties

    def put_value_in_property(self, object_number, property_number, value):
        for obj in self.objects:
            if obj.object_number == object_number:
                obj.put_value_in_property(property_number, value)
                break
        
    def test_attribute(self, object_number, attribute):
        for obj in self.objects:
            if  obj.object_number == object_number:
                # print(list(map(hex, obj.attribute_flags)))
                # print(obj.attribute_flags)
                return attribute in obj.attribute_flags