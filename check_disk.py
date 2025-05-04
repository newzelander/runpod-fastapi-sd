import os

VOLUME_PATH = "/runpod-volume"

def get_dir_size(path):
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            try:
                fp = os.path.join(dirpath, f)
                total += os.path.getsize(fp)
            except OSError:
                pass
    return total

def format_size(bytes):
    gb = bytes / (1024 ** 3)
    return f"{gb:.2f} GB"

def list_files(path):
    files = []
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            full_path = os.path.join(dirpath, f)
            rel_path = os.path.relpath(full_path, VOLUME_PATH)
            files.append(rel_path)
    return files

def find_model_dir(path):
    for root, dirs, files in os.walk(path):
        if "model_index.json" in files:
            return root
    return None

def main():
    used_bytes = get_dir_size(VOLUME_PATH)
    files = list_files(VOLUME_PATH)
    model_dir = find_model_dir(VOLUME_PATH)

    return {
        "volume_path": VOLUME_PATH,
        "used_space": format_size(used_bytes),
        "file_count": len(files),
        "files": files,
        "model_path": model_dir or "Not found"
    }

if __name__ == "__main__":
    print(main())
