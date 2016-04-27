#!/bin/bash

source venv/bin/activate

if (( $# != 4)); then
    printf "Usage: %s config_file input_dir output_dir log_dir\n" "$0" >&2
    exit 1
fi
if [ ! -d "$3" ]; then
    mkdir -p $3
fi
if [ ! -d "$4" ]; then
    mkdir -p $4
fi

CMD="python FluTrackMain.py $1 $2 $3 $4 2>&1 | tee $4/run.log"
echo $CMD
$CMD

