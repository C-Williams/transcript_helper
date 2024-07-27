import argparse
import os
import warnings
import torch
from pydub import AudioSegment
from pydub.utils import mediainfo
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

TEXT_COLORS = {
    'RED': '\033[91m',
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'END': '\033[0m'
}
# Redirect warnings to /dev/null
with open(os.devnull, 'w') as f:
    warnings.simplefilter("ignore")
    warnings.simplefilter(action='ignore', category=FutureWarning)

class TranscriptHelper:

    def __init__(self, file, print_transcription=False, delete_file=False):
        self.file = file
        self.print_transcription = print_transcription
        self.delete_file = delete_file

        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        model_id = "openai/whisper-base"

        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_id, torch_dtype=torch_dtype, use_safetensors=True
        )
        model.to(device)

        processor = AutoProcessor.from_pretrained(model_id)

        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            max_new_tokens=128,
            torch_dtype=torch_dtype,
            device=device
        )

        self.transcripted_files_file = "../Movies/Meeting transcriptions/transcripted_files.txt"
        os.makedirs(os.path.dirname(self.transcripted_files_file), exist_ok=True)

    def process_files(self):
        if not self.file:
            audio_files = self.get_audio_files(os.path.expanduser("../Movies"))
            transcripted_files = self.read_transcripted_files(self.transcripted_files_file)

            new_files = [f for f in audio_files if f not in transcripted_files]
            for audio_file in new_files:
                try:
                    transcribed_file = self.transcribe_file(audio_file)
                    transcripted_files.add(transcribed_file)
                except Exception as e:
                    print(f"{TEXT_COLORS['RED']}Error transcribing {audio_file}: {e}{TEXT_COLORS['END']}")

            self.write_transcripted_files(self.transcripted_files_file, transcripted_files)
        else:
            transcribed_file = self.transcribe_file()
            transcripted_files = self.read_transcripted_files(self.transcripted_files_file)
            transcripted_files.add(transcribed_file)
            self.write_transcripted_files(self.transcripted_files_file, transcripted_files)

    def transcribe_file(self, file):
        delete_wav = False
        wav_file = file

        if not file.endswith('.wav'):
            wav_file = self.convert_to_wav(file, os.path.dirname(file))
            if wav_file:
                delete_wav = True
            else:
                print(f"{TEXT_COLORS['RED']}Failed to convert {file} to WAV format{TEXT_COLORS['END']}")
                exit(1)

        print(f"{TEXT_COLORS['GREEN']}Transcribing file: {wav_file}{TEXT_COLORS['END']}")
        result = self.pipe(wav_file)
        if self.print_transcription:
            print(result["text"])

        txt_file = os.path.join("..", "Movies", "Meeting transcriptions", os.path.basename(file).rsplit('.', 1)[0] + '.txt')
        os.makedirs(os.path.dirname(txt_file), exist_ok=True)

        with open(txt_file, 'w') as f:
            f.write(result["text"])
        print(f"{TEXT_COLORS['GREEN']}Transcription saved to {txt_file}{TEXT_COLORS['END']}")

        if delete_wav:
            os.remove(wav_file)

        if self.delete_file:
            print(f"{TEXT_COLORS['YELLOW']}Here is a sample of the transcription:{TEXT_COLORS['END']}")
            print(result["text"][:100])
            answer = input(f"{TEXT_COLORS['YELLOW']}Would you like to delete the original file? (y/n): {TEXT_COLORS['END']}")
            if answer.lower() == 'y':
                os.remove(file)
                print(f"Deleted original file: {file}")
            else:
                print(f"Original file kept: {file}")
        return file

    def get_audio_files(self, directory):
        supported_formats = ['.mkv', '.mp3', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.aiff', '.ape', '.au', '.mpc', '.ra', '.rm', '.sln', '.vqf', '.w64', '.wv', '.webm', '.opus']
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

    def convert_to_wav(self, file_path, output_directory):
        """
        Converts an audio file to WAV format.

        Parameters:
        - file_path: str, path to the input audio file.
        - output_directory: str, directory where the output WAV file will be saved.
        """
        if not os.path.isfile(file_path):
            print(f"{TEXT_COLORS['RED']}File not found: {file_path}{TEXT_COLORS['END']}")
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe audio files using Whisper. Accepts various audio file formats.")
    parser.add_argument('file', nargs='?', help='Path to the audio file to be transcribed')
    parser.add_argument('print', type=str, help='Print the transcription to the console')
    parser.add_argument('delete', type=str, help='Delete the audio file after transcription')

    args = parser.parse_args()
    if args.print:
        if args.print.lower() != 'true':
            print(f"{TEXT_COLORS['RED']}Invalid argument for 'PRINT'. Expected 'true' or nothing.{TEXT_COLORS['END']}")
            exit(1)
    if args.delete:
        if args.delete.lower() != 'true':
            print(f"{TEXT_COLORS['RED']}Invalid argument for 'DELETE'. Expected 'true' or nothing.{TEXT_COLORS['END']}")
            exit(1)
    helper = TranscriptHelper(args.file, args.print, args.delete)
    helper.process_files()
