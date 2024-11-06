# main.py

import sys
from hex_extractor import HexExtractor
from file_exporter import FileExporter
from abreviator import Abreviator
from header import Header
from routine import Routine
from operand import Operand

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = f"{input_file}_hex_dump.txt"
    hex_data = [] # tuple in format (decimal_index, byte_value) where each entry represents a byte of data

    # Extract hex data
    extractor = HexExtractor(input_file, hex_data)
    hex_data = extractor.extract_hex()

    # Initiate sub-modules
    exporter = FileExporter(output_file)
    header = Header(hex_data, extractor)
    abreviator = Abreviator(hex_data, extractor, header)


    # Export hex data to file
    exporter.export_hex_data(hex_data)
    abreviator.print_abreviations()

    # Display header data
    header.output_header_info()

    # get first routine
    routine = Routine(extractor, header.initial_execution_point - 1)


if __name__ == "__main__":
    main()