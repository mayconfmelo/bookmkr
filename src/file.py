import utils
import __main__

# Recursivelly search for file in parent folders.
def find(file, current_dir=None):
    import os
  
    # If no current_dir, set it to $PWD
    if current_dir is None:
        current_dir = os.getcwd()
  
    # Set full path
    file_path = os.path.join(current_dir, file)

    if os.path.isfile(file_path):
        if __main__.args.verbose: utils.log("m", "Found file:", f"{file_path}")
        return file_path
        
    # Stop searching if current_dir is the root directory
    if current_dir == os.path.dirname(current_dir):
        utils.log("e", "File not found:", f"{file}")
        return None

    # If not found, search again in parent directory
    return find(file, os.path.dirname(current_dir))


# Read TOML file.
def toml(default, local):
    import tomli
    
    try:
        with open(default, 'rb') as default, open(local, 'rb') as local:
            data = tomli.load(default)
            add = tomli.load(local)
            
            # Set custom configurations with falback to defaults:
            
            # List all [table] in file
            tables = set(list(data.keys()) + list(add.keys()))
            
            for table in tables:
                # Add custom [table]
                if not data.get(table, None): data[table] = add[table]
                
                # List all keys inside a [table]
                keys = set(
                    list(data.get(table, {}).keys()) + 
                    list(add.get(table, {}).keys())
                )
                
                for key in keys:
                    defvalue = data.get(table, {}).get(key, None)
                    addvalue = add.get(table, {}).get(key, None)
                    
                    # Set local values in data, maintaining the default ones
                    if addvalue and defvalue != addvalue:
                        data[table][key] = addvalue
            
            return data
        
    except FileNotFoundError:
        utils.log("e", "File not found:", f"{file}")
    except tomli.TOMLDecodeError as e:
        utils.log("e", "TOML decode error:", f"{e}")
    except Exception as e:
        utils.log("e", "TOML error:", f"{e}")


# Write book data.yaml file
def write(content, path):
    with open(path, "w") as file:
        file.write("---\n")
        file.write(content)
        file.write("...")
    
    if __main__.args.verbose: utils.log("m", "Created file:", f"{path}")


# Resolves one or more globs
def globs(globs):
    import glob
    
    if not isinstance(globs, list): globs = [globs]

    result = []
    for pat in globs:
        paths = glob.glob(pat)
        
        for path in sorted(paths):
            result.append(path)
    return result