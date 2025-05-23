#!/usr/bin/env python
# DESC: Build pandoc book based on instructions in .bookrecipe files.
# USAGE: package [OPTIONS]
# TODOC: insert comments


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
else: utils.log("f", "Not a book project!")

# Init a new book
if args.init:
    if cfg_local:
        utils.log("w", "There's a book project here already!")
        exit(1)
    else:
        import shutil
        
        # Copy assets/ to $PWD
        shutil.copytree(proj_dir + "/assets/", "./assets/")
        utils.log("m", "Created folder:", "assets/")
        
        # Move cfg_file from $PWD/assets/ to $PWD
        shutil.move("./assets/" + cfg_file, "./")
        utils.log("m", "Created file:", cfg_file)
        
        # Create a bolerplate initial content file
        with open("./01.md", "w") as file:
            file.write("# Introduction\n\n")
          
        utils.log("s", "Book project initialized!")
        exit(0)


# Anort if not in a book project directory
if not cfg_local:
    utils.log("f", "Not a book project")
    exit(2)


# Book configurations
cfg = file.toml(cfg_default, cfg_local)

if args.format: cfg['general']['filetype'] = args.format

# Write .data.yaml file in assets/
file.write(
  yaml.dump(cfg["book"]),
  os.path.dirname(cfg_local) + "/assets/.data.yaml"
)

if args.verbose:
    utils.log("m", "Book title:", f"{cfg['book']['title']}")
    utils.log("m", "Book format:", f"{cfg['general']['filetype']}")


# Collect CLI flags/arguments
flags = ""
for key, value in cfg["pandoc"]["flags"].items():
    flags += f"--{key}={value} "

if cfg['general']['filetype'] == 'pdf':
    flags += ""


# Get the relative outpit directory
output_dir = os.path.join(
    os.path.relpath(os.path.dirname(cfg_local)),
    cfg['general']['output']
)
if not os.path.isdir(output_dir): os.mkdir(output_dir)


# Get the relative output path (directory and file name):
output = os.path.join(
    output_dir,
    cfg['book']['title'] + "." + cfg['general']['filetype']
)


# Generates the pandoc command:
command = "pandoc "
command += f"--output='{output}' "
command +=  "--metadata-file='assets/.data.yaml' "
command += f"{flags}"
command += " ".join(sorted(glob.glob(cfg["general"]["sources"])))

if args.loop:
    import time
    utils.log("m", f"Continuous building mode ({args.sleep_time}s)")

while True:
    if args.verbose: utils.log("o", "Building book...", )
    
    # Optional command executed before pandoc
    if cfg['general'].get('cmd-before'):
        utils.run(cfg['general']['cmd-before'])
    
    # Execute the pandoc command
    try: utils.run(command)
    except Exception as e: utils.log("e", "\nError:", e)
    
    if args.verbose: print("OK")
    
    # Optional command executed after pandoc
    if cfg['general'].get('cmd-after'):
        utils.run(cfg['general']['cmd-after'])
    
    # Sleep (loop) or end the program
    if args.loop:
        try: time.sleep(args.sleep_time)
        
        except KeyboardInterrupt:
            if args.verbose: utils.log("w", "Stoping continuous mode.")
            exit(0)
    else: break
