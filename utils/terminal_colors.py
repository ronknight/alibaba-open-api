class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def colorize(text: str, color: str) -> str:
    """Wrap text with color code and end code"""
    return f"{color}{text}{Colors.ENDC}"

def blue(text: str) -> str:
    return colorize(text, Colors.BLUE)

def green(text: str) -> str:
    return colorize(text, Colors.GREEN)

def warning(text: str) -> str:
    return colorize(text, Colors.WARNING)

def fail(text: str) -> str:
    return colorize(text, Colors.FAIL)

def bold(text: str) -> str:
    return colorize(text, Colors.BOLD)

def header(text: str) -> str:
    return colorize(text, Colors.HEADER)

def underline(text: str) -> str:
    return colorize(text, Colors.UNDERLINE)