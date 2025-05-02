import os

def symlink_tree(src, dst):
    os.makedirs(dst, exist_ok=True)

    for root, dirs, files in os.walk(src):
        for file in files:
            src_file = os.path.join(root, file)
            rel_path = os.path.relpath(src_file, src)
            dst_file = os.path.join(dst, rel_path)

            os.makedirs(os.path.dirname(dst_file), exist_ok=True)

            try:
                if not os.path.exists(dst_file):
                    os.symlink(src_file, dst_file)
            except OSError as e:
                print(f"Failed to create symlink for {src_file} → {dst_file}: {e}")
