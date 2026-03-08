#!/bin/bash

# Get the absolute path of the script's directory
SCRIPT_DIR=/Users/rshao/work/code_repos/kindlesyncer

# Check if a file is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <pdf_file>"
    exit 1
fi

# Get the absolute path of the PDF file
PDF_PATH=$(realpath "$1")

# Check if the file exists
if [ ! -f "$PDF_PATH" ]; then
    echo "Error: File not found: $PDF_PATH"
    exit 1
fi

# Check if the file is a PDF
if [[ ! "$PDF_PATH" =~ \.pdf$ ]]; then
    echo "Error: File must be a PDF"
    exit 1
fi

# Use bash to activate virtual environment and send PDF
/bin/bash -c "
source '$SCRIPT_DIR/venv/bin/activate'
echo 'Installing required packages...'
pip install -q python-dotenv

# Send PDF using Python
python3 -c '
import os
import sys
sys.path.append(\"$SCRIPT_DIR\")
from kindlesyncer import KindleEmailSender

sender = KindleEmailSender()
success = sender.send_pdf(\"$PDF_PATH\")

if success:
    print(f\"Successfully sent PDF: $PDF_PATH\")
    sys.exit(0)
else:
    print(f\"Failed to send PDF: $PDF_PATH\")
    sys.exit(1)
'
"

# Check the exit status
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    exit 0
else
    exit 1
fi 