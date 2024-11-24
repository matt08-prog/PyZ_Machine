# object_loader.py
from hex_extractor import HexExtractor
from instruction import Instruction
from object import Object
from debuger import Debug

debugger = Debug()

def debug(debug_string, severity_string="unclassified_severity", end_string="\n"):
    debugger.debug(debug_string, severity_string, end_string)


class ObjectLoader:
    def __init__(self, extractor, header):
        self.extractor = extractor
        self.header = header
        self.start_of_properties_table = 0x00
        self.objects = self.load_objects()
        self.default_properties = self.load_default_properties()
        debug(f"default_properties = {self.default_properties}", "debug")
        self.normalize_object_graph()

    def load_objects(self):
        objects = [Object(0)]
        start_of_next_object = self.header.start_of_objects_table
        self.start_of_properties_table = self.extractor.read_word(start_of_next_object + 7)
        object_index = 1

        while start_of_next_object != self.start_of_properties_table:
        # while object_index < 5:
            object_to_append = self.load_object(object_index, start_of_next_object)
            objects.append(object_to_append)
            # print(f"object #{object_index} ({objects[-1].object_description}) has properties: {objects[-1].properties}")


            start_of_next_object += 9
            object_index += 1
        
        return objects
    
    def normalize_object_graph(self):
        for object_to_append in self.objects:
            # print(f"fixing object {object_to_append.object_number}")
            object_child_index = object_to_append.child
            if (object_child_index > 0):
                # print(f"fixing object child {object_child_index}")

                object_child = self.find_object(object_to_append)
                if object_child.object_number > 0:
                    print(f"added {object_to_append.object_number} as {object_child}'s parent")
                    object_child.parent = object_to_append.object_number

            object_parent_index = object_to_append.parent
            if (object_parent_index > 0):
                object_parent = self.find_object(object_to_append)
                if object_parent.object_number > 0:
                    object_parent.child = object_to_append.object_number



    def load_object(self, object_index, starting_address):
        attributes = []
        attribute_index = 1
        attribute_table = self.extractor.read_bytes(starting_address, 4)
        for bit in range(32, -1, -1):
            if (attribute_table & (0b1 << bit)) != 0:
                attributes.append(31 - bit)

        # for byte_index in range(0, 25, 8):
        #     byte = ((0x000000FF << byte_index) & attribute_table) >> byte_index
        #     for bit in range(0, 8, 1):
        #     # for bit in range(0, 8, 1):
        #         if (byte & (0b10000000 >> bit)) != 0:
        #             attributes.append((bit) + byte_index)
        #         attribute_index += 1
        #     attribute_index += 1
        
        parent_obj_num = self.extractor.read_byte(starting_address + 4)
        sibling_obj_num = self.extractor.read_byte(starting_address + 5)
        child_obj_num = self.extractor.read_byte(starting_address + 6)

        property_header_address = self.extractor.read_word(starting_address + 7)
        
        property_header = self.load_property_header(property_header_address)
        property_address = property_header["final_address"]
        object_description = property_header["object_description"]
        properties = self.load_properties(property_address)


        z_object = Object(object_index, attributes, parent_obj_num, sibling_obj_num, child_obj_num, properties, object_description)

        return z_object

    def load_property_header(self, starting_address):
        num_descirption_words = self.extractor.read_byte(starting_address)
        description = self.extractor.read_string(starting_address + 1)
        final_address = starting_address + (num_descirption_words * 2) + 1
        # print(description)
        return {"final_address": final_address, "object_description": description}

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
            "property_address": starting_address + 1 + property_index,
            # stored as an array
            "property_data": self.extractor.read_bytes_as_array(starting_address + 1 + property_index, num_property_bytes)
                })
            # print(f"num prop bytes {num_property_bytes}")
            # print(f"prop_num: {property_number}")
            property_index += num_property_bytes + 1 
        return properties
    

    def load_default_properties(self):
        default_properties = ["Properties start at 0, this is a placeholder"]
        start_of_next_property = self.header.start_of_object_property_defaults_table
        start_of_objects_table = self.header.start_of_objects_table
        property_index = 1

        while start_of_next_property != start_of_objects_table:
        # while object_index < 5:
            default_properties.append([self.extractor.read_byte(start_of_next_property), self.extractor.read_byte(start_of_next_property + 1)])
            start_of_next_property += 2
            property_index += 1
        
        return default_properties

    def put_value_in_property(self, object_number, property_number, value):
        for obj in self.objects:
            if obj.object_number == object_number:
                obj.put_value_in_property(property_number, value)
                break
    
    def test_attribute(self, object_number, attribute):
        for obj in self.objects:
            if  obj.object_number == object_number:
                debug(f"obj.attribute_flags {obj.attribute_flags}", "debug")
                return attribute in obj.attribute_flags
    
    def set_attribute(self, object_number, attribute):
        object_to_set_attribute = self.find_object(object_number)
        if object_to_set_attribute.object_number != -1:
            # print(object_to_set_attribute.attribute_flags)
            if attribute not in object_to_set_attribute.attribute_flags:
                object_to_set_attribute.attribute_flags.append(attribute)
        else:
            print(f"Object #{object_number} does not exist, now exiting")
            exit(-1)
    
    def remove_attribute(self, object_number, attribute):
        object_to_set_attribute = self.find_object(object_number)
        if object_to_set_attribute.object_number != -1:
            # print(object_to_set_attribute.attribute_flags)
            if attribute in object_to_set_attribute.attribute_flags:
                object_to_set_attribute.attribute_flags.remove(attribute)
        else:
            print(f"Object #{object_number} does not exist, now exiting")
            exit(-1)
    
    def is_obj_a_the_direct_child_of_obj_b(self,obj_a_number, obj_b_number):
        return(self.find_object(obj_a_number).parent == obj_b_number)

    def find_object(self, object_number):
        for obj in self.objects:
                if obj.object_number == object_number:
                    return obj
        return Object(-1)

    def get_object_description(self, object_number):
        object = self.find_object(object_number)
        return object.object_description

    def get_object_parent(self, object_number):
        object = self.find_object(object_number)
        return object.parent
    
    def get_object_child(self, object_number):
        object = self.find_object(object_number)
        return object.child

    def get_object_sibling(self, object_number):
        object = self.find_object(object_number)
        return object.sibling

    def get_object_property_data(self, object_number, property_number):
        object = self.find_object(object_number)
        property = object.get_property_data(property_number)
        if property == -1:
            property = self.default_properties[property_number]
            # may need to turn the default properties into an array
        return property
    
    def get_object_property_address(self, object_number, property_number):
        object = self.find_object(object_number)
        property = object.get_property_address(property_number)
        if property == -1:
            property = self.default_properties[property_number]
            # may need to turn the default properties into an array
        return property

    def insert_object(self, index_of_object_to_be_moved, index_of_object_destination):
        # object_to_be_moved = None
        # original_parent_of_object_to_be_moved = None
        # original_sibling_of_object_destination = None

        # object_destination = None
        # previous_child_of_object_destination = None
        
        object_to_be_moved = self.find_object(index_of_object_to_be_moved)
        original_parent_of_object_to_be_moved = self.find_object(object_to_be_moved.parent)
        original_sibling_of_object_to_be_moved = self.find_object(object_to_be_moved.sibling)

        object_destination = self.find_object(index_of_object_destination)
        previous_child_of_object_destination = self.find_object(object_destination.child)

        object_destination.child = object_to_be_moved.object_number
        debug(f"object destination {object_destination.object_number} now has child {object_to_be_moved.object_number}")
        if (previous_child_of_object_destination.object_number != -1):
            debug(f"original object {object_to_be_moved.object_number} now has sibling {previous_child_of_object_destination.object_number}")
            object_to_be_moved.sibling = previous_child_of_object_destination.object_number
        if (original_sibling_of_object_to_be_moved.object_number != -1):
            debug(f"original object's parent {original_parent_of_object_to_be_moved.object_number} now has child {original_sibling_of_object_to_be_moved.object_number}")
            original_parent_of_object_to_be_moved.child = original_sibling_of_object_to_be_moved.object_number
        
        debug(f"original object {object_to_be_moved.object_number} now has parent {index_of_object_destination}")
        object_to_be_moved.parent = index_of_object_destination


        
