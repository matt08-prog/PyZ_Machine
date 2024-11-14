# hex_extractor.py

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

from debuger import debug

class HexExtractor:
    def __init__(self, file_path, hex_data, abreviator):
        self.file_path = file_path
        self.hex_data = hex_data
        self.abreviator = abreviator
        self.alphabet = [
            [" ", "", "", "", "", "", 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'],
            [" ", "", "", "", "", "", 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], 
            [" ", "", "", "", "", "", " ", "\n", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ".", ",", "!", "?", "_", "#", "'", "\"", "/", "\\", "-", ":", "(", ")"]
        ]

    def get_init_global_data(self, start_of_global_data_table):
        globals_data = []
        global_data_index = 0
        for global_data_address in range(0, 310, 2):
            read_word = self.read_word(start_of_global_data_table + global_data_address)
            read_word = read_word - (read_word >> 15 << 16)
            globals_data.append(read_word)
            # print(f"globals_data #{global_data_index} = {read_word}")
            global_data_index += 1
        return globals_data

    def extract_hex(self):
        with open(self.file_path, 'rb') as file:
            byte = file.read(1)
            address = 0
            while byte:
                self.hex_data.append((address, byte.hex()))
                address += 1
                byte = file.read(1)
        return self.hex_data
    
    def write_word(self, address, word_to_store):
        if (int.bit_length(word_to_store) > 16):
            print(f"{bcolors.FAIL}The word ({word_to_store:04x}) trying to be written to memory ({address:05x}) is not 16-bits long{bcolors.ENDC}")
            exit(-1)
        self.hex_data[address] = [address, hex((word_to_store & 0xFF00) >> 8)] # should follow hex_data pattern ?
        self.hex_data[address + 1] = [address, hex(word_to_store & 0x00FF)]
        debug(f"\t\tThe word ({word_to_store:04x}) was written to address ({address:05x})", "OKBLUE")

    def write_array_of_words(self, starting_address, word_array):
        word_index = 0
        for word_offset in range(0, len(word_array) * 2, 2):
            word = word_array[word_index]
            self.write_word(starting_address + word_offset, word)
            word_index += 1
    
    def write_byte(self, address, byte_to_store):
        if (int.bit_length(byte_to_store) > 8):
            print(f"{bcolors.FAIL}The byte ({byte_to_store:04x}) trying to be written to memory ({address:05x}) is not 8-bits long{bcolors.ENDC}")
            exit(-1)
        self.hex_data[address] = [address, hex(byte_to_store & 0xFF)]
        debug(f"\t\tThe byte ({byte_to_store:04x}) was written to address ({address:05x})", "OKBLUE")

    
    # returns decimal value of word at given address
    def read_word(self, address):
        return (int(self.hex_data[address][1], base =16) << 8) | (int(self.hex_data[address+1][1], base=16))

    def read_byte(self, address):
        return int(self.hex_data[address][1], base=16)

    def read_bytes(self, address, n):
        result = 0
        for i in range(n):
            byte = self.read_byte(address + i)
            result = (result << 8) | byte
        return result

    def read_bytes_as_array(self, address, n):
        result = []
        for i in range(n):
            byte = self.read_byte(address + i)
            result.append(byte)
        return result

    def load_abreviator(self, abreviator_table):
        self.abreviator_table = abreviator_table

    def read_char(self, character_code):
        if character_code > 31 and character_code < 127:
            return chr(character_code)
        else:
            return "__unknown ZSCII character, may not yet be implemented__"

    def read_string(self, base_address, abreviations_table=None):
        current_address = base_address
        current_alphabet = 0 # A0 = lowercase, A1 = Uppercase, A2 = punctuation
        next_alphabet = 0 # A0 = lowercase, A1 = Uppercase, A2 = punctuation
        z_words = []
        final_string = ""
        should_skip_index = 0
        while True:
            word = self.read_word(current_address)
            next_word = self.read_word(current_address + 2)
            z_word_sign = ((word & 0b1000000000000000) >> 15)
            z_words.append((word & 0b0111110000000000) >> 10)
            z_words.append((word & 0b0000001111100000) >> 5)
            z_words.append(word & 0b0000000000011111)

            for z_word_index in range(len(z_words)):
                if should_skip_index == 0:
                    z_word = z_words[z_word_index]
                    next_z_word = 0
                    if z_word_index < len(z_words) - 1:
                        next_z_word = z_words[z_word_index + 1]
                    else:
                        next_z_word = ((next_word & 0b0111110000000000) >> 10)
                    current_alphabet = next_alphabet
                    if (z_word in [1, 2, 3]):
                        if self.abreviator != None:
                            abreviated_zword = self.abreviator.abreviations_table[32* (z_word - 1) + next_z_word]
                            # print(f"abreviated zword: {z_word} {abreviated_zword}")
                            final_string += abreviated_zword
                            current_alphabet = next_alphabet = 0
                            should_skip_index = 1

                    elif (z_word == 4):
                        next_alphabet = 1
                    elif (z_word == 5):
                        next_alphabet = 2
                    else:
                        if (current_alphabet == 2 and z_word == 6):
                            final_string += "_10_bit_ZSCII_CHAR_ESCAPE_"
                        else:
                            word = self.alphabet[current_alphabet][z_word]
                            final_string += word
                            # print(f"           zword: {word}")

                    if current_alphabet == next_alphabet:
                        current_alphabet = next_alphabet = 0
                else:
                    should_skip_index -= 1
            if (z_word_sign == 1):
                return [final_string, current_address + 2]
            
            z_words = []
            current_address += 2
    
    def string_to_z_characters(self, input_string):
        z_characters = []
        for letter_index in range(len(input_string)):
            letter = input_string[letter_index]
            # for alphabet_index in range(3):
            if letter in self.alphabet[2]:
                # print(f"{letter} in alphabet A2")
                z_characters.append(3) # shift for 1 character to A2
                z_characters.append(self.alphabet[2].index(letter))
            elif letter in self.alphabet[0]:
                # print(f"{letter} in alphabet A0")
                z_characters.append(self.alphabet[0].index(letter))
            # else:
            #     print(f"unknown character {letter} was read from user input, now exiting")
            #     exit(-1)
        return z_characters
    
    def z_characters_to_z_words(self, original_z_characters):
        z_characters = original_z_characters.copy() # making a copy so popping doesn't affect original z_characters array
        z_words = []
        current_z_word = 0x00
        current_z_character = 0b00000
        z_character_index = 0

        while len(z_characters) > 0:
            current_z_character = z_characters.pop()
            assert(current_z_character == current_z_character & 0b11111) # make sure each z character is 5 bytes long
            current_z_word |= (current_z_character << 10) >> (z_character_index * 5) # add current_z_character to the current_z_word
            z_character_index = (z_character_index + 1)
            if z_character_index > 2:
                if len(z_characters) < 3:
                    # print(f"set final z_word bit when there were {len(z_characters)} characters left")
                    current_z_word |= 0x80 # set final word bit
                z_words.append(current_z_word)
                current_z_word = 0x00
                z_character_index = 0
        return z_words