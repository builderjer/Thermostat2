#!/usr/bin/env bash

# This is a setup script for my personal thermostat
# Right now, it checks for version 3.9 of python, and if not avaliable,
# will download and build it localy.
#
# Then, it creates a virtual environment and downlads the requirements.txt file
# with the local pip installation.
#
# Finally, it starts the thermostat its self.
#
# It works for me

# Pymata4 requires at least python 3.7  It will do a local install of 3.9 if
# the minimum version is not found.

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if ! python3 -c 'import sys; assert sys.version_info >= (3,7)' > /dev/null; then
  if [ ! -d "Python-3.9.0" ]; then
    if [ ! -f "Python-3.9.0.tar.xz" ]; then
      wget https://www.python.org/ftp/python/3.9.0/Python-3.9.0.tar.xz
    fi
    tar xfv $DIR/Python-3.9.0.tar.xz
    rm $DIR/Python-3.9.0.tar.xz
  fi

  # ls $PWD/Python-3.9.0/build


  if [ ! -f "$DIR/Python-3.9.0/build/python" ]; then
    cd Python-3.9.0
    mkdir build
    cd build
    ../configure
    make
    cd $DIR
  fi
  python="$DIR/Python-3.9.0/build/python"
else
  python="python3"
fi

if [ ! -d $HOME/.config/thermostat/venv ]; then
  $python -m venv $HOME/.config/thermostat/venv
fi

. $HOME/.config/thermostat/venv/bin/activate

pip install --upgrade pip

pip install -r requirements.txt

cd thermostat
#
./run.py
