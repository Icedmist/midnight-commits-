import os

def rename_files(folder_path, prefix):
    # Check if folder exists
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' not found.")
        return

    # Get all files
    files = os.listdir(folder_path)
    
    # Sort files so they are renamed in order (optional but good)
    files.sort()

    print(f"Renaming {len(files)} files in '{folder_path}'...")

    for index, filename in enumerate(files, start=1):
        # Skip hidden files (like .DS_Store or .git)
        if filename.startswith('.'):
            continue

        # Get the file extension (e.g., .jpg)
        extension = os.path.splitext(filename)[1]
        
        # Create new name: "Vacation_1.jpg"
        new_name = f"{prefix}_{index}{extension}"
        
        # Full paths
        old_file = os.path.join(folder_path, filename)
        new_file = os.path.join(folder_path, new_name)

        # Rename
        os.rename(old_file, new_file)
        print(f"Renamed: {filename} -> {new_name}")

    print("✅ Batch renaming complete!")

def main():
    folder = input("Enter folder path to rename: ")
    prefix = input("Enter new prefix (e.g., 'Holiday'): ")
    
    # Confirmation safety net
    confirm = input(f"This will rename ALL files in {folder}. Proceed? (y/n): ")
    if confirm.lower() == 'y':
        rename_files(folder, prefix)
    else:
        print("Operation cancelled.")

if __name__ == "__main__":
    main()