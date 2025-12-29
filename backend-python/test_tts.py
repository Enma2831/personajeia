#!/usr/bin/env python3
"""
Test script for TTS functionality
"""
import asyncio
from pathlib import Path
import sys
import os

# Add the backend-python directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import generate_voice_mock

async def test_tts():
    """Test the TTS functionality"""
    test_text = "Esta es una prueba de voz en español para narrar historias de horror. La voz debe sonar calmada e íntima."

    print("Testing TTS with text:", test_text[:50] + "...")

    try:
        audio_path = await generate_voice_mock(test_text, "test_narration")
        print(f"Audio generated successfully: {audio_path}")
        print(f"File exists: {audio_path.exists()}")
        print(f"File size: {audio_path.stat().st_size} bytes")
    except Exception as e:
        print(f"Error generating audio: {e}")

if __name__ == "__main__":
    asyncio.run(test_tts())