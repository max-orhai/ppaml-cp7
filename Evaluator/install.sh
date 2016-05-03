#!/bin/bash

ABSOLUTE_PATH=$(cd `dirname "${BASH_SOURCE[0]}"` && pwd)

if [ ! -d "venv" ]; then
  virtualenv $ABSOLUTE_PATH/venv
fi

source $ABSOLUTE_PATH/venv/bin/activate

pip install -r $ABSOLUTE_PATH/requirements.txt
