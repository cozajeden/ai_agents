#!/usr/bin/env python3
"""
Test module for the Whisper-based STT endpoint.
"""

import pytest
import requests
import json
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
STT_BASE = f"{BASE_URL}/stt"

class TestSTTEndpoints:
    """Test class for STT endpoints."""
    
    def test_stt_health(self):
        """Test STT health check endpoint."""
        response = requests.get(f"{STT_BASE}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["service"] == "stt"
        assert "status" in data
        assert "whisper_available" in data
    
    def test_transcribe_audio_file(self, sample_audio_file):
        """Test audio transcription endpoint with a sample file."""
        if not sample_audio_file or not os.path.exists(sample_audio_file):
            pytest.skip("Sample audio file not available")
        
        with open(sample_audio_file, 'rb') as audio_file:
            files = {'audio_file': audio_file}
            
            response = requests.post(f"{STT_BASE}/transcribe", files=files)
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert "transcribed_text" in data
            assert "language" in data
            assert "file_name" in data
            assert "model_used" in data
    
    def test_transcribe_invalid_file(self):
        """Test transcription with invalid file type."""
        # Create a fake text file
        fake_file = ("fake_audio.txt", "This is not an audio file", "text/plain")
        
        files = {'audio_file': fake_file}
        response = requests.post(f"{STT_BASE}/transcribe", files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert "File must be an audio file" in data["detail"]

@pytest.fixture
def sample_audio_file():
    """Fixture to create a sample audio file for testing."""
    try:
        from pydub import AudioSegment
        from pydub.generators import Sine
        
        # Create a simple sine wave audio
        audio = Sine(440).to_audio_segment(duration=2000)  # 2 seconds at 440Hz
        
        # Export as WAV
        sample_path = "test_sample_audio.wav"
        audio.export(sample_path, format="wav")
        
        yield sample_path
        
        # Cleanup
        if os.path.exists(sample_path):
            os.remove(sample_path)
            
    except ImportError:
        pytest.skip("pydub not available for audio generation")
        yield None

# Standalone test functions for manual testing
def test_health_manual():
    """Manual test for STT health check."""
    print("Testing STT health check...")
    try:
        response = requests.get(f"{STT_BASE}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 50)

def test_transcription_manual(audio_file_path: str):
    """Manual test for audio transcription."""
    print(f"Testing audio transcription with file: {audio_file_path}")
    
    if not os.path.exists(audio_file_path):
        print(f"Audio file not found: {audio_file_path}")
        return
    
    try:
        with open(audio_file_path, 'rb') as audio_file:
            files = {'audio_file': audio_file}
            
            response = requests.post(f"{STT_BASE}/transcribe", files=files)
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    print("-" * 50)

def create_sample_audio():
    """Create a sample audio file for manual testing."""
    print("Creating sample audio file for testing...")
    
    try:
        from pydub import AudioSegment
        from pydub.generators import Sine
        
        # Create a simple sine wave audio
        audio = Sine(440).to_audio_segment(duration=3000)  # 3 seconds at 440Hz
        
        # Export as WAV
        sample_path = "sample_audio.wav"
        audio.export(sample_path, format="wav")
        print(f"Sample audio created: {sample_path}")
        return sample_path
        
    except ImportError:
        print("pydub not available, skipping sample audio creation")
        return None

if __name__ == "__main__":
    """Manual test runner."""
    print("Manual STT API Test - Whisper-based")
    print("=" * 40)
    
    # Test health endpoint
    test_health_manual()
    
    # Test audio transcription (if sample file exists or can be created)
    sample_audio = create_sample_audio()
    if sample_audio:
        test_transcription_manual(sample_audio)
        
        # Clean up sample file
        os.remove(sample_audio)
        print(f"Cleaned up sample file: {sample_audio}")
    
    print("\nManual test completed!")
    print("\nTo test with your own audio files:")
    print("1. Start the FastAPI server: uvicorn app.main:app --reload")
    print("2. Use the endpoint:")
    print(f"   - POST {STT_BASE}/transcribe")
    print(f"   - GET {STT_BASE}/health")
    print("\nExample:")
    print(f'curl -X POST "{STT_BASE}/transcribe" \\')
    print('  -F "audio_file=@your_audio.wav"')
