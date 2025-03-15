def colored(text, color):
    return f"\033[{color}m{text}\033[0m"

def red(text):
    return colored(text, 31)

def green(text):
    return colored(text, 32)

def magenta(text):
    return colored(text, 35)