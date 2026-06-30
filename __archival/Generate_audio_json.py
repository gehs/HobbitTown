import os
import re
import json
import wave

def generate_tsunami_json(audio_dir, output_json_path="sounds.json"):
    """
    Scans a directory of WAV files, extracts Tsunami track numbers,
    calculates exact audio durations, and generates a structured JSON file.
    """
    sound_config = {
        "settings": {
            "master_volume_db": 0,
            "description": "Generated configuration for Tsunami Super WAV Trigger"
        },
        "tracks": {}
    }
    
    # Regex to capture leading digits, stripping out common separators like _, -, or spaces
    # Works for: "1_track.wav", "001-Track.wav", "0001.wav"
    filename_pattern = re.compile(r'^(\d+)[-_\s]*(.*)\.wav$', re.IGNORECASE)

    if not os.path.exists(audio_dir):
        print(f"Error: Directory '{audio_dir}' not found.")
        return

    # Sort files to process them sequentially by track number
    files = sorted(os.listdir(audio_dir))
    track_count = 0

    for filename in files:
        if not filename.lower().endswith('.wav'):
            continue
            
        match = filename_pattern.match(filename)
        if match:
            track_num_str, track_name = match.groups()
            track_number = int(track_num_str)
            
            # Generate a clean, Python/JSON-friendly lookup key
            if track_name:
                # Replace remaining spaces/hyphens with a single underscore, lowercase it
                key_name = re.sub(r'[-_\s]+', '_', track_name).strip('_').lower()
            else:
                # Fallback if the file is just numeric like "0001.wav"
                key_name = f"track_{track_number}"
            
            file_path = os.path.join(audio_dir, filename)
            
            # Read the WAV header to get exact length without loading the whole file into RAM
            try:
                with wave.open(file_path, 'rb') as wav_file:
                    frames = wav_file.getnframes()
                    rate = wav_file.getframerate()
                    length_seconds = round(frames / float(rate), 2)
            except Exception as e:
                print(f"Warning: Could not read audio length for {filename}. Error: {e}")
                length_seconds = 0.0

            # Smart Guessing: Let's assign default categories and loops based on naming clues
            category = "effect"
            loop_default = False
            
            # Simple keyword matching to save you manual editing time later
            if any(kw in key_name for kw in ["ambient", "loop", "bg", "cricket", "tavern"]):
                category = "ambient"
                loop_default = True
            elif any(kw in key_name for kw in ["quote", "dialogue", "voice", "speak"]):
                category = "dialogue"

            # Construct the entry
            sound_config["tracks"][key_name] = {
                "track_number": track_number,
                "file": filename,
                "length_seconds": length_seconds,
                "loop": loop_default,
                "volume_db": 0,  # Default to unity gain
                "category": category
            }
            track_count += 1

    # Write out the clean, indented JSON file
    with open(output_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(sound_config, json_file, indent=2)
        
    print(f"\nSuccess! Generated '{output_json_path}' with {track_count} tracks.")

# --- HOW TO RUN IT ---
if __name__ == "__main__":
    # Update this path to where your WAV files are currently stored on your computer
    AUDIO_DIRECTORY = "C:\\hTown\\HobbitTown\\tsunami_wavs" 
    
    generate_tsunami_json(AUDIO_DIRECTORY)