import os
import shutil
import logging

logging.basicConfig(level=logging.INFO)

VOLUME_PATH = "/runpod-volume"

def clear_volume():
    logging.info("⬇️ Clearing the persistent volume...")
    try:
        for item in os.listdir(VOLUME_PATH):
            item_path = os.path.join(VOLUME_PATH, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            else:
                shutil.rmtree(item_path)
        logging.info("✅ Volume cleared successfully!")
    except Exception as e:
        logging.error(f"❌ Failed to clear volume: {e}")

def handler(job):
    clear_volume()
    return {"status": "done"}

