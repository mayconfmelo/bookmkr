#!/usr/bin/env python
# DESC: Build Pandoc books based on instructions in bookrecipe.toml files.
# USAGE: bookmkr [OPTIONS] [FORMAT]

import yaml
import glob
import os
import argparse
import utils
import file


# CLI argument parsing
parser = argparse.ArgumentParser(
    description="Build Pandoc books based on instructions in bookrecipe.toml files.",
    usage="%(prog)s [OPTIONS] [FORMAT]",
    epilog="""
        Exit codes used: 0 = OK, 1 = bookmkr error, 2 = subprocess error,
        3 = path error, 4 = TOML, 5 = WatchHandler, 7+ = others.
    """
)
parser.add_argument(
    "format",
    help="set the book format.", nargs="?",
)
parser.add_argument(
    "-i", "--init",
    help="initialize a new book project.", action="store_true",
)
parser.add_argument(
    "-w", "--watch",
    help="enables infinite loop.", action='store_true',
)
parser.add_argument(
    "-v", "--verbose", 
    help="enables verbose mode.", action="store_true"
)
parser.add_argument(
    "-c", "--color", default=True,
    help="set colored text status.", action=argparse.BooleanOptionalAction
)
parser.add_argument(
    "--auto-cover", default=True,
    help="set colored text status.", action=argparse.BooleanOptionalAction
)
# CLI arguments
args = parser.parse_args()

# Init terminal logger
log = utils.Log(
    verbose=args.verbose,
    color=args.color
)


proj_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Configuration file
cfg_file = 'bookrecipe.toml'
cfg_default = proj_dir + "/assets/" + cfg_file
cfg_local = file.find(cfg_file)


# Init a new book
if args.init:
    log = utils.Log(
        verbose=True,
        color=args.color
    )
    
    if not cfg_local:
        import shutil
        
        # Copy assets/ to $PWD
        shutil.copytree(f"{proj_dir}/assets/", "./assets/")
        log.m("Created folder:", "assets/")
        
        # Move cfg_file from $PWD/assets/ to $PWD
        shutil.move(f"./assets/{cfg_file}", "./")
        log.m("Created file:", cfg_file)
        
        # Move 01.md from $PWD/assets/ to $PWD
        shutil.move("./assets/01.md", "./")
        with open(f"{proj_dir}/README.md", 'r', encoding='UTF-8') as readme:
            # Opens the bookmkr README.md file
            readme = readme.read()
            # Change the title to level 1 markdown
            readme = readme.replace("# Book Maker", "## Book Maker")
        with open("01.md", 'a', encoding='UTF-8') as init:
            # Insert the README.md content into the default 01.md as "Documentation"
            init.write("\n\n\n# Documentation\n\n\n")
            init.write(readme)
        log.m("Created file:", "01.md")
        
        # Move 01.md from $PWD/assets/ to $PWD
        shutil.move("./assets/gitignore", "./.gitignore")
        log.m("Created file:", ".gitignore")
        
        out = utils.run(f'git init .', get_output=True)
        utils.run(f'git config --global --add safe.directory .')
        utils.run(f'git add .')
        out += utils.run(f'git commit -m "Book initialized!"', get_output=True)
        log.m("Created Git repository:", out)
        
        log.s("Book project initialized!")
        
        exit(0)
    else:
        log.w("There's a book project here already!")
        exit(1)
 

# Set project directory based on bookrecipe.toml location
if cfg_local:
    cfg_local_dir = os.path.dirname(cfg_local)
    os.chdir(cfg_local_dir)
else: log.f("Not a book project", code=1)


# Book configurations
cfg = utils.DictAttr(
    file.toml(cfg_default, cfg_local)
)
cfg.book.title = cfg.book.title.replace("\\n", " ")
cfg.general.sources = file.globs(cfg.general.sources)
# Overwrite bookrecipe.toml format for the CLI bookmkr [FORMAT], if any:
if args.format: cfg.general.format = args.format

# Log book metadata
data = ""
if args.verbose:
    import string
    
    for key,val in [*cfg.book.items(), *cfg.general.items()]:
        if isinstance(val, list): val = "\n  " + "\n  ".join(str(i) for i in val)
        else: val = str(val)
        
        key = key.replace("-", " ")
        data += f"{string.capwords(key)}: {val}\n"

log.m("Book data retrieved:", data)


# Generate automatic cover using min-book (Typst)
if cfg.book.get('cover', 'auto') != 'none' and args.auto_cover and cfg.general.format != 'pdf':
    import tempfile
    import shutil
    import glob
    import os
    
    log.o("Generating automatic cover...")
    
    # Set subtitle, if any
    subtitle = ""
    if cfg.book.get('subtitle', None): subtitle = f'"{cfg.book.subtitle}"'
    else: subtitle = "none"
    
    # Set authors
    authors = ""
    if not isinstance(cfg.book.author, list): cfg.book.author = [ cfg.book.author ]
    for aut in cfg.book.author:
        authors = authors + f'"{aut}",'
    
    # Set configurations
    configs = ""
    config = cfg.book.cfg
    if config == None: config = []
    elif not isinstance(config, list): config = [ config ]
    config.append({'name': 'cover-back', 'value': 'false'})
    for conf in config:
        if conf == None: continue
        configs = configs + f"{conf['name']}: {conf['value']},"
    if not configs == '': configs = f"({configs})"
    else: configs = f"(:)"
    
    # Write Typst temp file
    with tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix='.txt') as tmp:
        tmp.write(f"""
          #import "@preview/min-book:1.1.0": book

          #show: book.with(
            title: "{cfg.book.title}",
            subtitle: {subtitle},
            edition:  {cfg.book.get('edition', '0')},
            volume:  {cfg.book.get('volume', '0')},
            authors:  ({authors}),
            date:  {cfg.book.get('date', 'datetime.today()')},
            cfg: {configs},
            titlepage: none,
            toc: false,
          )
        """)
        tmp_file = tmp.name
    
    utils.run("typst compile " + tmp_file + " cover{p}.png")
    
    cfg.book['cover-image'] = 'assets/cover.png'
    
    shutil.move('cover1.png', cfg.book['cover-image'])
    for png in glob.glob('cover*.png'): os.remove(png)
    if args.verbose: print("DONE\n")
    # with open(tmp_file, 'r') as f: print(f.read())
    
    os.unlink(tmp_file)
    

# Collect Pandoc flags/arguments
pandoc_args = ""
if cfg.general.format == 'pdf': pandoc_args += "--pdf-engine='typst' "
for key, value in cfg.pandoc.args.items():
    if value == 'true': pandoc_args += f'--{key} '
    elif key == 'css': cfg.book.css = value
    else: pandoc_args += f'--{key}="{value}" '

# Handle missing templates
if cfg.pandoc.args.template:
    if cfg.general.format == 'pdf' and cfg.pandoc.args.get('pdf-engine'):
        format = cfg.pandoc.args.get('pdf-engine')
    else: format = cfg.general.format
    
    template_path = cfg.pandoc.args.template + "." + format
    
    if not os.path.isfile(template_path):
        log.e("Template file not found")
        
        # Gather supported formats
        formats = utils.run("pandoc --list-output", get_output=True)
        formats = formats.strip().split("\n")
        
        if cfg.general.format in formats:
            # Get default template for cfg.general.format
            template = utils.run(f"pandoc -D {cfg.general.format}", get_output=True)
            
            with open(template_path, 'w') as template_file:
                template_file.write(template)
                
            log.w("Fallback to default template:", template_path)
        else:
            log.f(f"Format not supported by Pandoc: {cfg.general.format}")
    else:
        log.m("Template file found:", template_path)


# Write .data.yaml file in assets/
file.write(
  content=yaml.dump(cfg.book.dict()),
  path=f'{cfg_local_dir}/assets/.data.yaml'
)


# Get the output directory
output_dir = os.path.join(
    os.path.relpath(cfg_local_dir),
    cfg.general.output
)
if not os.path.isdir(output_dir): os.mkdir(output_dir)


# Get the output full path (directory and file name):
output = os.path.join(
    output_dir,
    cfg.book.title + "." + cfg.general.format
)

# Generates the pandoc command:
command = 'pandoc '
command += f'--output="{output}" '
command += f'--write="{cfg.general.format}" '
command += f'--metadata-file="{cfg_local_dir}/assets/.data.yaml" '
command += f'{pandoc_args}'
#command += " ".join(sorted( glob.glob(cfg.general.sources) ))
command += " ".join(cfg.general.sources)


# Run cmd-before, command, and cmd-after
def execute():
    # End previous "Waiting for for changes" when in loop
    if args.watch: print("DONE")
  
    # Optional command executed before pandoc
    if cfg.general.get("cmd-before"):
        cmd_before = cfg.general["cmd-before"]
        
        log.w("Running pre-generation command:", cmd_before)
        os.chdir(cfg_local_dir)
        out = utils.run(cmd_before, get_output=True)
        
        if args.verbose and out != '': 
            utils.pad(out, wraplines=False)
            print()
    
    
    # Verbose changes between bookmkr and bookmkr --watch
    if args.watch:
        from datetime import datetime
        now = f": {datetime.now().strftime("%H:%M:%S")}"
        points = "........."
    else:
        now = ""
        points = "..."
        
    log.o(f"Building book" + points)
    
    # Execute the main pandoc command
    utils.run(command)
    
    # Handles bookmkr and bookmkr --watch logs
    if args.verbose or args.watch: print(f"DONE{now}\n")
    if args.watch: log.o("Waiting for changes...")
    
    
    # Optional command executed after pandoc
    if cfg.general.get('cmd-after'):
        cmd_after = cfg.general['cmd-after']
        
        log.w("Running post-generation command:", cmd_after)
        os.chdir(cfg_local_dir)
        out = utils.run(cmd_after, get_output=True)

        if args.verbose and out != '':
          utils.pad(out, wraplines=False)
          print()


# When bookmkr --watch
if args.watch:
    from watchdog.observers import Observer
    import time
    
    # Init a new log with verbose=True
    log = utils.Log(
        verbose=True,
        color=args.color
    )
    
    log.m(f"Continuous building mode", "Rebuild the book on every change in the sources")

    # Event handler runs execute() when a file in cfg.general.sources is modified
    event_handler = utils.WatchHandler(execute, cfg.general.sources)
    observer = Observer()
    observer.schedule(event_handler, cfg_local_dir, recursive=True)
    observer.start()
    
    log.o("Waiting for changes...")
    # Trap the execution in an infinite loop
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print()
        log.w("Continuous building mode stoped.")
        exit(0)
    observer.join()
else:
  execute()
  
  if os.path.isfile(output): log.s("Book created:", os.path.relpath(output))
  else: log.f("Error: No book file was generated.", code=3)