#!/bin/bash

# Get the PID of the process
PID=$(pgrep -f "python3 parser.py")

if [ -n "$PID" ]; then
    # If the PID is not empty, kill the process
    kill "$PID"
    echo "Process with PID $PID has been stopped."
else
    echo "No running process found."
fi