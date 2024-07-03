.SILENT:
.EXPORT_ALL_VARIABLES:

# An optional argument to specify the file to transcribe
# When giving the file path, make sure to use the absolute path and wrap it in quotes
FILE := ""

# Check if the virtual environment exists, if not create it
check-for-venv:
	@if [ ! -d "transcript_helper/.venv" ]; then \
		make -f transcript_helper/Makefile venv; \
	fi

# CD into the transcript_helper directory and create a virtual environment
# Then install the required packages and ffmpeg
# NOTE: ffmpeg will install many dependencies, so it may take a minute
venv:
	cd transcript_helper && \
	python3 -m venv .venv && \
	. .venv/bin/activate && \
	pip3 install -r requirements.txt && \
	brew install ffmpeg

run: check-for-venv
	cd transcript_helper && \
	. .venv/bin/activate && \
	python3 main.py $(FILE)
