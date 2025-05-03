import subprocess
import runpod

def my_handler(event):
    try:
        # Get actual size of /runpod-volume
        output = subprocess.check_output(
            ['du', '-sh', '/runpod-volume']
        ).decode('utf-8')

        # output is like "12G   /runpod-volume"
        size = output.split()[0]

        return {
            "status": "success",
            "message": f"Used space: {size}B"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

runpod.serverless.start({"handler": my_handler})