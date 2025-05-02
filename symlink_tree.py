import os

def symlink_tree(src, dst):
    # Create the destination folder if it doesn't exist
    os.makedirs(dst, exist_ok=True)
    
    # Find the nested directory inside the models path
    for root, dirs, files in os.walk(src):
        # Skip non-snapshot directories
        if "snapshots" not in root:
            continue
        
        # Inside snapshot, we expect the actual model files (UNet, vae, etc.)
        for file in files:
            src_file = os.path.join(root, file)
            rel_path = os.path.relpath(src_file, src)
            dst_file = os.path.join(dst, rel_path)
            
            # Create the directories in the destination path
            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
            
            # Create symlinks for the files
            if not os.path.exists(dst_file):
                os.symlink(src_file, dst_file)
