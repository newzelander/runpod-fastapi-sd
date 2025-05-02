import os

def symlink_tree(src, dst):
    os.makedirs(dst, exist_ok=True)

    # Walk through the source folder
    for root, dirs, files in os.walk(src):
        for file in files:
            src_file = os.path.join(root, file)
            rel_path = os.path.relpath(src_file, src)
            dst_file = os.path.join(dst, rel_path)

            # Create the directories in the destination path
            os.makedirs(os.path.dirname(dst_file), exist_ok=True)

            # Create symlinks for the files
            if not os.path.exists(dst_file):
                os.symlink(src_file, dst_file)
