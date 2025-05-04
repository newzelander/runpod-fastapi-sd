import os
import shutil
from huggingface_hub import snapshot_download

VOLUME_PATH = "/runpod-volume"

def get_disk_usage(path):
    total, used, free = shutil.disk_usage(path)
    return f"Total: {total // (2**30)} GB, Used: {used // (2**30)} GB, Free: {free // (2**30)} GB}"

def clean_directory(path):
    print(f"Cleaning directory: {path}")
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}: {e}")

def main():
    print("=== Disk Usage Before Cleanup ===")
    print(get_disk_usage(VOLUME_PATH))

    clean_directory(VOLUME_PATH)

    print("=== Disk Usage After Cleanup ===")
    print(get_disk_usage(VOLUME_PATH))

    print("=== Downloading model ===")
    snapshot_download(
        repo_id="stabilityai/stable-diffusion-3.5-large",
        local_dir=VOLUME_PATH,
        local_dir_use_symlinks=False,
        resume_download=True
    )

    print("=== Disk Usage After Download ===")
    print(get_disk_usage(VOLUME_PATH))

if __name__ == "__main__":
    main()
