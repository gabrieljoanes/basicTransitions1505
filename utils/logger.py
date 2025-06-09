import os
import logging
from datetime import datetime
from typing import Optional
from .gdrive import upload_to_gdrive

# Create logs directory if it doesn't exist
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Configure logging with more detailed format
log_file = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',  # Only show the message
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Log the start of the application
logger.info("Application started")
logger.info(f"Log file location: {os.path.abspath(log_file)}")

def save_output_to_file(title: str, chapo: str, article_text: str, transitions: list[str]) -> Optional[str]:
    """
    Saves the generated article and transitions to a file and uploads it to Google Drive.
    Returns the Google Drive URL if successful, None otherwise.
    """
    try:
        # Create outputs directory if it doesn't exist
        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"article_{timestamp}.txt"
        filepath = os.path.join(output_dir, filename)

        # Write content to file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"Titre: {title}\n\n")
            f.write(f"Chapeau: {chapo}\n\n")
            f.write("Article:\n")
            f.write(article_text.strip() + "\n\n")
            f.write("Transitions générées:\n")
            for i, t in enumerate(transitions, 1):
                f.write(f"{i}. {t}\n")

        logger.info(f"Successfully saved article to {filepath}")

        # Upload to Google Drive
        gdrive_file_id = upload_to_gdrive(filepath, filename)
        if gdrive_file_id:
            logger.info(f"Successfully uploaded to Google Drive with file ID: {gdrive_file_id}")
            return filepath
        else:
            logger.warning("File saved locally but upload to Google Drive failed")
            return None

    except Exception as e:
        logger.error(f"Error saving output: {str(e)}")
        return None