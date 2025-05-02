import os

def symlink_tree(src, dst):
    os.makedirs(dst, exist_ok=True)

    # Walk through the source folder (look for the 'snapshots/<snapshot_id>' directory)
    for root, dirs, files in os.walk(src):
        # Look for the 'snapshots/<snapshot_id>' directory in the source path
        if 'snapshots' in dirs:
            snapshot_dir = os.path.join(root, 'snapshots')
            for snapshot_root, snapshot_dirs, snapshot_files in os.walk(snapshot_dir):
                for file in snapshot_files:
                    src_file = os.path.join(snapshot_root, file)
                    rel_path = os.path.relpath(src_file, snapshot_dir)
                    dst_file = os.path.join(dst, rel_path)

                    # Create the directories in the destination path
                    os.makedirs(os.path.dirname(dst_file), exist_ok=True)

                    # Create symlinks for the files
                    if not os.path.exists(dst_file):
                        os.symlink(src_file, dst_file)
