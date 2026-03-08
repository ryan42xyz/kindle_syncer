# Kindle PDF Syncer

A Python application that automatically sends PDF files to your Kindle device via email using a 163.com email account.

## Features

- Monitors a specified folder for new PDF files
- Automatically sends PDFs to your Kindle email address
- Uses secure SMTP connection
- Configurable through environment variables
- Detailed logging

## Setup

1. Clone this repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure your environment variables in `.env`:
   ```
   SMTP_SERVER=smtp.163.com
   SMTP_PORT=465
   EMAIL_USER=your_163_email
   EMAIL_PASSWORD=your_163_app_password
   KINDLE_EMAIL=your_kindle_email
   PDF_FOLDER=./pdf
   ```

   Note: For 163.com email, you'll need to:
   1. Enable SMTP service in your 163.com account settings
   2. Create an app-specific password for this application

## Usage

1. Start the syncer:
   ```bash
   python kindlesyncer.py
   ```

2. Place PDF files in the `pdf` folder (or your configured PDF_FOLDER)
3. The application will automatically detect new PDF files and send them to your Kindle
4. Press Ctrl+C to stop the application

## Logging

The application logs all activities to the console, including:
- New PDF file detection
- Successful email sending
- Error messages

## Troubleshooting

1. If emails are not being sent:
   - Verify your 163.com email credentials
   - Check if SMTP service is enabled in your 163.com account
   - Ensure you're using the correct app-specific password

2. If PDFs are not being detected:
   - Verify the PDF_FOLDER path in your .env file
   - Check file permissions
   - Ensure the files have .pdf extension

## Security Notes

- Never commit your .env file with real credentials
- Use app-specific passwords instead of your main email password
- Keep your Kindle email address private 