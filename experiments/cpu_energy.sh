#!/bin/bash

RUNTIME=180
sudo perf stat -I 1000 -e power/energy-ram/ -a -o logs/ram.log sleep $RUNTIME &
sudo perf stat -I 1000 -e power/energy-pkg/ -a -o logs/pkg.log sleep $RUNTIME 

