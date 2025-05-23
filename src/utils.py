
# Pretty print log messages
def log(type, msg, data=None):
    # ANSI escape codes for text colors
    RED = '\033[31;1m'
    GREEN = '\033[32;1m'
    YELLOW = '\033[33;1m'
    BLUE = '\033[34;1m'
    MAGENTA = '\033[35;1m'
    CYAN = '\033[36;1m'
    WHITE = '\033[37;1m'
    RESET = '\033[0m'

    match type:
        case "m":
            print(f"{GREEN}[MESSAGE]{RESET} {msg}")
        case "s":
            print(f"{GREEN}[SUCCESS]{RESET} {msg}")
        case "o":
            print(f"{BLUE}[ONGOING]{RESET} {msg}", end="")
        case "w":
            print(f"{YELLOW}[WARNING]{RESET} {msg}")
        case "e":
            print(f"{RED}[ ERROR ]{RESET} {msg}")
        case "f":
            print(f"{RED}[ FATAL ]{RESET} {msg}")
            exit(data)
        case _:
            print(f"{RED}[ ERROR ]{RESET} Wrong log type \"{type}\" for message \"{msg}\".")

    if data is not None:
        print(MAGENTA, end="")
        pad(data)
        print(RESET)


# Run one or more shell commands.
def run(cmd, get_output=False):
    import subprocess
    import shlex
  
    # Convert string cmd into list:
    if not isinstance(cmd, (list, tuple)):
        cmd = [cmd]
      
    # Run each command from cmd
    for command in cmd:
        # Break string command into list
        if isinstance(command, str):
            command = shlex.split(command)
            
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.stderr:
            log("e", "Pandoc: ", result.stderr)
            exit(1)
            
        if not get_output and result.stdout != "": print(result.stdout)
        elif get_output: return result.stdout
            

# Generates left-padded paragraphs of text in terminal
def pad(text, n=9):
    import textwrap
    import shutil

    width = shutil.get_terminal_size().columns - (n + 1)

    for line in textwrap.wrap(text, width=width):
        print(" " * n, line.ljust(width))