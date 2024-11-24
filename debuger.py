# debuger.py
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
printed_character_only = 1
print_instructions = 0

def debug(debug_string, severity_string="unclassified_severity", end_string="\n"):
    if instructions_only:
        if (severity_string == "time-stamp-only"):
            print(f"{debug_string}", end=end_string)
    elif not printed_character_only and print_instructions:
        if (severity_string != "unclassified_severity"):
            if (severity_string in used_debug_colors):
                print(f"{bcolors[severity_string]}{debug_string}{bcolors["ENDC"]}", end=end_string)
            elif (severity_string.lower() == "debug" or severity_string == "time-stamp"):
                print(debug_string, end=end_string)
            elif (severity_string.lower() == "cyan"):
                debug_string = debug_string.replace(":", "")
                print(f"{bcolors[severity_string]}{debug_string}{bcolors["ENDC"]}", end=end_string)
    elif printed_character_only:
        if (severity_string.lower() == "cyan" or severity_string.lower() == "bold"):
            start_index = debug_string.index(":") + 1
            debug_string = debug_string[start_index:]
            # debug_string = debug_string.replace(":", "")
            print(f"{bcolors[severity_string]}{debug_string}{bcolors["ENDC"]}", end="")
        elif (severity_string == "CYAN_no_z_string"):
            print(f"{bcolors["CYAN"]}{debug_string}{bcolors["ENDC"]}", end="")


