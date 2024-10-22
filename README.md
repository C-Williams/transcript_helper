A simple python script that uses [Open AI's Whisper](https://github.com/openai/whisper) model to create transcripts from .wav or .mkv files.

To clone this repo use:
```bash
git clone https://github.com/C-Williams/transcript_helper.git
```

To run this file use:
```bash
make -f transcript_helper/Makefile run
```

If this is your first run, a `.venv` directory will be created, which will then be used to create a virtual python environment. Then packages located in `requirements.txt` will be installed in this environment.

This file generates .wav files from .mkv files, then deletes them during runtime. If you would like to keep these files, comment out lines 38-40 in `main.py`

There are some optional flags you can add if you would like:

`FILE="<FILE_NAME>"`
to transcribe a particular file.

`PRINT="true"`
to print your transcript to the terminal.

`DELETE="true"`
to be prompted to delete transcripts that you consider valid.

-------------
NOTE: This project assumes a couple of things

1. The user generates .mkv files into the `~/Movies/` directory
2. All transcripted files will be located in `~/Movies/Meeting transcriptions/`
