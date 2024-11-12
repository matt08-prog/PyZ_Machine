# debuger.py
bcolors = {
    "HEADER": '\033[95m',
    "BLUE": '\033[94m',
    "CYAN": '\033[96m',
    "GREEN": '\033[92m',
    "WARNING": '\033[93m',
    "FAIL": '\033[91m',
    "ENDC": '\033[0m',
    "BOLD": '\033[1m',
    "UNDERLINE": '\033[4m'
}

used_debug_colors = ["HEADER",
    "BLUE",
    "CYAN",
    "GREEN",
    "WARNING",
    "FAIL",
    "ENDC",
    "BOLD",
    "UNDERLINE"]

# used_debug_colors = ["HEADER",
#     "BLUE",
#     "CYAN",
#     "GREEN",
#     "WARNING",
#     "FAIL",
#     "ENDC",
#     "BOLD",
#     "UNDERLINE"]

def debug(debug_string, severity_string="unclassified_severity"):
    if (severity_string != "unclassified_severity") and (severity_string in used_debug_colors):
        print(f"{bcolors[severity_string]}{debug_string}{bcolors["ENDC"]}")

