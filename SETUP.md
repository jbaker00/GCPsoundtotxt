# GCP Speech-to-Text Setup Guide

## Prerequisites

1. **Google Cloud Account**: Create a project at [Google Cloud Console](https://console.cloud.google.com/)

2. **Enable Speech-to-Text API**:
   - Go to the Google Cloud Console
   - Search for "Speech-to-Text API"
   - Click "Enable"

3. **Create Service Account**:
   - In GCP Console, go to "Service Accounts" (under APIs & Services)
   - Click "Create Service Account"
   - Fill in the service account name
   - Grant the "Editor" role (or at minimum "Cloud Speech Admin")
   - Click "Create and Continue"
   - Click "Create Key" > "JSON"
   - Download the JSON key file

4. **Set Authentication**:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
   ```

## Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Transcribe All Audio Files in Directory
```bash
python speech_to_text.py
```

This will:
- Find all audio files in the script's directory
- Transcribe each file
- Save transcriptions as `.txt` files

### Transcribe Specific File
```bash
python speech_to_text.py "path/to/audio/file.m4a"
```

## Supported Audio Formats
- MP3
- MP4 / M4A
- WAV
- FLAC
- OGG
- WebM

## Notes

- Audio files are sent to Google's servers for processing
- Pricing is based on the duration of audio processed
- First 60 minutes per month are free
- Maximum audio file size: 2GB (for local files)

## Troubleshooting

**Error: "Could not authenticate with Google Cloud"**
- Make sure `GOOGLE_APPLICATION_CREDENTIALS` environment variable is set
- Verify the JSON key file path is correct

**Error: "Speech-to-Text API is not enabled"**
- Enable the Speech-to-Text API in your GCP Console

**Poor Transcription Quality**
- Try adjusting `language_code` in the script
- Ensure audio file has good quality
- Try setting `enable_automatic_punctuation=True` in the config

## API Documentation
For more details: https://cloud.google.com/speech-to-text/docs/
