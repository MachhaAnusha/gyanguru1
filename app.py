"""
GyanGuru: AI-Powered ML Learning Assistant
Main Flask Application
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import utility modules
from utils.gemini_utils import GeminiClient
from utils.tts_utils import TextToSpeech
from utils.image_utils import ImageGenerator
from utils.code_utils import CodeProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'gyanguru-secret-key-2024')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Initialize utility clients (lazy initialization)
gemini_client = None
tts_client = None
image_generator = None
code_processor = None


def get_gemini_client():
    """Get or create Gemini client"""
    global gemini_client
    if gemini_client is None:
        try:
            gemini_client = GeminiClient()
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise
    return gemini_client


def get_tts_client():
    """Get or create TTS client"""
    global tts_client
    if tts_client is None:
        tts_client = TextToSpeech()
    return tts_client


def get_image_generator():
    """Get or create image generator"""
    global image_generator
    if image_generator is None:
        image_generator = ImageGenerator()
    return image_generator


def get_code_processor():
    """Get or create code processor"""
    global code_processor
    if code_processor is None:
        code_processor = CodeProcessor()
    return code_processor


# ============================================================================
# Page Routes
# ============================================================================

@app.route('/')
def index():
    """Home page / Dashboard"""
    return render_template('index.html')


@app.route('/text')
def text_page():
    """Text explanation page"""
    return render_template('text.html')


@app.route('/code')
def code_page():
    """Code generation page"""
    return render_template('code.html')


@app.route('/audio')
def audio_page():
    """Audio learning page"""
    return render_template('audio.html')


@app.route('/image')
def image_page():
    """Image visualization page"""
    return render_template('image.html')


# ============================================================================
# API Routes
# ============================================================================

@app.route('/api/generate-text', methods=['POST'])
def api_generate_text():
    """Generate text explanation for ML topic"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        topic = data.get('topic', '').strip()
        depth = data.get('depth', 'comprehensive')
        
        if not topic:
            return jsonify({"error": "Topic is required"}), 400
        
        if depth not in ['brief', 'intermediate', 'comprehensive']:
            depth = 'comprehensive'
        
        logger.info(f"Generating text explanation for: {topic} (depth: {depth})")
        
        client = get_gemini_client()
        result = client.generate_text_explanation(topic, depth)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Text generation error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/generate-code', methods=['POST'])
def api_generate_code():
    """Generate Python code for ML topic"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        topic = data.get('topic', '').strip()
        complexity = data.get('complexity', 'intermediate')
        
        if not topic:
            return jsonify({"error": "Topic is required"}), 400
        
        if complexity not in ['basic', 'intermediate', 'advanced']:
            complexity = 'intermediate'
        
        logger.info(f"Generating code for: {topic} (complexity: {complexity})")
        
        # Generate code using Gemini
        client = get_gemini_client()
        result = client.generate_code_example(topic, complexity)
        
        if not result.get('success'):
            return jsonify({"error": "Failed to generate code"}), 500
        
        # Process code for dependencies
        processor = get_code_processor()
        formatted = processor.format_code_response(
            result['code'],
            topic,
            complexity
        )
        
        # Save code file
        file_info = processor.save_code_file(result['code'], topic)
        
        response = {
            "success": True,
            "topic": topic,
            "complexity": complexity,
            "code": formatted['code'],
            "dependencies": formatted['dependencies'],
            "colab_setup": formatted['colab_setup'],
            "local_setup": formatted['local_setup'],
            "line_count": formatted['line_count'],
            "download_url": file_info.get('relative_path') if file_info.get('success') else None
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Code generation error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/generate-audio', methods=['POST'])
def api_generate_audio():
    """Generate audio lesson for ML topic"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        topic = data.get('topic', '').strip()
        
        if not topic:
            return jsonify({"error": "Topic is required"}), 400
        
        logger.info(f"Generating audio lesson for: {topic}")
        
        # Generate script using Gemini
        client = get_gemini_client()
        script_result = client.generate_audio_script(topic)
        
        if not script_result.get('success'):
            return jsonify({"error": "Failed to generate audio script"}), 500
        
        # Convert to speech
        tts = get_tts_client()
        audio_result = tts.text_to_speech(script_result['script'])
        
        if not audio_result.get('success'):
            return jsonify({"error": f"TTS failed: {audio_result.get('error')}"}), 500
        
        response = {
            "success": True,
            "topic": topic,
            "script": script_result['script'],
            "audio_url": audio_result['relative_path'],
            "filename": audio_result['filename'],
            "word_count": audio_result['word_count'],
            "estimated_duration": audio_result['estimated_duration_minutes']
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Audio generation error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/generate-image', methods=['POST'])
def api_generate_image():
    """Generate visual diagram for ML topic"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        topic = data.get('topic', '').strip()
        diagram_type = data.get('diagram_type', 'architecture')
        
        if not topic:
            return jsonify({"error": "Topic is required"}), 400
        
        if diagram_type not in ['architecture', 'flowchart', 'concept_map', 'visualization']:
            diagram_type = 'architecture'
        
        logger.info(f"Generating {diagram_type} diagram for: {topic}")
        
        # Generate image prompt using Gemini
        client = get_gemini_client()
        prompt_result = client.generate_image_prompt(topic, diagram_type)
        
        if not prompt_result.get('success'):
            return jsonify({"error": "Failed to generate image prompt"}), 500
        
        # Generate image
        generator = get_image_generator()
        image_result = generator.generate_diagram(
            prompt_result['prompt'],
            topic,
            diagram_type
        )
        
        if not image_result.get('success'):
            return jsonify({"error": f"Image generation failed: {image_result.get('error')}"}), 500
        
        response = {
            "success": True,
            "topic": topic,
            "diagram_type": diagram_type,
            "image_url": image_result['relative_path'],
            "filename": image_result['filename'],
            "method": image_result.get('method', 'unknown'),
            "prompt": prompt_result['prompt']
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Image generation error: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# File Download Routes
# ============================================================================

@app.route('/download/code/<filename>')
def download_code(filename):
    """Download generated code file"""
    try:
        processor = get_code_processor()
        filepath = os.path.join(processor.output_dir, filename)
        
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        return jsonify({"error": "File not found"}), 404
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/download/audio/<filename>')
def download_audio(filename):
    """Download generated audio file"""
    try:
        tts = get_tts_client()
        filepath = os.path.join(tts.output_dir, filename)
        
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        return jsonify({"error": "File not found"}), 404
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/download/image/<filename>')
def download_image(filename):
    """Download generated image file"""
    try:
        generator = get_image_generator()
        filepath = os.path.join(generator.output_dir, filename)
        
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        return jsonify({"error": "File not found"}), 404
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return render_template('index.html'), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    logger.error(f"Server error: {e}")
    return jsonify({"error": "Internal server error"}), 500


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == '__main__':
    # Check for API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or api_key == 'your-api-key-here':
        print("\n" + "="*60)
        print("⚠️  WARNING: GEMINI_API_KEY not set!")
        print("="*60)
        print("To use GyanGuru, you need a Google Gemini API key.")
        print("1. Get your key at: https://aistudio.google.com/apikey")
        print("2. Set it: export GEMINI_API_KEY='your-key-here'")
        print("="*60 + "\n")
    
    # Run Flask app
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"\n🚀 Starting GyanGuru ML Learning Assistant")
    print(f"📍 Access at: http://{host}:{port}")
    print(f"📚 Features: Text | Code | Audio | Images\n")
    
    app.run(host=host, port=port, debug=debug)
