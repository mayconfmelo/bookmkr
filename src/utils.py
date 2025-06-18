from watchdog.events import FileSystemEventHandler
import __main__


class Log:
    """Init a logger for pretty print log messages."""

    def __init__(self, flush=True, color=True, verbose=True):
        self.flush = flush
        self.verbose = verbose
        if color:
            self.red = '\033[31;1m'
            self.green = '\033[32;1m'
            self.yellow= '\033[33;1m'
            self.blue = '\033[34;1m'
            self.magenta = '\033[35;1m'
            self.cyan = '\033[36;1m'
            self.white = '\033[37;1m'
            self.reset = '\033[0m'
        else:
            self.red = ''
            self.green = ''
            self.yellow= ''
            self.blue = ''
            self.magenta = ''
            self.cyan = ''
            self.white = ''
            self.reset = ''
    
    def __getattr__(self, name):
        import inspect
        members = inspect.getmembers(self.__class__, predicate=inspect.isfunction)
        methods = []
        
        for name, member in members:
            if not name.startswith('__'):
                methods.append(f"Log.{name}")
                
        methods = ", ".join(methods)
        self.f(f"Does not exist: Log.{name}()", f"Must be one of: {methods}.")
    
    def m(self, msg, data=None):
        """Print a standard log message."""
        
        if not self.verbose: return
        print(f"{self.white}[MESSAGE]{self.reset} {msg}", flush=self.flush)
        if data:
            print(self.magenta, end='')
            pad(data, wraplines=False, end ='')
            print(self.reset)
        print()

    def s(self, msg, data=None):
        """Print a success log message"""
        
        if not self.verbose: return
        print(f"{self.green}[SUCCESS]{self.reset} {msg}", flush=self.flush)
        if data:
            print(self.magenta, end='')
            pad(data, wraplines=False, end ='')
            print(self.reset)
        print()
        
    def o(self, msg):
        """Print ongoing process log message"""
        
        if not self.verbose: return
        print(f"{self.blue}[ONGOING]{self.reset} {msg}", flush=True, end="")
        
    def w(self, msg, data=None):
        """Print warning log message"""
        
        if not self.verbose: return
        print(f"{self.yellow}[WARNING]{self.reset} {msg}", flush=self.flush)
        if data:
            print(self.magenta, end='')
            pad(data, wraplines=False, end ='')
            print(self.reset)
        print()
        
    def e(self, msg, data=None):
        """Print error log message"""
        
        print(f"{self.red}[ ERROR ]{self.reset} {msg}", flush=self.flush)
        if data:
            print(self.magenta, end='')
            pad(data, wraplines=False, end ='')
            print(self.reset)
        print()
        
    def f(self, msg, data=None, code=1):
        """Print fatal log message and anort execution."""
        
        print(f"{self.red}[ FATAL ] {msg}{self.reset}", flush=self.flush)
        if data:
            print(self.magenta, end='')
            pad(data, wraplines=False, end ='')
            print(self.reset)
        exit(code)

    def t(self, msg, data=None):
        """Print a timed log message."""
        from datetime import datetime
        
        if not self.verbose: return
        time = datetime.now().strftime("%H:%M:%S")
        print(f"{self.cyan} {time} {self.reset}{msg}", flush=self.flush)
        if data:
            print(self.magenta, end='')
            pad(data, wraplines=False, end ='')
            print(self.reset)
        print()


class DictAttr(dict):
    """Init a dictionary object that allows to access dict["foo"] as dict.foo"""
    
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

    def dict(self):
        return dict(self)


class WatchHandler(FileSystemEventHandler):
    """Handles modificafions made in one or more paths."""
  
    def __init__(self, callback, files):
        self.callback = callback
        self.files = files
        self.mtimes = {}

    def on_modified(self, event):
        event.src_path = event.src_path.replace(__main__.cfg_local_dir + "/", "")
        
        if not event.is_directory and event.src_path in self.files:
            import os
            
            curr_mtime = os.path.getmtime(event.src_path)
            prev_mtime = self.mtimes.get(event.src_path)
            
            if prev_mtime is None or curr_mtime - prev_mtime > 0.5:
                from datetime import datetime
                
                now = datetime.fromtimestamp(curr_mtime).strftime("%H:%M:%S")
                try: self.callback()
                except Exception as e:
                    __main__.log.f(f"WatchHandler error:", e, code=5)
            self.mtimes[event.src_path] = curr_mtime


def run(cmd, get_output=False, fatal_errors=True):
    """Run one or more shell commands."""
    import subprocess
    import shlex
  
    # Convert string/array cmd into list, unless it's an array of arrays:
    if not isinstance(cmd[0], (list, tuple)):
        cmd = [cmd]
      
    # Run each command from cmd
    for command in cmd:
        # Break string command into list
        if isinstance(command, str):
            command = shlex.split(command)
        
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.stderr:
            print()
            if fatal_errors:
                __main__.log.f("Execution failed:", result.stderr, code=2)
            else: __main__.log.e("Execution failed:", result.stderr)
        else:
            if not get_output and result.stdout != "": print(result.stdout)
            elif get_output: return result.stdout


def pad(text, n=9, wraplines=True, end='\n'):
    """Generates left-padded paragraphs of text in terminal"""
    
    import textwrap
    import shutil

    width = shutil.get_terminal_size().columns - (n + 1)

    lines = []
    #text = " -" * int(width /2) + "-" *width 
    
    text = str(text)
    if wraplines == False and '\n' in text.strip(): 
        for part in text.split('\n'):
            for line in textwrap.wrap(part, width=width): lines.append(line)
    else: 
        lines = textwrap.wrap(text, width=width)
    
    lines[-1] = lines[-1].strip()
    line_end = '\n'
    
    for line in lines:
        if line == lines[-1]: line_end = end
        print(" " * n, line.ljust(width), end=line_end)
        
