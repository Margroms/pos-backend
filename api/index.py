from fastapi import FastAPI, File, UploadFile, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
import pytesseract
import io
import base64
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class ImageModel(BaseModel):
    image: str

@app.get("/")
async def home():
    return {"message": "Menu OCR Service is running with FastAPI"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "Menu OCR Service"}

@app.post("/ocr")
async def ocr_image(request: Request, file: UploadFile = None):
    try:
        logger.info("OCR endpoint hit")
        image_data = None

        # Handle multipart form data (file upload)
        if file:
            logger.info(f"Processing uploaded file: {file.filename}")
            image_data = await file.read()
        
        # Handle JSON with base64 encoded image or raw image data
        else:
            content_type = request.headers.get('content-type', '').lower()
            if 'application/json' in content_type:
                try:
                    json_data = await request.json()
                    base64_string = json_data['image']
                    if ',' in base64_string:
                        base64_string = base64_string.split(',')[1]
                    image_data = base64.b64decode(base64_string)
                    logger.info("Processing base64 encoded image from JSON")
                except Exception as e:
                    logger.error(f"Invalid JSON or base64 image: {str(e)}")
                    raise HTTPException(status_code=400, detail=f"Invalid JSON or base64 image: {str(e)}")
            elif content_type.startswith('image/'):
                image_data = await request.body()
                logger.info("Processing raw image data")

        if not image_data:
            raise HTTPException(status_code=400, detail="No image file found in request")

        logger.info(f"Processing image, size: {len(image_data)} bytes")
        
        # Process image with PIL and Tesseract
        try:
            image = Image.open(io.BytesIO(image_data))
            logger.info(f"Image loaded: {image.format}, size: {image.size}, mode: {image.mode}")
            
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            logger.info("Starting OCR extraction...")
            text = pytesseract.image_to_string(image, config='--psm 6')
            
            if not text or not text.strip():
                logger.warning("No text extracted from image")
                raise HTTPException(status_code=400, detail="No text found in image")
            
            logger.info(f"OCR completed. Text length: {len(text)}")
            logger.info(f"OCR preview: {text[:200]}...")
            
            return {"success": True, "text": text}
            
        except HTTPException as http_exc:
            raise http_exc # Re-raise HTTPException
        except Exception as img_error:
            logger.error(f"Error processing image: {str(img_error)}")
            raise HTTPException(status_code=500, detail=f"Image processing error: {str(img_error)}")
            
    except HTTPException as http_exc:
        return JSONResponse(status_code=http_exc.status_code, content={"success": False, "error": http_exc.detail})
    except Exception as e:
        logger.error(f"Error in OCR handler: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content={"success": False, "error": f"Internal server error: {str(e)}"})

# To run locally for testing: uvicorn api.index:app --reload
