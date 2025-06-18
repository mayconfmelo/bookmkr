import __main__

def find(file, current_dir=None):
    """Recursivelly search for file in parent folders."""
    
    import os
  
    # If no current_dir, set it to $PWD
    if current_dir is None:
        current_dir = os.getcwd()
  
    # Set full path
    file_path = os.path.join(current_dir, file)

    if os.path.isfile(file_path):
        __main__.log.m("Found file:", str(file_path))
        return file_path
        
    # Stop searching if current_dir is the root directory
    if current_dir == os.path.dirname(current_dir):
        __main__.log.e("File not found:", str(file))
        return None

    # If not found, search again in parent directory
    return find(file, os.path.dirname(current_dir))


def toml(default, local):
    """Read TOML file and return its dictionary."""
    
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
        __main__.log.e("File not found:", f"{file}")
    except tomli.TOMLDecodeError as e:
        __main__.log.f("TOML decode error:", f"{e}", code=4)
    except Exception as e:
        __main__.log.f("TOML error:", f"{e}", code=4)


def write(content, path):
    """Write temporary assets/.data.yaml file."""
    
    import os
    
    try:
        with open(path, "w") as file:
            file.write("---\n")
            file.write(content)
            file.write("...")
    except FileNotFoundError as e:
        __main__.log.f("Temporary file not found:", path, code=3)
    except Exception as e:
        __main__.log.f("Could not write metadata:", e, code=3)
    
    __main__.log.m("Created file:", f"{path.replace(os.getcwd() + "/", "")}")


def globs(globs):
    """Resolves one or more globs, in order."""
    
    import glob
    
    if not isinstance(globs, list): globs = [globs]

    result = []
    for pat in globs:
        paths = glob.glob(pat)
        
        for path in sorted(paths):
            result.append(path)
    return result