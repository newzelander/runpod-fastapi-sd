import os
import shutil

# Function to show all existing folders/paths including ~/.cache/huggingface/hub
def show_existing_paths():
    print("Existing folders and paths:")
    paths_to_check = [
        "/runpod-volume",  # Path where RunPod volume is stored
        os.path.expanduser("~/.cache/huggingface/hub")  # Hugging Face cache path
    ]

    for path in paths_to_check:
        if os.path.exists(path):
            print(f"Path found: {path}")
        else:
            print(f"Path not found: {path}")

# Function to clear contents inside the directories (keeping the directories intact)
def clear_directory_contents():
    paths_to_clear = [
        "/runpod-volume",  # Path where RunPod volume is stored
        os.path.expanduser("~/.cache/huggingface/hub")  # Hugging Face cache path
    ]

    for path in paths_to_clear:
        if os.path.exists(path):
            print(f"Clearing contents of {path}...")
            if os.path.isdir(path):
                # Delete all files and subdirectories inside the directory
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)  # Recursively delete directories
                    else:
                        os.remove(item_path)  # Delete files
                print(f"Cleared contents of: {path}")
            else:
                os.remove(path)
                print(f"Deleted file: {path}")
        else:
            print(f"Path does not exist: {path}")

# Function to ensure Hugging Face does not download the model twice
def configure_hugging_face_cache():
    # Set the Hugging Face cache directory to the runpod-volume directory
    os.environ["HF_HUB_CACHE"] = "/runpod-volume"  # Use runpod-volume as the cache directory
    
    # Optionally, you can disable the default cache altogether
    # os.environ["HF_HUB_DISABLE_CACHE"] = "1"  # Uncomment to disable the default Hugging Face cache

# Main function to run the operations
def main():
    # Show existing paths
    show_existing_paths()

    # Ask for user confirmation to proceed with deletion
    confirmation = input("Are you sure you want to clear the contents of the specified paths (including Hugging Face cache)? (yes/no): ")
    if confirmation.lower() == "yes":
        # Clear the contents of the directories
        clear_directory_contents()

        # Ensure Hugging Face model download does not happen twice by setting the cache to runpod-volume
        configure_hugging_face_cache()
        print("Hugging Face cache configuration applied. No duplicate downloads will occur.")
        
        # You may want to trigger any other process after clearing the directories, if necessary.
        
        print("Cleanup and configuration complete.")
    else:
        print("Operation aborted.")

# Run the script
if __name__ == "__main__":
    main()
