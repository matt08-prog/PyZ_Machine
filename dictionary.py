# dictionary.py
from hex_extractor import HexExtractor
from instruction import Instruction
# from interpreter import Interpreter
from debuger import Debug

debugger = Debug()

def debug(self, *args, **kwargs):
    debugger.debug(*args, **kwargs)


class Dictionary:
    def __init__(self, header, extractor):
        self.header = header
        self.extractor = extractor
        self.word_seperators = []
        self.individual_enrty_length = 0
        self.num_entries = 0
        dictionary_data_start_address = 0x00000
        get_dictionary_header_data = self.get_dictionary_header_data()
        self.dictionary = self.get_dictionary_data()
        debug(f"word seperators: {self.word_seperators}", "debug")
        # debug(f"word dictionary (length={self.num_entries}, ({len(self.dictionary)})): {self.dictionary}", "debug")


    def get_dictionary_header_data(self):
        dictionary_start_address = self.header.start_of_dictionary_table
        num_word_seperators = self.extractor.read_byte(dictionary_start_address)
        word_seperators = self.extractor.read_bytes_as_array(dictionary_start_address + 1, num_word_seperators)
        word_seperators = [chr(element) for i, element in enumerate(word_seperators)]
        self.individual_enrty_length = self.extractor.read_byte(dictionary_start_address + num_word_seperators + 1)
        self.num_entries = self.extractor.read_word(dictionary_start_address + num_word_seperators + 2)
        self.dictionary_data_start_address = dictionary_start_address + num_word_seperators + 4
        self.packed_dictionary_data_start_address = self.dictionary_data_start_address // 2

    def get_dictionary_data(self):
        dictionary_entry = []
        dictionary = []
        for dictionary_entry_address in range(self.dictionary_data_start_address, self.dictionary_data_start_address + (self.num_entries * self.individual_enrty_length), self.individual_enrty_length):
            # print(f"{dictionary_entry_address:05x}")
            dictionary_string_entry = self.extractor.read_string(dictionary_entry_address)[0] # (4 byte) 2xword z-word entry
            # debug(dictionary_string_entry, "debug")
            dictionary_data_entry = (self.extractor.read_bytes_as_array(dictionary_entry_address + 4, 3)) # (3 byte) data entry
            dictionary.append([dictionary_string_entry, dictionary_data_entry])
            dictionary_entry = []
        return dictionary
    
    def get_dict_address(self, word):
        shortened_word = word[0:6]
        for dict_entry_index, dict_entry in enumerate(self.dictionary):
            if dict_entry[0] == shortened_word:
                # print(f"{(self.packed_dictionary_data_start_address * 2):05x}")
                dict_entry_address = ((dict_entry_index * 7)) + self.dictionary_data_start_address
                return dict_entry_address
        print(f"get_dict_address could not find entry for word \"{shortened_word}\"")
        return 0

    def parse_split_input(self, split_input):
        parsed_input = []
        return parsed_input