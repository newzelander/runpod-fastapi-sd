import subprocess
import runpod

def my_handler(event):
    try:
        # Run disk usage command on persistent volume
        output = subprocess.check_output(['du', '-h', '/runpod-volume']).decode('utf-8')
        return {
            "status": "success",
            "message": output
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# Register handler with runpod
runpod.serverless.start({"handler": my_handler})
