#!/usr/bin/env python
# DESC: Build Pandoc books based on instructions in bookrecipe.toml files.
# USAGE: bookmkr [OPTIONS] <FORMAT>
# INFO: exit error numbers: 0 = OK, 1 = bookmkr, 2 = subprocess, 3 = file, 4 = unknown

import yaml
import glob
import os
import argparse
import utils
import file


# CLI argument parsing
parser = argparse.ArgumentParser(description="")
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
            readme = readme.read()
            readme = readme.replace("# ", "## ")
        with open("01.md", 'a', encoding='UTF-8') as init:
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
 
 
if cfg_local:
    cfg_local_dir = os.path.dirname(cfg_local)
    os.chdir(cfg_local_dir)
else: log.f("Not a book project", code=2)



# Book configurations
cfg = utils.DictAttr(
    file.toml(cfg_default, cfg_local)
)

if args.format: cfg.general.format = args.format

# Write .data.yaml file in assets/
file.write(
  yaml.dump(cfg["book"]),
  cfg_local_dir + "/assets/.data.yaml"
)
cfg.book.title = cfg.book.title.replace("\\n", " ")
cfg.general.sources = file.globs(cfg.general.sources)

log.m("Book title:", cfg.book.title)
log.m("Book format:", cfg.general.format)


# Collect CLI flags/arguments
pandoc_args = ""
if cfg.general.format == 'pdf': pandoc_args += "--pdf-engine='typst' "
for key, value in cfg.pandoc.args.items():
    if value == 'true': pandoc_args += f'--{key} '
    else: pandoc_args += f'--{key}="{value}" '


# Get the relative output directory
output_dir = os.path.join(
    os.path.relpath(cfg_local_dir),
    cfg.general.output
)
if not os.path.isdir(output_dir): os.mkdir(output_dir)


# Get the relative output path (directory and file name):
output = os.path.join(
    output_dir,
    cfg.book.title + "." + cfg.general.format
)

# Generates the pandoc command:
command = 'a'
command = 'pandoc '
command += f'--output="{output}" '
command +=  '--metadata-file="assets/.data.yaml" '
command += f'{pandoc_args}'
#command += " ".join(sorted( glob.glob(cfg.general.sources) ))
command += " ".join(cfg.general.sources)

# if args.watch:
#     import time
#     log.m(f"Continuous building mode ({args.sleep_time}s)")


# Run cmd-before, command, and cmd-after
def execute():
    # End "Waiting for for changes" with DONE in loop
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
    
    # Execute the pandoc command
    utils.run(command)
    
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
    
    log.m(f"Continuous building mode")

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
        log.w("Stoping continuous mode.")
        exit(0)
    observer.join()
else:
  execute()
  
  if os.path.isfile(output): log.s("Book created:", os.path.relpath(output))
  else: log.f("Error: No book file was generated.", code=2)