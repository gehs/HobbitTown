import os
import csv
import sys
import re

# --- THE MAGIC PATH INJECTION ---
# This tricks Python into thinking ffmpeg is fully installed in Windows
FFMPEG_BIN = r"C:\Users\aksca\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin"
os.environ["PATH"] += os.pathsep + FFMPEG_BIN

from pydub import AudioSegment

# Define your folders using raw strings (r"")
INPUT_DIR = r"C:\hTown\sound_stage\raw_mp3s"
OUTPUT_DIR = r"C:\hTown\sound_stage\tsunami_wavs"
CSV_FILE = r"C:\hTown\sound_stage\track_list.csv"

def convert_and_index():
    # Ensure the output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    track_data = []

    # Verify input directory exists before starting
    if not os.path.exists(INPUT_DIR):
        print(f"Error: Input directory not found: {INPUT_DIR}")
        return

    print("--- Step 1: Auto-Numbering Files ---")
    
    # Grab all mp3s and sort them alphabetically so the numbering order is consistent
    mp3_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".mp3")]
    mp3_files.sort()
    
    # We will store the newly renamed filenames here to pass to Step 2
    files_to_process = []
    
    for index, filename in enumerate(mp3_files, start=1):
        # PROTECT: Strip any existing numbers and underscores from the front 
        # (e.g. "001_AMFarm.mp3" becomes "AMFarm.mp3"). 
        # This prevents "001_001_AMFarm" if you run the script twice.
        clean_name = re.sub(r'^\d+_', '', filename)
        
        # Create the new zero-padded name (001_AMFarm.mp3)
        new_filename = f"{index:03d}_{clean_name}"
        
        old_path = os.path.join(INPUT_DIR, filename)
        new_path = os.path.join(INPUT_DIR, new_filename)
        
        # Actually rename the file on the hard drive if it needs it
        if old_path != new_path:
            os.rename(old_path, new_path)
            print(f"Renamed: {filename} -> {new_filename}")
            
        files_to_process.append(new_filename)


    print("\n--- Step 2: Batch Conversion & CSV Indexing ---")
    
    # Loop through the newly organized files
    for filename in files_to_process:
        base_name = os.path.splitext(filename)[0]
        
        # Split the number from the description
        parts = base_name.split("_", 1)
        track_num = int(parts[0])
        
        # Clean up the description for the CSV (replace remaining underscores with spaces)
        description = parts[1].replace("_", " ") if len(parts) > 1 else "Unknown Track"
            
        input_path = os.path.join(INPUT_DIR, filename)
        output_filename = f"{base_name}.wav"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        print(f"Converting Track {track_num:03d}: {description}...")
        
        try:
            # Load MP3 and convert strictly to Tsunami Mono requirements:
            # 44.1kHz (44100), 16-bit (sample_width=2), Mono (channels=1)
            audio = AudioSegment.from_mp3(input_path)
            audio = audio.set_frame_rate(44100).set_sample_width(2).set_channels(1)
            
            # Export as WAV
            audio.export(output_path, format="wav")
            
            # Add to our index list
            track_data.append([track_num, description, output_filename])
            
        except Exception as e:
            print(f"Failed to convert {filename}: {e}")

    # Write the master index to a CSV file
    try:
        with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Track Number", "Description", "Filename"])
            writer.writerows(track_data)
        print(f"\nSuccess! Converted {len(track_data)} files and generated {CSV_FILE}.")
    except PermissionError:
        print(f"\nERROR: Could not write to {CSV_FILE}. Is the file open in Excel?")

if __name__ == "__main__":
    convert_and_index()