# hex_extractor.py

class HexExtractor:
    def __init__(self, file_path, hex_data):
        self.file_path = file_path
        self.hex_data = hex_data
        self.alphabet = [
            [" ", "", "", "", "", "", 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'],
            [" ", "", "", "", "", "", 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], 
            [" ", "", "", "", "", "", " ", "^", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ".", ",", "!", "?", "_", "#", "'", "\"", "/", "\\", "-", ":", "(", ")"]
        ]

    def extract_hex(self):
        with open(self.file_path, 'rb') as file:
            byte = file.read(1)
            address = 0
            while byte:
                self.hex_data.append((address, byte.hex()))
                address += 1
                byte = file.read(1)
        return self.hex_data
    
    # returns decimal value of word at given address
    def read_word(self, address):
        return (int(self.hex_data[address][1], base =16) << 8) | (int(self.hex_data[address+1][1], base=16))

    def read_string(self, base_address):
        current_address = base_address
        current_alphabet = 0 # A0 = lowercase, A1 = Uppercase, A2 = punctuation
        next_alphabet = 0 # A0 = lowercase, A1 = Uppercase, A2 = punctuation
        z_words = []
        final_string = ""
        while True:
            word = self.read_word(current_address)
            z_word_sign = ((word & 0b1000000000000000) >> 15)
            z_words.append((word & 0b0111110000000000) >> 10)
            z_words.append((word & 0b0000001111100000) >> 5)
            z_words.append(word & 0b0000000000011111)

            for z_word in z_words:
                current_alphabet = next_alphabet
                if (z_word == 4):
                    next_alphabet = 1
                elif (z_word == 5):
                    next_alphabet = 2
                else:
                    if (current_alphabet == 2 and z_word == 6):
                        final_string += "_10_bit_ZSCII_CHAR_ESCAPE_"
                    else:
                        final_string += self.alphabet[current_alphabet][z_word]

                if current_alphabet == next_alphabet:
                    current_alphabet = next_alphabet = 0
                
            if (z_word_sign == 1):
                return final_string
            
            z_words = []
            current_address += 2