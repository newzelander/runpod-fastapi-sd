import os
import shutil
from symlink_tree import symlink_tree  # updated import

def download_and_flatten_model(src_dir, snapshot_dir, dest_dir):
    if os.path.exists(dest_dir):
        print(f"[INFO] Model already exists at {dest_dir}. Skipping download.")
        return dest_dir

    print(f"[INFO] Symlinking from {snapshot_dir} to {dest_dir}...")
    symlink_tree(snapshot_dir, dest_dir)
    return dest_dir

def handler(job):
    job_input = job.get("input", {})
    action = job_input.get("action")

    if action == "check":
        usage = shutil.disk_usage("/")
        used_gb = (usage.used / (1024 ** 3))
        return {"status": "success", "message": f"Used space: {int(used_gb)}GB"}

    model_path = "/runpod-volume/models/stable-diffusion-3.5-large"
    snapshot_base_path = os.path.join(model_path, "models--stabilityai--stable-diffusion-3.5-large", "snapshots")
    snapshot_id = os.listdir(snapshot_base_path)[0]  # assumes only one snapshot folder
    snapshot_path = os.path.join(snapshot_base_path, snapshot_id)
    final_model_path = os.path.join(model_path, "text_encoder_3")

    result_path = download_and_flatten_model(model_path, snapshot_path, final_model_path)
    return {"status": "success", "message": f"Model linked to {result_path}"}
