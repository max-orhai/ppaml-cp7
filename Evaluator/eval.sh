#!/bin/bash

ABSOLUTE_PATH=$(cd `dirname "${BASH_SOURCE[0]}"` && pwd)

if [ "$#" -ne 3 ]; then
    echo "usage: $(basename $0) <run_out> <eval_in> <eval_output_dir>"
    exit 1
fi

export PYTHONPATH=$ABSOLUTE_PATH

run_out=$1
eval_in=$2
eval_output_dir=$3

[ -d $eval_output_dir ] || mkdir $eval_output_dir

source venv/bin/activate

python $ABSOLUTE_PATH/Evaluation.py $1 $2 $3
