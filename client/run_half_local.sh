#!/bin/bash
if [[ -z "$JASPER_HOME" ]]; then
    if [[ -d "/home/osmc" ]]; then
        JASPER_HOME="/home/osmc"
        export JASPER_HOME;
    else
        echo "Error: \$JASPER_HOME is not set."
        exit 0;
    fi
fi

cd $JASPER_HOME/jasper/client
rm -rf ../old_client
tmux new -d -s jasper "./debug.sh -hl -c $1 $2 $3"
#tmux new -s jasper "./debug.sh -hl -c -n $1 $2 $3 > debug.log 2>&1"
#tmux new -s jasper "./debug.sh -hl -c -n $1 $2 $3 "
#python main.py -hl -c $1 $2 $3
