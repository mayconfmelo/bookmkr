
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
            print(f"{WHITE}[MESSAGE]{RESET} {msg}", flush=True)
        case "s":
            print(f"{GREEN}[SUCCESS]{RESET} {msg}", flush=True)
        case "o":
            print(f"{BLUE}[ONGOING]{RESET} {msg}", flush=True, end="")
        case "w":
            print(f"{YELLOW}[WARNING]{RESET} {msg}", flush=True)
        case "e":
            print(f"{RED}[ ERROR ]{RESET} {msg}", flush=True)
        case "f":
            print(f"{RED}[ FATAL ]{RESET} {msg}", flush=True)
            exit(data)
        case _:
            print(f"{RED}[ ERROR ]{RESET} Wrong log type \"{type}\" for message \"{msg}\".")

    if data is not None:
        print(MAGENTA, end="")
        pad(data, wraplines=False)
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
            print()
            log("e", "Command execution failed: ", result.stderr)
            exit(1)
            
        if not get_output and result.stdout != "": print(result.stdout)
        elif get_output: return result.stdout
            

# Generates left-padded paragraphs of text in terminal
def pad(text, n=9, wraplines=True):
    import textwrap
    import shutil

    width = shutil.get_terminal_size().columns - (n + 1)

    lines = []
    if wraplines == False and '\n' in text.strip(): 
      for part in text.split('\n'):
          for line in textwrap.wrap(part, width=width): lines.append(line)
    else: lines = textwrap.wrap(text, width=width)
    
    for line in lines:
        print(" " * n, line.ljust(width))
    

# Allows to access dict["foo"] as dict.foo
class DictAttr(dict):
    def __getattr__(self, attr):
        value = self.get(attr)
        if isinstance(value, dict) and not isinstance(value, DictAttr):
            value = DictAttr(value)
            self[attr] = value
        return value

    def __setattr__(self, attr, value):
        parts = attr.split(".")
        current = self
        for part in parts[:-1]:
            if part not in current or not isinstance(current[part], dict):
                current[part] = DictAttr()
            elif not isinstance(current[part], DictAttr):
                current[part] = DictAttr(current[part])
            current = current[part]
        last_part = parts[-1]
        if isinstance(value, dict) and not isinstance(value, DictAttr):
            value = DictAttr(value)
        current[last_part] = value

    def __delattr__(self, attr):
        try:
            del self[attr]
        except KeyError:
            raise AttributeError(f"No such attribute: {attr}")