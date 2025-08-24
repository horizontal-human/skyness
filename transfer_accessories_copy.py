import shutil
import os

# List of JSON files to copy
files_to_copy = [
    "accessories.json",
    "accessories_clean.json",
    "accessories_fixed.json",
    "accessories_soulbound.json",
    "accessory_plan.json"
]

# Destination folder
destination = os.path.join("accessory-planner", "public")

# Copy each file
for file_name in files_to_copy:
    src_path = os.path.join(os.getcwd(), file_name)
    dest_path = os.path.join(destination, file_name)

    if os.path.exists(src_path):
        shutil.copy(src_path, dest_path)
        print(f"Copied {file_name} to {destination}")
    else:
        print(f"File {file_name} not found in project folder.")
