#!/bin/bash

ABSOLUTE_PATH=$(cd `dirname "${BASH_SOURCE[0]}"` && pwd)

if [ "$#" -ne 3 ]; then
    echo "usage: $(basename $0) <run_out> <eval_in> <eval_output_dir>"
    exit 1
fi

export PYTHONPATH=$ABSOLUTE_PATH

if [ -z "$INPUT_DIR" ]; then
  echo "INPUT_DIR not set!"
  exit 1
fi

run_out=$1
eval_in=$2
eval_output_dir=$3
input_dir=$INPUT_DIR

[ -d $eval_output_dir ] || mkdir $eval_output_dir

source $ABSOLUTE_PATH/venv/bin/activate

# Note that arguments are permuted
python $ABSOLUTE_PATH/Evaluation.py $eval_in $input_dir $run_out $eval_output_dir
