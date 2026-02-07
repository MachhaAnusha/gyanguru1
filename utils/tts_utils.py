"""
Text-to-Speech Module for GyanGuru
Converts generated scripts to audio using gTTS
"""

import os
from datetime import datetime
from gtts import gTTS
from typing import Dict, Any, Optional


class TextToSpeech:
    """Handles text-to-speech conversion using Google TTS"""
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize TTS handler
        
        Args:
            output_dir: Directory to save audio files
        """
        self.output_dir = output_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'static', 'generated', 'audio'
        )
        os.makedirs(self.output_dir, exist_ok=True)
    
    def text_to_speech(
        self, 
        text: str, 
        filename: Optional[str] = None,
        language: str = 'en',
        slow: bool = False
    ) -> Dict[str, Any]:
        """
        Convert text to speech and save as MP3
        
        Args:
            text: The text content to convert
            filename: Optional custom filename (without extension)
            language: Language code (default: 'en' for English)
            slow: If True, speak slower
        
        Returns:
            Dictionary with file path and metadata
        """
        try:
            # Generate filename with timestamp if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"audio_lesson_{timestamp}"
            
            # Ensure .mp3 extension
            if not filename.endswith('.mp3'):
                filename = f"{filename}.mp3"
            
            filepath = os.path.join(self.output_dir, filename)
            
            # Create TTS object and save
            tts = gTTS(text=text, lang=language, slow=slow)
            tts.save(filepath)
            
            # Calculate approximate duration (rough estimate: 150 words/min)
            word_count = len(text.split())
            estimated_duration = round(word_count / 150, 1)
            
            return {
                "success": True,
                "filepath": filepath,
                "filename": filename,
                "relative_path": f"/static/generated/audio/{filename}",
                "word_count": word_count,
                "estimated_duration_minutes": estimated_duration,
                "language": language
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "filepath": None
            }
    
    def get_available_audio_files(self) -> list:
        """Get list of available audio files"""
        files = []
        if os.path.exists(self.output_dir):
            for f in os.listdir(self.output_dir):
                if f.endswith('.mp3'):
                    files.append({
                        "filename": f,
                        "path": os.path.join(self.output_dir, f),
                        "relative_path": f"/static/generated/audio/{f}"
                    })
        return files
    
    def delete_audio_file(self, filename: str) -> bool:
        """Delete an audio file"""
        filepath = os.path.join(self.output_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
