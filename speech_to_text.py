"""
Convert audio files to text using Google Cloud Speech-to-Text API.

Prerequisites:
1. Install the Google Cloud Speech library:
   pip install google-cloud-speech

2. Set up authentication:
   - Create a service account in GCP Console
   - Download the JSON key file
   - Set environment variable: export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"

3. Required: Install ffmpeg for audio format conversion (all non-WAV formats):
   brew install ffmpeg  (on macOS)
   OR apt-get install ffmpeg  (on Linux)
"""

import os
import sys
import subprocess
import tempfile
import time
from google.cloud import speech_v1
from google.cloud import storage


def get_audio_duration(audio_file_path):
    """
    Get the duration of an audio file in seconds using ffprobe.
    
    Args:
        audio_file_path: Path to the audio file
    
    Returns:
        float: Duration in seconds, or None if unable to determine
    """
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
             '-of', 'default=noprint_wrappers=1:nokey=1:noprint_wrappers=1', 
             audio_file_path],
            capture_output=True,
            text=True,
            check=True
        )
        return float(result.stdout.strip())
    except (FileNotFoundError, subprocess.CalledProcessError, ValueError):
        return None


def upload_to_gcs(file_path, bucket_name="jamesbaker-audio-transcription-2026"):
    """
    Upload a file to GCS and return the GCS URI.
    
    Args:
        file_path: Path to the local file
        bucket_name: GCS bucket name
    
    Returns:
        str: GCS URI (gs://bucket/filename)
    """
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob_name = os.path.basename(file_path)
        blob = bucket.blob(blob_name)
        
        print(f"  Uploading {blob_name} to GCS...")
        blob.upload_from_filename(file_path)
        gcs_uri = f"gs://{bucket_name}/{blob_name}"
        print(f"  Upload complete: {gcs_uri}")
        return gcs_uri
    except Exception as e:
        print(f"  Error uploading to GCS: {e}")
        return None





def transcribe_audio_long(audio_file_path, client):
    """
    Transcribe long audio file (>1 min) using LongRunningRecognize.
    
    Args:
        audio_file_path: Path to the audio file
        client: SpeechClient instance
    
    Returns:
        str: Transcribed text
    """
    print("  Using LongRunningRecognize API for long audio...")
    
    with open(audio_file_path, "rb") as audio_file:
        content = audio_file.read()
    
    audio = speech_v1.RecognitionAudio(content=content)
    
    config = speech_v1.RecognitionConfig(
        encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )
    
    # Start long-running recognition
    operation = client.long_running_recognize(config=config, audio=audio)
    
    print("  Waiting for long-running recognition to complete...")
    response = operation.result(timeout=3600)  # Wait up to 1 hour
    
    transcription = ""
    for result in response.results:
        for alternative in result.alternatives:
            transcription += alternative.transcript
    
    return transcription



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
    
    # Convert any non-WAV format to WAV using ffmpeg
    audio_to_process = audio_file_path
    if ext != '.wav':
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
    
    # Get audio duration to determine which API to use
    duration = get_audio_duration(audio_to_process)
    use_long_running = duration and duration > 60  # Use LongRunningRecognize for audio > 1 minute
    
    print(f"Transcribing audio file: {audio_file_path}")
    if use_long_running:
        print(f"Audio duration: {duration:.1f} seconds - Using long-running API with GCS")
        # Upload to GCS for long audio
        gcs_uri = upload_to_gcs(audio_to_process)
        if not gcs_uri:
            return None
    
    print("This may take a moment...")
    
    # Configure the recognition request
    config = speech_v1.RecognitionConfig(
        encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )
    
    # Perform the transcription
    try:
        if use_long_running:
            # Use GCS URI for long audio
            audio = speech_v1.RecognitionAudio(uri=gcs_uri)
            operation = client.long_running_recognize(config=config, audio=audio)
            print("  Waiting for transcription to complete (this may take several minutes)...")
            response = operation.result(timeout=3600)  # Wait up to 1 hour
        else:
            # Read the audio file for shorter files
            with open(audio_to_process, "rb") as audio_file:
                content = audio_file.read()
            audio = speech_v1.RecognitionAudio(content=content)
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
    supported_extensions = [".wav", ".mp3", ".mp4", ".m4a", ".flac", ".ogg", ".webm", ".caf"]
    
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
