import os
import tkinter as tk
from tkinter import filedialog

def delete_migration_files(folder_path):
    migrations_path = os.path.join(folder_path, 'migrations')

    if os.path.exists(migrations_path):
        for file in os.listdir(migrations_path):
            file_path = os.path.join(migrations_path, file)

            # Check if the file is not '__init__.py'
            if file != '__init__.py':
                try:
                    #os.remove(file_path)
                    print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")

    # Recursively call the function for each subdirectory
    for subdir in os.listdir(folder_path):
        subdir_path = os.path.join(folder_path, subdir)
        if os.path.isdir(subdir_path):
            delete_migration_files(subdir_path)

def select_folder_and_delete_files():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    folder_path = filedialog.askdirectory(title="Select Folder")

    if folder_path:
        delete_migration_files(folder_path)
        print("Files deleted successfully.")
    else:
        print("No folder selected. Operation canceled.")

if __name__ == "__main__":
    select_folder_and_delete_files()
