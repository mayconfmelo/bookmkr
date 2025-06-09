#!/usr/bin/env python
# DESC: Build Pandoc books based on instructions in bookrecipe.toml files.
# USAGE: bookmkr [OPTIONS] <FORMAT>

# TODO: Implement min-book commands in md files through Perl filters


import yaml
import glob
import os
import argparse
import utils
import file


# CLI argument parsing
parser = argparse.ArgumentParser(description="")
parser.add_argument(
    "-v", "--verbose", 
    help="enables verbose mode.", action="store_true"
)
parser.add_argument(
    "-l", "--loop", const=1.0,
    help="enables infinite loop.", type=float, nargs='?'
)
parser.add_argument(
    "-s", "--sleep-time",
    help="set time between each build in loop mode (default: 1.0)",
    type=float, default=1.0
)
parser.add_argument(
    "-i", "--init",
    help="initialize a new book project.", action="store_true",
)
parser.add_argument(
    "-c", "--color", default=True,
    help="initialize a new book project.", action=argparse.BooleanOptionalAction
)
parser.add_argument(
    "format",
    help="set the book format.", nargs="?",
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

if cfg_local: os.chdir(os.path.dirname(cfg_local))

# Init a new book
if args.init:
    log = utils.Log(verbose=True)
    
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


# Abort if not in a book project directory
if not cfg_local:
    log.f("Not a book project")
    exit(2)


# Book configurations
cfg = utils.DictAttr(
    file.toml(cfg_default, cfg_local)
)

if args.format: cfg.general.format = args.format

# Write .data.yaml file in assets/
file.write(
  yaml.dump(cfg["book"]),
  os.path.dirname(cfg_local) + "/assets/.data.yaml"
)
cfg.book.title = cfg.book.title.replace("\\n", " ")

log.m("Book title:", f"{cfg.book.title}")
log.m("Book format:", f"{cfg.general.format}")


# Collect CLI flags/arguments
flags = ""
if cfg.general.format == 'pdf': flags += "--pdf-engine='typst' "
for key, value in cfg.pandoc.flags.items():
    if value == 'true': flags += f'--{key} '
    else: flags += f'--{key}="{value}" '


# Get the relative output directory
output_dir = os.path.join(
    os.path.relpath(os.path.dirname(cfg_local)),
    cfg.general.output
)
if not os.path.isdir(output_dir): os.mkdir(output_dir)


# Get the relative output path (directory and file name):
output = os.path.join(
    output_dir,
    cfg.book.title + "." + cfg.general.format
)

# Generates the pandoc command:
command = 'pandoc '
command += f'--output="{output}" '
command +=  '--metadata-file="assets/.data.yaml" '
command += f'{flags}'
#command += " ".join(sorted( glob.glob(cfg.general.sources) ))
command += " ".join(file.globs(cfg.general.sources))

if args.loop:
    import time
    log.m(f"Continuous building mode ({args.sleep_time}s)")

while True:
    # Optional command executed before pandoc
    if cfg.general.get("cmd-before"):
        cmd_before = cfg.general["cmd-before"]
        
        log.w("Running pre-generation command:", cmd_before)
        
        os.chdir(os.path.dirname(cfg_local))
        
        out = utils.run(cmd_before, get_output=True)
        if args.verbose and out != '': 
            utils.pad(out, wraplines=False)
            print()
    
    
    log.o("Building book...", )
    
    # Execute the pandoc command
    utils.run(command)
    if args.verbose and not args.loop: print("OK\n")
    
    
    # Optional command executed after pandoc
    if cfg.general.get('cmd-after'):
        cmd_after = cfg.general['cmd-after']
        
        log.w("Running post-generation command:", cmd_after)
        
        os.chdir(os.path.dirname(cfg_local))
        
        out = utils.run(cmd_after, get_output=True)
        if args.verbose and out != '':
          utils.pad(out, wraplines=False)
          print()
    
    
    # Sleep (loop) or end the program
    if args.loop:
        try: time.sleep(args.loop)
        
        
        except KeyboardInterrupt:
            log.w("Stoping continuous mode.")
            exit(0)
    else: break


log.s("Book created:", os.path.relpath(output))