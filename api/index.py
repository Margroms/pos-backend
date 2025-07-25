from flask import Flask, request, jsonify
import json
import io
import logging
import base64
from PIL import Image
import pytesseract
from flask_cors import CORS


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set the path to the Tesseract binary using an absolute path for the serverless environment
pytesseract.pytesseract.tesseract_cmd = "/var/task/bin/tesseract.sh"

# Log the path for debugging
logging.info(f"Tesseract binary path: {pytesseract.pytesseract.tesseract_cmd}")

@app.route('/')
def home():
    return jsonify({"message": f"Menu OCR Service is running with"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "Menu OCR Service"})

@app.route('/ocr', methods=['POST', 'OPTIONS'])
def ocr_image():
    if request.method == 'OPTIONS':
        # Handle CORS preflight
        return '', 200
    
    try:
        logger.info("OCR endpoint hit")
        
        image_data = None
        
        # Handle multipart form data (file upload)
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename:
                logger.info(f"Processing uploaded file: {file.filename}")
                image_data = file.read()
        
        # Handle JSON with base64 encoded image
        elif request.is_json:
            json_data = request.get_json()
            if 'image' in json_data:
                try:
                    image_data = base64.b64decode(json_data['image'])
                    logger.info("Processing base64 encoded image from JSON")
                except Exception as e:
                    return jsonify({"success": False, "error": f"Invalid base64 image: {str(e)}"}), 400
        
        # Handle raw image data
        elif request.content_type and request.content_type.startswith('image/'):
            image_data = request.get_data()
            logger.info("Processing raw image data")
        
        if not image_data:
            return jsonify({"success": False, "error": "No image file found in request"}), 400
        
        logger.info(f"Processing image, size: {len(image_data)} bytes")
        
        # Process image with PIL
        try:
            image = Image.open(io.BytesIO(image_data))
            logger.info(f"Image loaded: {image.format}, size: {image.size}, mode: {image.mode}")
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # OCR with Tesseract
            logger.info("Starting OCR extraction...")
            text = pytesseract.image_to_string(image, config='--psm 6')
            
            if not text or not text.strip():
                logger.warning("No text extracted from image")
                return jsonify({"success": False, "error": "No text found in image"}), 400
            
            logger.info(f"OCR completed. Text length: {len(text)}")
            logger.info(f"OCR preview: {text[:200]}...")
            
            # Send successful response
            response = {
                "success": True,
                "text": text
            }
            
            return jsonify(response)
            
        except Exception as img_error:
            logger.error(f"Error processing image: {str(img_error)}")
            return jsonify({"success": False, "error": f"Image processing error: {str(img_error)}"}), 500
            
    except Exception as e:
        logger.error(f"Error in OCR handler: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": f"Internal server error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)