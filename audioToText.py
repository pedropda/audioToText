from openai import OpenAI
from pydub import AudioSegment
import os
import math

client = OpenAI()  # Ensure the API key is set in your environment variables

def split_audio(file_path, chunk_length_ms=600000):  # Split audio into chunks of 10 minutes each
    audio = AudioSegment.from_file(file_path)
    chunks = []
    for i in range(0, len(audio), chunk_length_ms):
        chunk = audio[i:i+chunk_length_ms]
        chunk_file_path = f"/tmp/chunk_{i}.mp3"  # Temporary file for each chunk
        chunk.export(chunk_file_path, format="mp3")
        chunks.append(chunk_file_path)
    return chunks

def transcribe_audio(file_path):
    with open(file_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )
    return transcription  # Directly return the transcription text

def transcribe_large_file(file_path):
    # Check if the file needs to be split by estimating its size
    file_size = os.path.getsize(file_path)
    max_size_bytes = 25 * 1024 * 1024  # 25 MB in bytes
    if file_size > max_size_bytes:
        print(f"File {file_path} exceeds 25MB, splitting into smaller chunks...")
        chunks = split_audio(file_path)
        transcriptions = [transcribe_audio(chunk) for chunk in chunks]
        # Clean up temporary chunk files
        for chunk in chunks:
            os.remove(chunk)
        return " ".join(transcriptions)
    else:
        return transcribe_audio(file_path)

# Paths to your uploaded audio files
file_paths = [
    "GMT20240227-013720_Recording.m4a",
    "GMT20240229-013002_Recording.m4a"
]

# Transcribe each file and save the transcription
for path in file_paths:
    try:
        print(f"Transcribing {os.path.basename(path)}...")
        text = transcribe_large_file(path)
        
        # Define a path for the output text file
        transcription_file_path = path + ".txt"
        
        # Save the transcription to a file
        with open(transcription_file_path, "w") as text_file:
            text_file.write(text)
        
        print(f"Transcription saved to {transcription_file_path}")
    except Exception as e:
        print(f"Failed to transcribe {os.path.basename(path)}: {e}")

