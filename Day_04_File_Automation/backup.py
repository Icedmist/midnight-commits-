import shutil
import os
import datetime

def create_backup(source_folder):
    if not os.path.exists(source_folder):
        print("Source folder does not exist.")
        return

    # Create a unique name: "my_project_2025-01-23"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder_name = os.path.basename(source_folder)
    backup_folder_name = f"{folder_name}_backup_{timestamp}"
    
    try:
        # Copy the entire directory tree
        shutil.copytree(source_folder, backup_folder_name)
        print(f"✅ Backup successful! Created: {backup_folder_name}")
    except Exception as e:
        print(f"❌ Backup failed: {e}")

def main():
    folder = input("Enter folder to back up: ")
    create_backup(folder)

if __name__ == "__main__":
    main()