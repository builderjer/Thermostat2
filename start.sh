#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Check for the correct version of python
if ! python3 -c 'import sys; assert sys.version_info >= (3,7)' &> /dev/null; then
  if ! python -c 'import sys; assert sys.version_info >= (3,7)' &> /dev/null; then
    # See if 3.9 is installed by altinstall
    if ! python3.9 -c 'import sys; assert sys.version_info >= (3,7)' &> /dev/null; then

      echo You need to have at least python 3.7 installed
      echo Checking for local version in current directory
      if ! $DIR/Python-3.9.0/build/python -c 'import sys; assert sys.version_info >= (3,9)' &> /dev/null; then
        exit
      else
        python="$DIR/Python-3.9.0/build/python"
      fi
    else
      python="python3.9"
    fi
  else
    python="python"
  fi
else
  python="python3"
fi

# Start a virtual environment

if [ ! -d $HOME/.config/thermostat/venv ]; then
  mkdir -p $HOME/.config/thermostat
  $python -m venv $HOME/.config/thermostat/venv
fi
source $HOME/.config/thermostat/venv/bin/activate

cd $DIR/thermostat

./run.py &

# It takes a while for the first run of the thermostat
# We need it to start the loop before we start the ui 
sleep 30

export FLASK_APP=$DIR/thermostat/ui/main.py

flask run --host=192.168.0.254 --with-threads &
