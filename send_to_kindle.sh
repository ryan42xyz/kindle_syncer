#!/bin/bash

# Get the absolute path of the script's directory
SCRIPT_DIR=/Users/rshao/work/code_repos/kindlesyncer

# Check if a file is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <markdown_file>"
    exit 1
fi

# Get the absolute path of the markdown file
MD_PATH=$(realpath "$1")

# Check if the file exists
if [ ! -f "$MD_PATH" ]; then
    echo "Error: File not found: $MD_PATH"
    exit 1
fi

# Check if the file is a markdown file
if [[ ! "$MD_PATH" =~ \.(md|markdown)$ ]]; then
    echo "Error: File must be a markdown file (.md or .markdown)"
    exit 1
fi

# Get the src directory path
SRC_DIR="$SCRIPT_DIR/src"

# Create src directory if it doesn't exist
mkdir -p "$SRC_DIR"

# Copy the markdown file to src directory
cp "$MD_PATH" "$SRC_DIR/"

# Setup virtual environment using bash
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$SCRIPT_DIR/venv"
fi

# Use bash to activate virtual environment and run commands
/bin/bash -c "
source '$SCRIPT_DIR/venv/bin/activate'
echo 'Installing required packages...'
pip install -q weasyprint python-dotenv watchdog secure-smtplib
cd '$SCRIPT_DIR' && python3 kindlesyncer.py
"

# Check the exit status
if [ $? -eq 0 ]; then
    echo "Successfully processed $MD_PATH and sent to Kindle"
else
    echo "Failed to process $MD_PATH"
    exit 1
fi 