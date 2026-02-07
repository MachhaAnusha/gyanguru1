"""
Gemini AI Integration Module for GyanGuru
Handles all interactions with Google's Gemini 1.5 Flash API
"""

import os
import time
import google.generativeai as genai
from typing import Optional, Dict, Any


class GeminiClient:
    """Client for interacting with Google Gemini AI API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini client with API key"""
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found. Set it in environment or pass directly.")
        
        genai.configure(api_key=self.api_key)
        
        # Configure the model
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
        )
    
    def _retry_with_backoff(self, func, max_retries: int = 3):
        """Execute function with exponential backoff for rate limiting"""
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if "429" in str(e) or "quota" in str(e).lower():
                    wait_time = (2 ** attempt) * 2
                    time.sleep(wait_time)
                    continue
                raise e
        raise Exception("Max retries exceeded for API call")
    
    def generate_text_explanation(self, topic: str, depth: str = "comprehensive") -> Dict[str, Any]:
        """
        Generate educational text explanation for an ML topic
        
        Args:
            topic: The ML concept to explain
            depth: Level of detail - 'brief', 'intermediate', or 'comprehensive'
        
        Returns:
            Dictionary with explanation content
        """
        depth_instructions = {
            "brief": "Provide a concise 2-3 paragraph explanation suitable for quick reference.",
            "intermediate": "Provide a moderate explanation with key concepts, examples, and use cases in 4-6 paragraphs.",
            "comprehensive": """Provide an in-depth explanation covering:
            1. Introduction and definition
            2. Mathematical foundations (with LaTeX notation where appropriate)
            3. How it works step-by-step
            4. Key components/variants
            5. Practical applications
            6. Advantages and limitations
            7. Related concepts"""
        }
        
        prompt = f"""You are an expert Machine Learning educator. Generate a clear, educational explanation about:

**Topic:** {topic}

**Depth Level:** {depth}
{depth_instructions.get(depth, depth_instructions['comprehensive'])}

Format your response in clean Markdown with:
- Clear section headers using ##
- Code snippets where relevant (use ```python)
- Mathematical expressions where appropriate
- Bullet points for lists
- Bold for key terms

Make the content accessible yet technically accurate. Use analogies where helpful."""

        def generate():
            response = self.model.generate_content(prompt)
            return response.text
        
        content = self._retry_with_backoff(generate)
        
        return {
            "topic": topic,
            "depth": depth,
            "content": content,
            "success": True
        }
    
    def generate_code_example(self, topic: str, complexity: str = "intermediate") -> Dict[str, Any]:
        """
        Generate Python code implementation for an ML concept
        
        Args:
            topic: The ML concept to implement
            complexity: 'basic', 'intermediate', or 'advanced'
        
        Returns:
            Dictionary with code and metadata
        """
        complexity_instructions = {
            "basic": "Simple implementation with minimal dependencies, focusing on core concept.",
            "intermediate": "Complete implementation with proper structure, comments, and visualization.",
            "advanced": "Production-ready code with error handling, optimization, and comprehensive documentation."
        }
        
        prompt = f"""You are an expert Python developer specializing in Machine Learning. Generate working Python code for:

**Topic:** {topic}

**Complexity:** {complexity}
{complexity_instructions.get(complexity, complexity_instructions['intermediate'])}

Requirements:
1. Write complete, runnable Python code
2. Include detailed comments explaining each section
3. Add docstrings for functions/classes
4. Include example usage with sample data
5. Add visualization where appropriate (matplotlib/seaborn)
6. Print meaningful output to demonstrate functionality

Format:
- Start with necessary imports
- Include a main() function or if __name__ == "__main__": block
- Make code Google Colab compatible

Return ONLY the Python code without any markdown formatting or explanation outside the code."""

        def generate():
            response = self.model.generate_content(prompt)
            return response.text
        
        code = self._retry_with_backoff(generate)
        
        # Clean up the response - remove markdown code blocks if present
        code = code.strip()
        if code.startswith("```python"):
            code = code[9:]
        elif code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        code = code.strip()
        
        return {
            "topic": topic,
            "complexity": complexity,
            "code": code,
            "success": True
        }
    
    def generate_audio_script(self, topic: str) -> Dict[str, Any]:
        """
        Generate a conversational script suitable for text-to-speech
        
        Args:
            topic: The ML concept to explain
        
        Returns:
            Dictionary with audio script
        """
        prompt = f"""You are creating an educational audio lesson about Machine Learning. Generate a conversational, spoken explanation about:

**Topic:** {topic}

Requirements:
1. Write as if speaking to a student - natural, conversational tone
2. Avoid visual references (no "as you can see", "in the diagram")
3. Use clear transitions between ideas
4. Keep sentences moderate length for TTS clarity
5. Include pauses by using periods appropriately
6. Explain complex terms when first introduced
7. Target length: 3-5 minutes of speaking time (roughly 500-800 words)

Write ONLY the spoken script without stage directions or formatting."""

        def generate():
            response = self.model.generate_content(prompt)
            return response.text
        
        script = self._retry_with_backoff(generate)
        
        return {
            "topic": topic,
            "script": script.strip(),
            "success": True
        }
    
    def generate_image_prompt(self, topic: str, diagram_type: str = "architecture") -> Dict[str, Any]:
        """
        Generate a detailed prompt for educational diagram creation
        
        Args:
            topic: The ML concept to visualize
            diagram_type: 'architecture', 'flowchart', 'concept_map', or 'visualization'
        
        Returns:
            Dictionary with image generation prompt
        """
        type_instructions = {
            "architecture": "Create a clear system/neural network architecture diagram showing components and data flow.",
            "flowchart": "Create a step-by-step flowchart showing the algorithm or process flow.",
            "concept_map": "Create a concept map showing relationships between related ideas.",
            "visualization": "Create a data visualization or mathematical illustration of the concept."
        }
        
        prompt = f"""Create a detailed prompt for generating an educational diagram about:

**Topic:** {topic}
**Diagram Type:** {diagram_type}

{type_instructions.get(diagram_type, type_instructions['architecture'])}

The prompt should describe:
1. Layout and structure
2. Key components to include
3. Labels and annotations
4. Color scheme (professional, educational style)
5. Visual style (clean, modern, technical)

Return a single detailed paragraph that can be used for image generation."""

        def generate():
            response = self.model.generate_content(prompt)
            return response.text
        
        image_prompt = self._retry_with_backoff(generate)
        
        return {
            "topic": topic,
            "diagram_type": diagram_type,
            "prompt": image_prompt.strip(),
            "success": True
        }
