#!/bin/sh

avconv -i $1 -v quiet -y -ar $3 $2

