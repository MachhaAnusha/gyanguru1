"""
Image Generation Module for GyanGuru
Handles educational diagram generation using Gemini AI
"""

import os
import base64
from datetime import datetime
from typing import Dict, Any, Optional
import google.generativeai as genai
from PIL import Image
import io


class ImageGenerator:
    """Handles image generation for educational diagrams"""
    
    def __init__(self, api_key: Optional[str] = None, output_dir: Optional[str] = None):
        """
        Initialize image generator
        
        Args:
            api_key: Gemini API key
            output_dir: Directory to save generated images
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.output_dir = output_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'static', 'generated', 'images'
        )
        os.makedirs(self.output_dir, exist_ok=True)
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
    
    def generate_diagram(
        self,
        prompt: str,
        topic: str,
        diagram_type: str = "architecture",
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate an educational diagram using Gemini
        
        Args:
            prompt: Detailed prompt for image generation
            topic: The ML topic being visualized
            diagram_type: Type of diagram
            filename: Optional custom filename
        
        Returns:
            Dictionary with image path and metadata
        """
        try:
            # Generate filename with timestamp if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_topic = "".join(c if c.isalnum() else "_" for c in topic[:30])
                filename = f"{safe_topic}_{diagram_type}_{timestamp}.png"
            
            filepath = os.path.join(self.output_dir, filename)
            
            # Try Gemini image generation
            try:
                image_model = genai.GenerativeModel("gemini-2.0-flash-exp-image-generation")
                
                enhanced_prompt = f"""Create a professional educational diagram:

{prompt}

Style requirements:
- Clean, modern technical illustration style
- Professional color scheme (blues, teals, grays)
- Clear labels and annotations
- White or light background
- High contrast for readability
- No text errors or gibberish
"""
                
                response = image_model.generate_content(
                    enhanced_prompt,
                    generation_config={"response_mime_type": "image/png"}
                )
                
                # Check if we got image data
                if response.candidates and response.candidates[0].content.parts:
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            image_data = base64.b64decode(part.inline_data.data)
                            with open(filepath, 'wb') as f:
                                f.write(image_data)
                            
                            return {
                                "success": True,
                                "filepath": filepath,
                                "filename": filename,
                                "relative_path": f"/static/generated/images/{filename}",
                                "topic": topic,
                                "diagram_type": diagram_type,
                                "method": "gemini"
                            }
            
            except Exception as gemini_error:
                print(f"Gemini image generation failed: {gemini_error}")
            
            # Fallback: Create a placeholder image
            return self._create_placeholder_image(topic, diagram_type, filename, filepath)
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "filepath": None
            }
    
    def _create_placeholder_image(
        self,
        topic: str,
        diagram_type: str,
        filename: str,
        filepath: str
    ) -> Dict[str, Any]:
        """Create a placeholder diagram image"""
        try:
            # Create a simple placeholder image using PIL
            width, height = 800, 600
            
            # Create image with gradient background
            img = Image.new('RGB', (width, height), color=(30, 41, 59))
            
            # We'll create a simple visual placeholder
            # In production, you could use matplotlib to create actual diagrams
            from PIL import ImageDraw, ImageFont
            
            draw = ImageDraw.Draw(img)
            
            # Draw border
            draw.rectangle([10, 10, width-10, height-10], outline=(59, 130, 246), width=3)
            
            # Draw title area
            draw.rectangle([20, 20, width-20, 80], fill=(51, 65, 85))
            
            # Add text (using default font)
            title = f"{diagram_type.upper()}: {topic[:40]}"
            draw.text((40, 35), title, fill=(248, 250, 252))
            
            # Add placeholder content
            draw.text((40, 120), "📊 Educational Diagram", fill=(148, 163, 184))
            draw.text((40, 160), f"Topic: {topic}", fill=(148, 163, 184))
            draw.text((40, 200), f"Type: {diagram_type}", fill=(148, 163, 184))
            draw.text((40, 280), "Note: Full diagram generation requires", fill=(100, 116, 139))
            draw.text((40, 320), "Gemini image generation API access.", fill=(100, 116, 139))
            
            # Draw some decorative elements
            draw.ellipse([width-200, height-200, width-50, height-50], outline=(59, 130, 246), width=2)
            draw.rectangle([50, height-150, 200, height-50], outline=(59, 130, 246), width=2)
            
            img.save(filepath)
            
            return {
                "success": True,
                "filepath": filepath,
                "filename": filename,
                "relative_path": f"/static/generated/images/{filename}",
                "topic": topic,
                "diagram_type": diagram_type,
                "method": "placeholder",
                "note": "Placeholder image - Gemini image generation unavailable"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create placeholder: {str(e)}",
                "filepath": None
            }
    
    def get_available_images(self) -> list:
        """Get list of available generated images"""
        files = []
        if os.path.exists(self.output_dir):
            for f in os.listdir(self.output_dir):
                if f.endswith(('.png', '.jpg', '.jpeg')):
                    files.append({
                        "filename": f,
                        "path": os.path.join(self.output_dir, f),
                        "relative_path": f"/static/generated/images/{f}"
                    })
        return files
