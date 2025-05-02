import os
import shutil
import logging
import sys
import time

logging.basicConfig(level=logging.INFO)

VOLUME_PATH = "/runpod-volume"

def delete_volume_contents(path):
    logging.info("⬇️ Clearing the persistent volume...")
    try:
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
        logging.info("✅ Volume cleared successfully!")
    except Exception as e:
        logging.error(f"❌ Error clearing volume: {e}")
        sys.exit(1)

if __name__ == "__main__":
    delete_volume_contents(VOLUME_PATH)

    logging.info("✅ Script finished. Sleeping 2 seconds then exiting.")
    time.sleep(2)  # Give logs time to flush
    sys.exit(0)
