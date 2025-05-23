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
test:
  #!/usr/bin/env bash
  
  python ../src/bookmkr.py -v
  
# move changes in test/ to assets/
[private]
deploy:
  rm -r assets/  2>/dev/null || true
  cp -r test/assets/ ./  2>/dev/null || true
  cp test/bookrecipe.toml assets/  2>/dev/null || true
  rm assets/.data.yaml