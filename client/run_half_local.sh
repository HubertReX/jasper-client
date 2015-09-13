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

#dummy console for debug
tmux new -d -s jasper-debug "nano debug"
#tmux attach -t jasper-debug

#run mic as stand alone process for continues listen (command are send  to main server by: tmux send-keys -t jasper "<command>\n\r")
tmux new -d -s jasper-mic "python half_local_mic.py"
#tmux attach -t jasper-mic

#run jasper server with half-local mic -> passive from keyboard (or remote) active from mic
tmux new -d -s jasper "./debug.sh -hl -c $1 $2 $3"


#tmux new -s jasper "./debug.sh -hl -c -n $1 $2 $3 > debug.log 2>&1"
#tmux new -s jasper "./debug.sh -hl -c -n $1 $2 $3 "
#python main.py -hl -c $1 $2 $3


#tmux list-sessions

