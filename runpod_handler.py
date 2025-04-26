import subprocess
import runpod

def my_handler(event):
    try:
        # Run df and filter only /runpod-volume info
        output = subprocess.check_output(
            ['df', '-h', '--output=size,used,avail,pcent,target', '/runpod-volume']
        ).decode('utf-8')

        # Remove extra first line if needed
        lines = output.strip().split('\n')
        header = lines[0]
        data = lines[1]

        return {
            "status": "success",
            "message": f"{header}\n{data}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

runpod.serverless.start({"handler": my_handler})
