# asset_manager.py
import struct
import pickle
import io
import os

class AssetManager:
    """
    Manages loading resources (e.g., sound files) from a single .dat package file.
    """
    def __init__(self, dat_path):
        # Ensure path is absolute if not already
        if not os.path.isabs(dat_path):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            dat_path = os.path.join(base_dir, dat_path)
            
        try:
            self.file = open(dat_path, 'rb')
            metadata_size_bytes = self.file.read(4)
            metadata_size = struct.unpack('>I', metadata_size_bytes)[0]
            pickled_metadata = self.file.read(metadata_size)
            self.metadata = pickle.loads(pickled_metadata)
            self.data_start_offset = self.file.tell()
            print(f"Asset Manager successfully loaded '{dat_path}'.")
        except FileNotFoundError:
            print(f"!!! CRITICAL ERROR: The '{dat_path}' file was not found!")
            print("Please ensure the sound package exists in the correct directory.")
            exit()
        except Exception as e:
            print(f"!!! CRITICAL ERROR while loading '{dat_path}': {e}")
            exit()

    def get_asset_as_file_like_object(self, name):
        """
        Looks up an asset by name and returns it as an in-memory file-like object.
        """
        if name not in self.metadata:
            print(f"Error: Asset '{name}' not found in the package.")
            return None
        offset, length = self.metadata[name]
        self.file.seek(self.data_start_offset + offset)
        data_bytes = self.file.read(length)
        return io.BytesIO(data_bytes)

    def list_assets(self, extension_filter=None):
        """Lists the names of assets found in the package."""
        if not extension_filter:
            return list(self.metadata.keys())
        return [name for name in self.metadata.keys() if name.endswith(extension_filter)]

    def close(self):
        """Closes the opened .dat file."""
        self.file.close()