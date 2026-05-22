import os
import struct
import pickle
import io

def pack_sounds(output_path, sound_sources):
    """
    Packs sounds into a .dat file.
    sound_sources: list of (name, bytes)
    """
    metadata = {}
    current_offset = 0
    data_buffer = io.BytesIO()

    for name, data in sound_sources:
        length = len(data)
        metadata[name] = (current_offset, length)
        data_buffer.write(data)
        current_offset += length

    pickled_metadata = pickle.dumps(metadata)
    metadata_size = len(pickled_metadata)

    with open(output_path, 'wb') as f:
        f.write(struct.pack('>I', metadata_size))
        f.write(pickled_metadata)
        f.write(data_buffer.getvalue())
    
    print(f"Successfully packed {len(sound_sources)} assets into {output_path}")

def main():
    # Set working directory to the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Paths
    external_sounds_dir = r"C:\Users\natan\AppData\Roaming\Jarvis\audios"
    existing_dat = "sounds.dat"
    output_dat = "sounds_new.dat"

    sound_sources = []

    # 1. Load existing sounds from sounds.dat
    if os.path.exists(existing_dat):
        from asset_manager import AssetManager
        am = AssetManager(existing_dat)
        for name in am.list_assets():
            print(f"Extracting existing: {name}")
            fileobj = am.get_asset_as_file_like_object(name)
            if fileobj:
                sound_sources.append((name, fileobj.read()))
        am.close()

    # 2. Load new sounds from external directory
    if os.path.exists(external_sounds_dir):
        for filename in os.listdir(external_sounds_dir):
            if filename.endswith(('.mp3', '.wav')):
                # Add prefix for the 'jarvis' soundpack
                prefixed_name = f"jarvis/{filename}"
                print(f"Adding new as soundpack: {prefixed_name}")
                filepath = os.path.join(external_sounds_dir, filename)
                with open(filepath, 'rb') as f:
                    sound_sources.append((prefixed_name, f.read()))
    else:
        print(f"Warning: External sounds directory not found: {external_sounds_dir}")

    # 3. Pack everything
    pack_sounds(output_dat, sound_sources)
    
    # 4. Replace old dat (backup first)
    if os.path.exists(existing_dat):
        if os.path.exists(existing_dat + ".bak"):
            os.remove(existing_dat + ".bak")
        os.rename(existing_dat, existing_dat + ".bak")
    os.rename(output_dat, existing_dat)
    print("Done! sounds.dat has been updated.")

if __name__ == "__main__":
    main()
