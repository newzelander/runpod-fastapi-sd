import subprocess

def handler(event):
    result = subprocess.run(["python", "preload_model.py"], capture_output=True, text=True)
    return {
        "status": "completed",
        "stdout": result.stdout,
        "stderr": result.stderr
    }
