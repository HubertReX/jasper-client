#!/bin/bash
if [[ -z "$JASPER_HOME" ]]; then
    if [[ -d "/home/pi" ]]; then
        JASPER_HOME="/home/pi"
        export JASPER_HOME;
    else
        echo "Error: \$JASPER_HOME is not set."
        exit 0;
    fi
fi

cd $JASPER_HOME/jasper/client
rm -rf ../old_client
(python main.py  > /var/log/jasper.log 2>&1 ) &
