from flask import Flask, request, jsonify
from PIL import Image
import pytesseract
import io
import base64
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In the Vercel environment, Tesseract is installed via apt-get,
# and we need to tell pytesseract where to find the executable.
if "VERCEL" in os.environ:
    pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

app = Flask(__name__)

@app.route('/')
def home():
    return "OCR Service is running."

@app.route('/ocr', methods=['POST'])
def ocr_image():
    try:
        json_data = request.get_json()
        if not json_data or 'image' not in json_data:
            return jsonify({"success": False, "error": "No image key found in JSON payload"}), 400

        base64_string = json_data['image']
        # Remove the data URI prefix if it exists (e.g., "data:image/png;base64,")
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]

        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))
        
        # Perform OCR
        text = pytesseract.image_to_string(image)
        
        return jsonify({"success": True, "text": text.strip()})
            
    except Exception as e:
        logger.error(f"Error in OCR handler: {e}", exc_info=True)
        return jsonify({"success": False, "error": f"Internal server error: {str(e)}"}), 500

# This entry point is for local testing. Vercel uses its own server.
if __name__ == '__main__':
    app.run(debug=True)
