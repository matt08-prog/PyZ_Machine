# file_exporter.py

class FileExporter:
    def __init__(self, output_file):
        self.output_file = output_file

    def export_hex_data(self, hex_data):
        with open(self.output_file, 'w') as file:
            for address, byte_value in hex_data:
                file.write(f"{address:08x}: {byte_value}\n")
        print(f"    Hex dump exported to {self.output_file}")