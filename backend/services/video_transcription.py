"""
Corrected service for video transcription and integration with the RAG system.
This module properly implements Whisper for transcription.
"""
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any

# Import the correct whisper library - this is the one you need to install
import whisper

from fastapi import UploadFile, HTTPException

# Import your existing vector DB service
from services.vector_db import VectorDBService

class VideoTranscriptionService:
    """Service for handling video transcription and indexing."""
    
    def __init__(self, vector_db_service: VectorDBService):
        """Initialize the video transcription service."""
        self.vector_db_service = vector_db_service
        self.whisper_model = None
        self.transcription_dir = "./knowledge/transcriptions"
        
        # Create transcription directory if it doesn't exist
        os.makedirs(self.transcription_dir, exist_ok=True)
    
    def _load_whisper_model(self, model_size: str = "base"):
        """
        Load the Whisper model for transcription.
        
        Args:
            model_size: Size of the Whisper model to use.
                Options: "tiny", "base", "small", "medium", "large"
        """
        if self.whisper_model is None:
            try:
                # This is the correct way to load the model
                self.whisper_model = whisper.load_model(model_size)
                print(f"Loaded Whisper model: {model_size}")
            except Exception as e:
                print(f"Error loading Whisper model: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to load transcription model: {str(e)}"
                )
    
    def _extract_audio(self, video_path: str) -> str:
        """
        Extract audio from a video file.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Path to the extracted audio file
        """
        # Create a temporary file for the audio
        audio_path = tempfile.mktemp(suffix=".wav")
        
        try:
            # Use FFmpeg to extract audio
            cmd = [
                "ffmpeg", "-i", video_path, 
                "-vn", "-acodec", "pcm_s16le", 
                "-ar", "16000", "-ac", "1",
                audio_path
            ]
            
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                print(f"FFmpeg error: {stderr.decode()}")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to extract audio from video"
                )
                
            return audio_path
            
        except Exception as e:
            print(f"Error extracting audio: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Error in audio extraction: {str(e)}"
            )
    
    def transcribe_video(self, video_file: UploadFile, model_size: str = "base") -> Dict[str, Any]:
        """
        Transcribe a video file and index the transcription.
        
        Args:
            video_file: Uploaded video file
            model_size: Size of the Whisper model to use
            
        Returns:
            Dictionary with transcription details
        """
        # Load the Whisper model if not already loaded
        self._load_whisper_model(model_size)
        
        # Create a temporary file for the uploaded video
        video_filename = Path(video_file.filename).stem
        video_path = tempfile.mktemp(suffix=Path(video_file.filename).suffix)
        
        try:
            # Save the uploaded video to a temporary file
            with open(video_path, "wb") as temp_video:
                content = video_file.file.read()
                temp_video.write(content)
                video_file.file.seek(0)  # Reset file pointer
            
            # Extract audio from the video
            audio_path = self._extract_audio(video_path)
            
            # Transcribe the audio using Whisper
            # This is how you actually use the Whisper model
            result = self.whisper_model.transcribe(audio_path)
            
            # Save the transcription to a file
            transcription_path = os.path.join(
                self.transcription_dir, f"{video_filename}_transcription.txt"
            )
            
            with open(transcription_path, "w", encoding="utf-8") as f:
                f.write(f"# Transcription of {video_file.filename}\n\n")
                f.write(result["text"])
            
            # Clean up temporary files
            os.remove(video_path)
            os.remove(audio_path)
            
            # Reindex the vector database to include the new transcription
            self.vector_db_service.clear_and_reindex()
            
            return {
                "filename": video_file.filename,
                "transcription_path": transcription_path,
                "duration": result.get("duration", 0),
                "language": result.get("language", "unknown"),
                "success": True
            }
            
        except Exception as e:
            import traceback
            print(f"Error in video transcription: {e}")
            print(traceback.format_exc())
            raise HTTPException(
                status_code=500,
                detail=f"Error in video transcription: {str(e)}"
            )