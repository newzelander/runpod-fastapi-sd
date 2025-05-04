import runpod
import check_disk

def handler(event):
    result = check_disk.main()
    return {
        "status": "completed",
        "disk_info": result
    }

runpod.serverless.start({"handler": handler})
