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
        # Walk the directory tree and delete files and directories
        for root_dir, dirs, files in os.walk(volume_path, topdown=False):
            for file in files:
                try:
                    os.remove(os.path.join(root_dir, file))
                except Exception as e:
                    logging.warning(f"❌ Failed to delete file {file}: {e}")

            for dir in dirs:
                try:
                    shutil.rmtree(os.path.join(root_dir, dir))  # Delete non-empty directories
                except Exception as e:
                    logging.warning(f"❌ Failed to delete directory {dir}: {e}")

        logging.info("✅ Volume cleared successfully!")
    except Exception as e:
        logging.error(f"❌ Error clearing volume: {e}")

# Main process
delete_volume_contents(volume_path)
