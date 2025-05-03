import subprocess 
import runpod
import os

def my_handler(event):
    try:
        # Get actual size of /runpod-volume
        output = subprocess.check_output(
            ['du', '-sh', '/runpod-volume']
        ).decode('utf-8')

        # output is like "12G   /runpod-volume"
        size = output.split()[0]

        # Delete everything in /runpod-volume after checking space
        for root, dirs, files in os.walk('/runpod-volume', topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

        return {
            "status": "success",
            "message": f"Used space: {size}B. All files in /runpod-volume have been deleted."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

runpod.serverless.start({"handler": my_handler})
