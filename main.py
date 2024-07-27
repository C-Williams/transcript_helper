import argparse
import os
import whisper

from convert import convert_to_wav

class TranscriptHelper:

    def __init__(self, file):
        self.file = file
        self.model = whisper.load_model("base")

        self.transcripted_files_file = "../Movies/Meeting transcriptions/transcripted_files.txt"
        os.makedirs(os.path.dirname(self.transcripted_files_file), exist_ok=True)

    def process_files(self):
        if not self.file:
            audio_files = self.get_audio_files(os.path.expanduser("../Movies"))
            transcripted_files = self.read_transcripted_files(self.transcripted_files_file)

            new_files = [f for f in audio_files if f not in transcripted_files]

            for audio_file in new_files:
                try:
                    transcribed_file = self.transcribe_file(audio_file, self.model)
                    transcripted_files.add(transcribed_file)
                except Exception as e:
                    print(f"Error transcribing {audio_file}: {e}")

            self.write_transcripted_files(self.transcripted_files_file, transcripted_files)
        else:
            transcribed_file = self.transcribe_file()
            transcripted_files = self.read_transcripted_files(self.transcripted_files_file)
            transcripted_files.add(transcribed_file)
            self.write_transcripted_files(self.transcripted_files_file, transcripted_files)


    def escape_path(self, path):
        return path.replace(" ", "\\ ")

    def transcribe_file(self):
        delete_wav = False
        wav_file = self.file

        if not self.file.endswith('.wav'):
            wav_file = convert_to_wav(self.file, os.path.dirname(self.file))
            if wav_file:
                delete_wav = True
            else:
                print(f"Failed to convert {self.file} to WAV format")
                return None

        print(f"Transcribing file: {wav_file}")
        result = self.model.transcribe(wav_file)

        txt_file = os.path.join("..", "Movies", "Meeting transcriptions", os.path.basename(self.file).rsplit('.', 1)[0] + '.txt')
        os.makedirs(os.path.dirname(txt_file), exist_ok=True)

        with open(txt_file, 'w') as f:
            f.write(result["text"])
        print(f"Transcription saved to {txt_file}")

        if delete_wav:
            os.remove(wav_file)
            print(f"Deleted temporary wav file: {wav_file}")

        return self.file

    def get_audio_files(self, directory):
        supported_formats = ['.mkv', '.mp3', '.flac', '.aac', '.ogg', '.wma']
        return [os.path.join(directory, f) for f in os.listdir(directory) if os.path.splitext(f)[1].lower() in supported_formats]

    def read_transcripted_files(self, file):
        if not os.path.exists(file):
            return set()
        with open(file, 'r') as f:
            return set(f.read().splitlines())

    def write_transcripted_files(self, file, transcripted_files):
        with open(file, 'w') as f:
            for file in transcripted_files:
                f.write(file + '\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe audio files using Whisper. Accepts various audio file formats.")
    parser.add_argument('file', nargs='?', help='Path to the audio file to be transcribed')

    args = parser.parse_args()

    helper = TranscriptHelper(args.file)
    helper.process_files()
