import os
import shutil
import logging

logging.basicConfig(level=logging.INFO)

# Path to the persistent volume
volume_path = "/runpod-volume"

def delete_volume_contents(volume_path):
    """Deletes everything from the volume"""
    logging.info("⬇️ Clearing the persistent volume...")
    try:
        # Walk through the directory and delete all files and directories
        for item in os.listdir(volume_path):
            item_path = os.path.join(volume_path, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)  # Remove directory and contents
            else:
                os.remove(item_path)  # Remove file
        logging.info("✅ Volume cleared successfully!")
    except Exception as e:
        logging.error(f"❌ Error clearing volume: {str(e)}")

# Main process
if __name__ == "__main__":
    delete_volume_contents(volume_path)
