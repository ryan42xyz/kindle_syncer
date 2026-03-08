import os
import re
import logging
import smtplib
import tempfile
import shutil
import subprocess
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from dotenv import load_dotenv
from weasyprint import HTML

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KindleEmailSender:
    def __init__(self):
        load_dotenv()
        self.smtp_server = os.getenv('SMTP_SERVER')
        self.smtp_port = int(os.getenv('SMTP_PORT'))
        self.email_user = os.getenv('EMAIL_USER')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.kindle_email = os.getenv('KINDLE_EMAIL')
        
        if not all([self.smtp_server, self.smtp_port, self.email_user, 
                   self.email_password, self.kindle_email]):
            raise ValueError("Missing required environment variables")

    def send_pdf(self, pdf_path):
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = self.kindle_email
            msg['Subject'] = f"Convert to Kindle format: {os.path.basename(pdf_path)}"

            # Add body
            msg.attach(MIMEText("Please convert this PDF to Kindle format.", 'plain'))

            # Add PDF attachment
            with open(pdf_path, 'rb') as f:
                pdf_attachment = MIMEApplication(f.read(), _subtype='pdf')
                pdf_attachment.add_header('Content-Disposition', 'attachment', 
                                        filename=os.path.basename(pdf_path))
                msg.attach(pdf_attachment)

            # Send email
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            logger.info(f"Successfully sent PDF: {pdf_path}")
            return True

        except Exception as e:
            logger.error(f"Error sending PDF {pdf_path}: {str(e)}")
            return False

def process_mermaid_charts(markdown_content, output_dir):
    """Extract and convert Mermaid charts to images"""
    # Regular expression to find Mermaid code blocks
    mermaid_pattern = r'```mermaid\s+(.*?)\s+```'
    chart_counter = 0
    replacement_content = markdown_content
    
    # Find all Mermaid code blocks
    for match in re.finditer(mermaid_pattern, markdown_content, re.DOTALL):
        chart_counter += 1
        mermaid_code = match.group(1)
        chart_file = os.path.join(output_dir, f"chart_{chart_counter}.png")
        
        # Create a temporary file for the Mermaid code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(mermaid_code)
        
        try:
            # Convert Mermaid to PNG using mermaid-cli
            logger.info(f"Converting Mermaid chart {chart_counter} to PNG...")
            cmd = [
                "mmdc",
                "-i", temp_file_path,
                "-o", chart_file,
                "-t", "dark",  # Theme: default, dark, forest, neutral
                "-b", "transparent"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Error converting Mermaid chart: {result.stderr}")
                # Keep the original Mermaid block if conversion fails
                continue
            
            # Replace the Mermaid code block with an image reference
            image_md = f"\n\n![Diagram {chart_counter}](chart_{chart_counter}.png)\n\n"
            replacement_content = replacement_content.replace(match.group(0), image_md)
            
            logger.info(f"Successfully converted Mermaid chart to {chart_file}")
            
        except Exception as e:
            logger.error(f"Error processing Mermaid chart: {str(e)}")
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    return replacement_content, chart_counter

def convert_markdown_to_pdf(markdown_path):
    """Convert a Markdown file to PDF format using pandoc and weasyprint"""
    try:
        # Get the base name without extension
        base_name = os.path.splitext(markdown_path)[0]
        pdf_path = f"{base_name}.pdf"
        
        # Create a temporary directory for conversion
        with tempfile.TemporaryDirectory() as temp_dir:
            # Read the markdown content
            with open(markdown_path, 'r', encoding='utf-8') as md_file:
                markdown_content = md_file.read()
            
            # Process Mermaid charts
            processed_content, chart_count = process_mermaid_charts(markdown_content, temp_dir)
            
            # If charts were processed, write the modified markdown to a temporary file
            if chart_count > 0:
                temp_md_path = os.path.join(temp_dir, os.path.basename(markdown_path))
                with open(temp_md_path, 'w', encoding='utf-8') as temp_md_file:
                    temp_md_file.write(processed_content)
                markdown_path = temp_md_path
            
            # Get style based on environment variable
            style = os.getenv('PDF_STYLE', 'kindle')
            
            # Copy appropriate style.css to temp directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            style_css = os.path.join(script_dir, 'style.css' if style == 'kindle' else 'style_native.css')
            
            if not os.path.exists(style_css):
                logger.warning(f"{style_css} not found, using default styles")
            
            # Convert markdown to HTML using pandoc
            html_path = os.path.join(temp_dir, 'output.html')
            cmd = [
                "pandoc",
                markdown_path,
                "-o", html_path,
                "--standalone",
                "--toc",
                "--toc-depth=3"
            ]
            
            if os.path.exists(style_css):
                cmd.extend(["--css", style_css])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Error converting {markdown_path} to HTML: {result.stderr}")
                return None
            
            # Convert HTML to PDF using weasyprint with custom styles
            HTML(html_path).write_pdf(pdf_path)
            
        logger.info(f"Successfully converted {markdown_path} to {pdf_path}")
        return pdf_path
        
    except Exception as e:
        logger.error(f"Error in conversion: {str(e)}")
        return None

def backup_and_clean_src(markdown_folder):
    """Backup processed files to src.bk and clean src directory"""
    try:
        # Create backup directory if it doesn't exist
        backup_dir = os.path.join(os.path.dirname(markdown_folder), 'src.bk')
        os.makedirs(backup_dir, exist_ok=True)

        # Get timestamp for backup folder
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        timestamped_backup_dir = os.path.join(backup_dir, timestamp)
        os.makedirs(timestamped_backup_dir)

        # Move all files from src to backup
        files = os.listdir(markdown_folder)
        for file in files:
            src_path = os.path.join(markdown_folder, file)
            if os.path.isfile(src_path):
                shutil.move(src_path, os.path.join(timestamped_backup_dir, file))
        
        logger.info(f"Backed up {len(files)} files to {timestamped_backup_dir}")
        
    except Exception as e:
        logger.error(f"Error in backup process: {str(e)}")

def main():
    try:
        # Create src folder if it doesn't exist
        markdown_folder = os.getenv('MARKDOWN_FOLDER', './src')
        os.makedirs(markdown_folder, exist_ok=True)
        
        # Initialize email sender
        email_sender = KindleEmailSender()
        
        # Get all markdown files in the folder
        markdown_files = [f for f in os.listdir(markdown_folder) 
                         if f.lower().endswith(('.md', '.markdown'))]
        
        if not markdown_files:
            logger.info("No markdown files found in the folder.")
            return
            
        logger.info(f"Found {len(markdown_files)} markdown files to process.")
        
        # Process each markdown file
        for markdown_file in markdown_files:
            markdown_path = os.path.join(markdown_folder, markdown_file)
            
            # Convert to PDF
            pdf_path = convert_markdown_to_pdf(markdown_path)
            if pdf_path:
                # Send the PDF file
                if email_sender.send_pdf(pdf_path):
                    # Clean up the PDF file after sending
                    try:
                        os.remove(pdf_path)
                        logger.info(f"Removed temporary PDF file: {pdf_path}")
                    except Exception as e:
                        logger.error(f"Error removing PDF file: {str(e)}")
        
        # Backup processed files and clean src directory
        backup_and_clean_src(markdown_folder)
        logger.info("All files have been processed.")
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")

if __name__ == "__main__":
    main() 