"""
Convert audio files to text using Google Cloud Speech-to-Text API.

Prerequisites:
1. Install the Google Cloud Speech library:
   pip install google-cloud-speech

2. Set up authentication:
   - Create a service account in GCP Console
   - Download the JSON key file
   - Set environment variable: export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"

3. Optional: Install ffmpeg for M4A/AAC audio conversion:
   brew install ffmpeg  (on macOS)
   OR apt-get install ffmpeg  (on Linux)
"""

import os
import sys
import subprocess
import tempfile
from google.cloud import speech_v1


def transcribe_audio(audio_file_path):
    """
    Transcribe audio file to text using Google Cloud Speech-to-Text API.
    
    Args:
        audio_file_path: Path to the audio file (supports various formats)
    
    Returns:
        str: Transcribed text
    """
    
    # Check if file exists
    if not os.path.exists(audio_file_path):
        print(f"Error: File '{audio_file_path}' not found")
        return None
    
    # Get file extension
    _, ext = os.path.splitext(audio_file_path)
    ext = ext.lower()
    
    # Convert M4A to WAV if necessary
    audio_to_process = audio_file_path
    if ext in ['.m4a', '.aac', '.mp4']:
        try:
            # Use ffmpeg to convert to WAV (LINEAR16)
            print(f"  Converting {ext} to WAV format...")
            wav_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False).name
            subprocess.run(
                ['ffmpeg', '-i', audio_file_path, '-acodec', 'pcm_s16le', '-ar', '16000', wav_file, '-y'],
                capture_output=True,
                check=True
            )
            audio_to_process = wav_file
            print(f"  Conversion complete.")
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            print(f"  Error: Could not convert audio. Make sure ffmpeg is installed.")
            print(f"  Install ffmpeg with: brew install ffmpeg (macOS) or apt-get install ffmpeg (Linux)")
            return None
    
    # Initialize the speech client
    client = speech_v1.SpeechClient()
    
    # Read the audio file
    with open(audio_to_process, "rb") as audio_file:
        content = audio_file.read()
    
    # Configure the audio file
    audio = speech_v1.RecognitionAudio(content=content)
    
    # Configure the recognition request
    config = speech_v1.RecognitionConfig(
        encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,  # 16kHz is standard for WAV conversion
        language_code="en-US",  # Change language as needed
    )
    
    print(f"Transcribing audio file: {audio_file_path}")
    print("This may take a moment...")
    
    # Perform the transcription
    try:
        response = client.recognize(config=config, audio=audio)
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None
    
    # Clean up temporary file if created
    if audio_to_process != audio_file_path:
        try:
            os.remove(audio_to_process)
        except:
            pass
    
    # Extract the transcribed text
    transcription = ""
    for result in response.results:
        for alternative in result.alternatives:
            transcription += alternative.transcript
    
    return transcription


def transcribe_directory(directory_path="."):
    """
    Transcribe all audio files in a directory.
    
    Supported formats: MP3, MP4, WAV, FLAC, and others supported by GCP.
    
    Args:
        directory_path: Path to the directory containing audio files
    """
    
    # Supported audio extensions
    supported_extensions = [".wav", ".mp3", ".mp4", ".m4a", ".flac", ".ogg", ".webm"]
    
    # Find all audio files
    audio_files = []
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            _, ext = os.path.splitext(filename)
            if ext.lower() in supported_extensions:
                audio_files.append(file_path)
    
    if not audio_files:
        print(f"No audio files found in '{directory_path}'")
        return
    
    print(f"Found {len(audio_files)} audio file(s) to transcribe.\n")
    
    # Transcribe each file
    for audio_file in audio_files:
        print(f"\n{'='*60}")
        print(f"Processing: {os.path.basename(audio_file)}")
        print(f"{'='*60}")
        
        transcription = transcribe_audio(audio_file)
        
        if transcription:
            print("\nTranscription:")
            print(transcription)
            
            # Save the transcription to a text file
            output_file = os.path.splitext(audio_file)[0] + ".txt"
            with open(output_file, "w") as f:
                f.write(transcription)
            print(f"\nSaved to: {output_file}")
        else:
            print("Transcription failed.")


if __name__ == "__main__":
    # If a specific file is provided as an argument, transcribe just that file
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
        transcription = transcribe_audio(audio_file)
        if transcription:
            print("\nTranscription:")
            print(transcription)
            
            # Save the transcription
            output_file = os.path.splitext(audio_file)[0] + ".txt"
            with open(output_file, "w") as f:
                f.write(transcription)
            print(f"\nSaved to: {output_file}")
    else:
        # Transcribe all audio files in the current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        transcribe_directory(current_dir)
