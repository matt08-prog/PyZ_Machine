# abreviator.py
from hex_extractor import HexExtractor
from header import Header

class Abreviator:
    def __init__(self):
        self.num_abreviations = 96 # 96 vor V3+, 32 for V1/V2
        self.abreviations_table = []
        # self.load_abreivations()

    def load_abreivations(self, extractor, header):
        base_addr = header.start_of_abreviations_address_table
        self.abreviation_addresses = []
        address_index = 0

        for address_table_offset in range(0, self.num_abreviations * 2, 2):
            address = extractor.read_word(base_addr + address_table_offset) * 2
            self.abreviation_addresses.append(address)
            abreviation = extractor.read_string(address)[0]
            self.abreviations_table.append(abreviation)
            print(f"    abreviation: \"{abreviation}\"")
            address_index += 1
        print(f"self.abreviations_table: {self.abreviations_table}")
    
    def print_abreviations(self):
        for address_index in range(len(self.abreviation_addresses)):
            abreviation_address = self.abreviation_addresses[address_index]
            print(f"address of abreviation {address_index}: {abreviation_address} ({abreviation_address:02x})")