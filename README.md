# GCP Speech-to-Text Converter

Convert audio files to text using Google Cloud Platform's Speech-to-Text API.

## Features

- Converts audio files to text using GCP Speech-to-Text API
- Supports multiple audio formats: M4A, MP3, WAV, FLAC, and more
- Automatically converts M4A/AAC files to WAV format for processing
- Saves transcriptions as text files
- Processes single files or entire directories

## Supported Audio Formats

- MP3
- MP4 / M4A (AAC)
- WAV
- FLAC
- OGG
- WebM
- AMR
- SPEEX

## Prerequisites

1. **Python 3.7+**
2. **ffmpeg** (for audio conversion)
   - macOS: `brew install ffmpeg`
   - Linux: `apt-get install ffmpeg`
   - Windows: Download from https://ffmpeg.org/download.html

3. **Google Cloud Account** with Speech-to-Text API enabled
4. **Service Account credentials** (JSON key file)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/GCPsoundtotxt.git
   cd GCPsoundtotxt
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Setup

1. Create a GCP service account and download the JSON key
2. Set the authentication environment variable:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
   ```

For detailed setup instructions, see [SETUP.md](SETUP.md)

## Usage

### Transcribe all audio files in directory:
```bash
GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json" python speech_to_text.py
```

### Transcribe a specific file:
```bash
GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json" python speech_to_text.py "path/to/audio/file.m4a"
```

### Example output:
```
Found 1 audio file(s) to transcribe.

============================================================
Processing: New Recording.m4a
============================================================
  Converting .m4a to WAV format...
  Conversion complete.
Transcribing audio file: /path/to/New Recording.m4a
This may take a moment...

Transcription:
test 1 2 3 4 5 this is a test of 1 2 3 4 5 please transcribe

Saved to: /path/to/New Recording.txt
```

## How It Works

1. Detects audio files in the directory (or processes specified file)
2. For M4A/AAC files, converts to WAV format using ffmpeg
3. Sends audio to Google Cloud Speech-to-Text API
4. Receives and saves transcription to a `.txt` file with the same name

## Pricing

- First 60 minutes of audio per month: **Free**
- Additional audio: $0.006 per 15 seconds

See [Google Cloud Speech pricing](https://cloud.google.com/speech-to-text/pricing) for details.

## Troubleshooting

**Error: "Default credentials were not found"**
- Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable with path to your JSON key file

**Error: "Speech-to-Text API is not enabled"**
- Enable the API in your GCP Console

**Error: "Could not convert audio (ffmpeg not found)"**
- Install ffmpeg: `brew install ffmpeg` (macOS) or `apt-get install ffmpeg` (Linux)

**Poor transcription quality**
- Ensure audio file has good quality and clear speech
- Try setting a specific language code in the script if not English

## Customization

Edit `speech_to_text.py` to modify:
- **Language**: Change `language_code="en-US"` to your desired language
- **Audio settings**: Adjust sample rate, encoding, etc.
- **File types**: Add or remove supported file extensions

## License

MIT

## Support

For issues with the script, check [SETUP.md](SETUP.md) for troubleshooting.
For GCP API issues, see [Google Cloud Speech documentation](https://cloud.google.com/speech-to-text/docs)
