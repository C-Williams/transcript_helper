A simple python script that uses [Open AI's Whisper](https://github.com/openai/whisper) model to create transcripts from .wav or .mkv files.

This file generates .wav files from .mkv files, then deletes them during runtime. If you would like to keep these files, comment out lines 38-40 in `main.py`

-------------
NOTE: This project assumes a couple of things

1. The user has generates .mkv files into the `~/Movies/` directory
2. All transcripted files will be located in `~/Movies/Meeting transcriptions/`
