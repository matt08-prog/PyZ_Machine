# main.py

from hex_extractor import HexExtractor
from file_exporter import FileExporter
from abreviator import Abreviator
from header import Header
from routine import Routine
from instruction import Instruction
from routine_interpreter import RoutineInterpreter
from object_loader import ObjectLoader

import argparse

def main():
    max_time_step = 0

    #input parsing
    parser = argparse.ArgumentParser(description="Process input file with optional abbreviations table.")
    parser.add_argument("-a", "--abbreviations", action="store_true", help="Output abbreviations table")
    parser.add_argument("-x", "--hexdump", action="store_true", help="Write hexdump of input to a file")
    parser.add_argument("-mts", "--should_look_for_max_time_step", action="store_true", help="Write hexdump of input to a file")
    parser.add_argument("input_file", help="Input file to process")
    parser.add_argument("max_time_step", help="maximum number of instructions to process")

    args = parser.parse_args()

    should_output_abbreviations_table = args.abbreviations
    should_dump_input_file = args.hexdump
    input_file = args.input_file
    if args.should_look_for_max_time_step:
        max_time_step = int(args.max_time_step)
    else:
        max_time_step = 0
    output_file = f"{input_file}_hex_dump.txt"


    hex_data = [] # tuple in format (decimal_index, byte_value) where each entry represents a byte of data

    # Extract hex data
    extractor = HexExtractor(input_file, hex_data)
    hex_data = extractor.extract_hex()

    # Initiate sub-modules
    exporter = FileExporter(output_file)
    header = Header(hex_data, extractor)
    abreviator = Abreviator(hex_data, extractor, header)
    objectLoader = ObjectLoader(extractor, header)
    print()
    routine_interpreter = RoutineInterpreter(extractor, header, max_time_step)
    

    # Export hex data to file
    if should_dump_input_file:
        exporter.export_hex_data(hex_data)
    
    # List abreviations table
    if should_output_abbreviations_table:
        abreviator.print_abreviations()

    # Display header data
    header.output_header_info()

    # Tell Interpreter to get first routine
    routine_interpreter.start_interpreting()


if __name__ == "__main__":
    main()