#!/bin/bash

# Get the absolute path of the script's directory
SCRIPT_DIR=/Users/rshao/work/code_repos/kindlesyncer

# Function to show usage
show_usage() {
    echo "Usage: $0 [-k|--kindle] [-n|--native] <markdown_file>"
    echo "Options:"
    echo "  -k, --kindle    Use Kindle-optimized style (default)"
    echo "  -n, --native    Use native PDF style"
    exit 1
}

# Parse command line arguments
STYLE="kindle"  # Default style
MARKDOWN_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -k|--kindle)
            STYLE="kindle"
            shift
            ;;
        -n|--native)
            STYLE="native"
            shift
            ;;
        -h|--help)
            show_usage
            ;;
        *)
            if [[ -z "$MARKDOWN_FILE" ]]; then
                MARKDOWN_FILE="$1"
            else
                echo "Error: Multiple input files specified"
                show_usage
            fi
            shift
            ;;
    esac
done

# Check if a file is provided
if [[ -z "$MARKDOWN_FILE" ]]; then
    show_usage
fi

# Get the absolute path of the markdown file
MD_PATH=$(realpath "$MARKDOWN_FILE")

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

# Get the output PDF path (same directory as markdown file)
PDF_PATH="${MD_PATH%.*}.pdf"

# Create src directory if it doesn't exist
SRC_DIR="$SCRIPT_DIR/src"
mkdir -p "$SRC_DIR"

# Copy the markdown file to src directory
FILENAME=$(basename "$MD_PATH")
cp "$MD_PATH" "$SRC_DIR/$FILENAME"

# Use bash to activate virtual environment and run conversion
/bin/bash -c "
source '$SCRIPT_DIR/venv/bin/activate'
echo 'Installing required packages...'
pip install -q weasyprint python-dotenv
cd '$SCRIPT_DIR'

# Directly call the python script to process one file
python3 -c '
import os
import sys
sys.path.append(\"$SCRIPT_DIR\")
from kindlesyncer import convert_markdown_to_pdf

# Set style based on command line argument
os.environ[\"PDF_STYLE\"] = \"$STYLE\"

# Convert to PDF
markdown_path = \"$SRC_DIR/$FILENAME\"
pdf_path = convert_markdown_to_pdf(markdown_path)

if pdf_path:
    # Copy the PDF to the original location if different
    if \"$PDF_PATH\" != pdf_path:
        import shutil
        shutil.copy(pdf_path, \"$PDF_PATH\")
        print(f\"Successfully converted to PDF: {pdf_path}\")
        print(f\"Copied to: $PDF_PATH\")
    else:
        print(f\"Successfully converted to PDF: {pdf_path}\")
    
    # Remove the original PDF if it was created in src directory
    try:
        os.remove(pdf_path)
    except:
        pass
    
    sys.exit(0)
else:
    print(\"Conversion failed\")
    sys.exit(1)
'
"

# Check the exit status
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    # If successful, clean up the markdown file in src
    rm -f "$SRC_DIR/$FILENAME"
    exit 0
else
    echo "Failed to convert to PDF"
    # Clean up on failure too
    rm -f "$SRC_DIR/$FILENAME"
    exit 1
fi 