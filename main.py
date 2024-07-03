import argparse
import os
import subprocess
import whisper

def escape_path(path):
    return path.replace(" ", "\\ ")

def convert_mkv_to_wav(mkv_file):
    wav_file = mkv_file.rsplit('.', 1)[0] + '.wav'
    escaped_mkv_file = escape_path(mkv_file)
    escaped_wav_file = escape_path(wav_file)
    command = f'ffmpeg -i {escaped_mkv_file} {escaped_wav_file}'
    subprocess.run(command, shell=True, check=True)
    return wav_file

def transcribe_file(file, model):
    delete_wav = False
    wav_file = file

    if file.endswith('.mkv'):
        wav_file = convert_mkv_to_wav(file)
        delete_wav = True

    print(f"Transcribing file: {wav_file}")
    result = model.transcribe(wav_file)
    print(f"Transcription result: {result}")

    # Save the result to a text file
    txt_file = os.path.join("..", "Movies", "Meeting transcriptions", os.path.basename(file).rsplit('.', 1)[0] + '.txt')
    os.makedirs(os.path.dirname(txt_file), exist_ok=True)

    with open(txt_file, 'w') as f:
        f.write(result["text"])
    print(f"Transcription saved to {txt_file}")

    # Delete the wav file if it was created
    if delete_wav:
        os.remove(wav_file)
        print(f"Deleted temporary wav file: {wav_file}")

    return file

def get_mkv_files(directory):
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.mkv')]

def read_transcripted_files(file):
    if not os.path.exists(file):
        return set()
    with open(file, 'r') as f:
        return set(f.read().splitlines())

def write_transcripted_files(file, transcripted_files):
    with open(file, 'w') as f:
        for file in transcripted_files:
            f.write(file + '\n')

def main(file):
    model = whisper.load_model("base")
    transcripted_files_file = "../Movies/Meeting transcriptions/transcripted_files.txt"

    # Ensure the directory exists
    os.makedirs(os.path.dirname(transcripted_files_file), exist_ok=True)

    if not file:
        mkv_files = get_mkv_files(os.path.expanduser("../Movies"))
        transcripted_files = read_transcripted_files(transcripted_files_file)

        new_files = [f for f in mkv_files if f not in transcripted_files]

        for mkv_file in new_files:
            try:
                transcribed_file = transcribe_file(mkv_file, model)
                transcripted_files.add(transcribed_file)
            except Exception as e:
                print(f"Error transcribing {mkv_file}: {e}")

        write_transcripted_files(transcripted_files_file, transcripted_files)
    else:
        transcribed_file = transcribe_file(file, model)
        transcripted_files = read_transcripted_files(transcripted_files_file)
        transcripted_files.add(transcribed_file)
        write_transcripted_files(transcripted_files_file, transcripted_files)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe audio files using Whisper. Accepts .mkv or .wav files. However, search only works with .mkv")
    parser.add_argument('file', nargs='?', help='Path to the audio file to be transcribed')

    args = parser.parse_args()

    main(args.file)
