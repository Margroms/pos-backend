#!/bin/bash
# Vercel build script to install Tesseract OCR

# Install Tesseract
sudo apt-get update
sudo apt-get install -y tesseract-ocr

# Install Python dependencies
pip install -r requirements.txt
