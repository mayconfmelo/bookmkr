[private]
default:
	@just --list --unsorted

# TODO: Installation command
# install the program.
install:
  echo "Install feature not implemented yet"
  
# TODO: uninstallation command
# removes the program.
remove:
  echo "Remove feature not implemented yet"
  

# test the program.
test init="none" format="epub":
  #!/usr/bin/env bash
  filepath="$(realpath src/bookmkr.py)"
  
  if [[ "{{init}}" == "init" ]]; then
    rm -r test/  2>/dev/null || true
    mkdir test/  2>/dev/null || true
    cd test/
    python $filepath --init
  else
    cd test/
  fi
  
  python $filepath --verbose {{format}}
  
# move changes in test/ to assets/
[private]
deploy:
  rm -r assets/  2>/dev/null || true
  cp -r test/assets/ ./  2>/dev/null || true
  cp test/bookrecipe.toml assets/  2>/dev/null || true
  rm assets/.data.yaml