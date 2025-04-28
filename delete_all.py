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
        for root_dir, dirs, files in os.walk(volume_path, topdown=False):
            for file in files:
                os.remove(os.path.join(root_dir, file))
            for dir in dirs:
                os.rmdir(os.path.join(root_dir, dir))
        logging.info("✅ Volume cleared successfully!")
    except Exception as e:
        logging.error(f"❌ Error clearing volume: {e}")

# Main process
delete_volume_contents(volume_path)
