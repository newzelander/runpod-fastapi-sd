import subprocess

print("✅ runpod_handler.py started, waiting for event...")

def handler(event):
    try:
        # Run disk usage command on persistent volume
        output = subprocess.check_output(['df', '-h', '/runpod-volume']).decode('utf-8')
        return {
            "status": "success",
            "message": output
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
