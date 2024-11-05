# header.py
from hex_extractor import HexExtractor

class Header:
    def __init__(self, hex_data, extractor):
        self.hex_data = hex_data
        self.extractor = extractor
        self.start_of_abreviations_address_table = self.extractor.read_word(0x18)

    def output_header_info(self):
        # Print number of bytes
        print(f"Number of bytes (including EOF): {len(self.hex_data)} (0x{len(self.hex_data):08x})")
        print(f"0x0e - static memory base: {self.hex_data[0X0e]}")
        print(f"0x18 - abbreviations table address: {self.start_of_abreviations_address_table}")