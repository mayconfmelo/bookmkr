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
parser.add_argument("-v", "--verbose", action="store_true", help="enables veebose mode.")
parser.add_argument("-l", "--loop", action="store_true", help="enables infinite loop.")
parser.add_argument("-s", "--sleep-time", type=float, default=1.0, help="set time between each build in loop mode (default: 1.0)")
parser.add_argument("-i", "--init", action="store_true", help="initialize a new book project.")
parser.add_argument("format", nargs="?", help="set the book format.")
# CLI arguments
args = parser.parse_args()


proj_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Configuration file
cfg_file = 'bookrecipe.toml'
cfg_default = proj_dir + "/assets/" + cfg_file
cfg_local = file.find(cfg_file)

if cfg_local: os.chdir(os.path.dirname(cfg_local))

# Init a new book
if args.init:
    if cfg_local:
        utils.log("w", "There's a book project here already!")
        exit(1)
    else:
        import shutil
        
        # Copy assets/ to $PWD
        shutil.copytree(f"{proj_dir}/assets/", "./assets/")
        utils.log("m", "Created folder:", "assets/")
        
        # Move cfg_file from $PWD/assets/ to $PWD
        shutil.move(f"./assets/{cfg_file}", "./")
        utils.log("m", "Created file:", cfg_file)
        
        # Move 01.md from $PWD/assets/ to $PWD
        shutil.move("./assets/01.md", "./")
        with open(f"{proj_dir}/README.md", 'r', encoding='UTF-8') as readme:
            readme = readme.read()
            readme = readme.replace("# ", "## ")
        with open("01.md", 'a', encoding='UTF-8') as init:
            init.write("\n\n\n# Documentation\n\n\n")
            init.write(readme)
        utils.log("m", "Created file:", "01.md")
        
        # Move 01.md from $PWD/assets/ to $PWD
        shutil.move("./assets/gitignore", "./.gitignore")
        utils.log("m", "Created file:", ".gitignore")
        
        out = utils.run(f'git init .', get_output=True)
        utils.run(f'git config --global --add safe.directory .')
        utils.run(f'git add .')
        out += utils.run(f'git commit -m "Book initialized!"', get_output=True)
        utils.log("m", "Created Git repository:", out)
        
        utils.log("s", "Book project initialized!")
        print()
        
        exit(0)


# Abort if not in a book project directory
if not cfg_local:
    utils.log("f", "Not a book project")
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

if args.verbose:
    utils.log("m", "Book title:", f"{cfg.book.title}")
    utils.log("m", "Book format:", f"{cfg.general.format}")


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
    utils.log("m", f"Continuous building mode ({args.sleep_time}s)")

while True:
    # Optional command executed before pandoc
    if cfg.general.get("cmd-before"):
        cmd_before = cfg.general["cmd-before"]
        
        if args.verbose: utils.log("w",
          "Running pre-generation command:", cmd_before
        )
        
        os.chdir(os.path.dirname(cfg_local))
        
        try:
            out = utils.run(cmd_before, get_output=True)
            if args.verbose: 
                utils.pad(out, wraplines=False)
                print()
        except Exception as e: utils.log("e", "Pre-generation:", e)
    
    if args.verbose: utils.log("o", "Building book...", )
    
    # Execute the pandoc command
    try: utils.run(command)
    except Exception as e: utils.log("e", "Execution failed:", e)
    if args.verbose: print("OK\n")
    
    
    # Optional command executed after pandoc
    if cfg.general.get('cmd-after'):
        cmd_after = cfg.general['cmd-after']
        
        if args.verbose: utils.log("w",
          "Running post-generation command:", cmd_after
        )
        
        os.chdir(os.path.dirname(cfg_local))
        
        try:
            out = utils.run(cmd_after, get_output=True)
            if args.verbose:
              utils.pad(out, wraplines=False)
              print()
        except Exception as e: utils.log("e", "Post-generation:", e)
    
    
    # Sleep (loop) or end the program
    if args.loop:
        try: time.sleep(args.sleep_time)
        
        except KeyboardInterrupt:
            if args.verbose: utils.log("w", "Stoping continuous mode.")
            exit(0)
    else: break


if args.verbose: utils.log("s", "Book created:", os.path.relpath(output))