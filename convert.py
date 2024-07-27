import os
from pydub import AudioSegment
from pydub.utils import mediainfo

def convert_to_wav(file_path, output_directory):
    """
    Converts an audio file to WAV format.

    Parameters:
    - file_path: str, path to the input audio file.
    - output_directory: str, directory where the output WAV file will be saved.
    """
    if not os.path.isfile(file_path):
        print(f"File not found: {file_path}")
        return None

    file_info = mediainfo(file_path)
    if 'format_name' not in file_info:
        print(f"Not a valid audio file: {file_path}")
        return None

    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_path = os.path.join(output_directory, f"{base_name}.wav")

    try:
        audio = AudioSegment.from_file(file_path)
        audio.export(output_path, format="wav")
        return output_path
    except Exception as e:
        print(f"Failed to convert {file_path}: {e}")
        return None
