import os

def symlink_tree(src_dir, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)

    for root, dirs, files in os.walk(src_dir):
        rel_path = os.path.relpath(root, src_dir)
        dest_root = os.path.join(dest_dir, rel_path) if rel_path != "." else dest_dir

        os.makedirs(dest_root, exist_ok=True)

        for file in files:
            src_file = os.path.join(root, file)
            dest_file = os.path.join(dest_root, file)

            if not os.path.exists(dest_file):
                os.symlink(src_file, dest_file)
