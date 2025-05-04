import runpod
import check_disk

def handler(event):
    action = event.get("input", {}).get("action")

    if action == "check":
        result = check_disk.main()
        return {
            "status": "completed",
            "disk_info": result
        }
    else:
        return {
            "status": "error",
            "message": f"Unknown action: {action}"
        }

runpod.serverless.start({"handler": handler})
