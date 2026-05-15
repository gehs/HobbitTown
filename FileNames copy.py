import os
import csv

# Define your paths
TARGET_DIR = r"C:\hTown\sound_stage\tsunami_wavs"
CSV_FILE = r"C:\hTown\sound_stage\track_list - track_list.csv"

def rename_files_from_csv():
    if not os.path.exists(TARGET_DIR):
        print(f"Error: Directory not found: {TARGET_DIR}")
        return

    if not os.path.exists(CSV_FILE):
        print(f"Error: CSV file not found: {CSV_FILE}")
        return

    print("--- Starting File Renaming ---")

    with open(CSV_FILE, mode='r', encoding='utf-8') as f:
        # Use DictReader if your CSV has headers, or standard reader for indexing
        reader = csv.reader(f)
        
        # Skip the header row
        header = next(reader)
        
        count = 0
        for row in reader:
            # Column 4 is index 3 (Current Name)
            # Column 5 is index 4 (New Name)
            try:
                current_name = row[3].strip()
                new_name = row[4].strip()
            except IndexError:
                continue # Skip rows that don't have enough columns

            # Construct full paths
            old_path = os.path.join(TARGET_DIR, current_name)
            new_path = os.path.join(TARGET_DIR, new_name)

            # Only rename if the file exists and the name is actually different
            if os.path.exists(old_path):
                if old_path != new_path:
                    try:
                        os.rename(old_path, new_path)
                        print(f"Renamed: {current_name} -> {new_name}")
                        count += 1
                    except Exception as e:
                        print(f"Error renaming {current_name}: {e}")
                else:
                    print(f"Skipped: {current_name} is already correctly named.")
            else:
                print(f"File not found: {current_name}")

    print(f"\nFinished! Total files renamed: {count}")

if __name__ == "__main__":
    rename_files_from_csv()