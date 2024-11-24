# debuger.py
import os


bcolors = {
    "HEADER": '\033[95m',
    "BLUE": '\033[94m',
    "OKBLUE": '\033[94m',
    "CYAN": '\033[96m',
    "GREEN": '\033[92m',
    "WARNING": '\033[93m',
    "FAIL": '\033[91m',
    "ENDC": '\033[0m',
    "BOLD": '\033[1m',
    "UNDERLINE": '\033[4m'
    # "time-stamp": '\033[4m'
}

used_debug_colors = [
    "HEADER",
    "BLUE",
    "OKBLUE",
    # "CYAN", # special case for outputting to terminal
    "GREEN",
    "WARNING",
    "FAIL",
    "ENDC",
    "BOLD",
    "UNDERLINE"]

instructions_only = 0
printed_character_only = 0
print_instructions = 1

class Debug:
    _instance = None

    def __new__(cls, gui_queue=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, gui_queue=None):
        if gui_queue != None:
            self.gui_queue = gui_queue

    def debug(self, debug_string, severity_string="unclassified_severity", end_string="\n"):
        if severity_string == "unclassified_severity":
            return
        # print(f"debug request, debug({debug_string}, {severity_string})")
        translated_debug_colors = {
            "HEADER": "MediumPurple1",
            "OKBLUE": "DodgerBlue3", # or turquoise1
            "OKCYAN": "cyan",
            "CYAN": "cyan", 
            "GREEN": "green2",
            "WARNING": "yellow",
            "FAIL": "red",
            "ENDC": "white",
            "time-stamp": "white",
            "time-stamp-only": "white",
            "BOLD": "white", # specail
            "UNDERLINE": "white" # special
        }

        text_location = "left" # left or right
        text = debug_string # text to display
        text_color = "white"

        if severity_string == "time-stamp-only" and not instructions_only:
            return

        if severity_string in translated_debug_colors.keys():
            text_color = translated_debug_colors[severity_string]

        if (severity_string.lower() == "cyan"):
            start_index = debug_string.index(":") + 1
            text = debug_string[start_index:]
            text_color = "cyan"
            text_location = "left"
            end_string = ""
        elif severity_string.lower() == "bold":
            start_index = debug_string.index(":") + 1
            text = debug_string[start_index:]
            text_color = "white"
            text_location = "left"
            end_string = ""
        elif severity_string == "CYAN_no_z_string":
            text_color = "cyan"
            text_location = "left"
            end_string = ""
        elif (severity_string != "unclassified_severity"):
            if (severity_string in used_debug_colors):
                text = debug_string
                text_location = "right"
            elif (severity_string.lower() == "debug" or severity_string == "time-stamp"):
                text = debug_string
                text_location = "right"
        elif severity_string == "unclassified_severity":
            print(f"\"unclassified_severity\" was sent to debugger")
            os._exit(1)
            

        text_data_object = {
            "text_location": text_location,
            "text": text + end_string,
            "text_color": text_color
        }

        self.gui_queue.put(text_data_object)
        # if instructions_only:
        #     if (severity_string == "time-stamp-only"):
        #         print(f"{debug_string}", end=end_string)
        # elif not printed_character_only and print_instructions:
        #     if (severity_string != "unclassified_severity"):
        #         if (severity_string in used_debug_colors):
        #             print(f"{bcolors[severity_string]}{debug_string}{bcolors["ENDC"]}", end=end_string)
        #         elif (severity_string.lower() == "debug" or severity_string == "time-stamp"):
        #             print(debug_string, end=end_string)
        #         elif (severity_string.lower() == "cyan"):
        #             debug_string = debug_string.replace(":", "")
        #             print(f"{bcolors[severity_string]}{debug_string}{bcolors["ENDC"]}", end=end_string)
        # elif printed_character_only:
        #     if (severity_string.lower() == "cyan" or severity_string.lower() == "bold"):
        #         start_index = debug_string.index(":") + 1
        #         debug_string = debug_string[start_index:]
        #         # debug_string = debug_string.replace(":", "")
        #         print(f"{bcolors[severity_string]}{debug_string}{bcolors["ENDC"]}", end="")
        #     elif (severity_string == "CYAN_no_z_string"):
        #         print(f"{bcolors["CYAN"]}{debug_string}{bcolors["ENDC"]}", end="")


