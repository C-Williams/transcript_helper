.SILENT:
.EXPORT_ALL_VARIABLES:

# An optional argument to specify the file to transcribe
# When giving the file path, make sure to use the absolute path and wrap it in quotes
FILE := ""
PRINT := ""
DELETE := ""

# CD into the transcript_helper directory and create a virtual environment
# Then install the required packages and ffmpeg
# NOTE: ffmpeg will install many dependencies, so it may take a minute
venv:
	cd transcript_helper && \
	python3 -m venv .venv && \
	. .venv/bin/activate && \
	pip3 install --upgrade pip > /dev/null && \
	pip3 install -r requirements.txt > /dev/null && \
	make check-dependencies

run: venv
	cd transcript_helper && \
	. .venv/bin/activate && \
	python3 main.py $(FILE) $(PRINT) $(DELETE)

check-dependencies:
	command -v cmake >/dev/null 2>&1 || { \
		echo "cmake is not installed. Installing..."; \
		brew install cmake; \
	}
	cmake_version=$(cmake --version 2>/dev/null | head -n 1 | cut -d ' ' -f 3); \
	if [ -n "$$cmake_version" ] && [ "$$(printf '%s\n' "$$cmake_version" "3.30.1" | sort -V | head -n1)" != "3.30.1" ]; then \
		echo "cmake is outdated. Installing..."; \
		brew upgrade cmake; \
	fi

	command -v ffmpeg >/dev/null 2>&1 || { \
		echo "ffmpeg is not installed. Installing..."; \
		brew install ffmpeg; \
	}
	ffmpeg_version=$(ffmpeg -version 2>/dev/null | head -n 1 | cut -d ' ' -f 3); \
	if [ -n "$$ffmpeg_version" ] && [ "$$(printf '%s\n' "$$ffmpeg_version" "7.0.1" | sort -V | head -n1)" != "7.0.1" ]; then \
		echo "ffmpeg is outdated. Installing..."; \
		brew upgrade ffmpeg; \
	fi

	command -v pkg-config >/dev/null 2>&1 || { \
		echo "pkg-config is not installed. Installing..."; \
		brew install pkg-config; \
	}
	pkgconfig_version=$(pkg-config --version 2>/dev/null); \
	if [ -n "$$pkgconfig_version" ] && [ "$$(printf '%s\n' "$$pkgconfig_version" "0.29.2" | sort -V | head -n1)" != "0.29.2" ]; then \
		echo "pkg-config is outdated. Installing..."; \
		brew upgrade pkg-config; \
	fi

	echo "All dependencies are installed and up-to-date"
