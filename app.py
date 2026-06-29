from flask import Flask, render_template, request, send_file
from PIL import Image, ImageEnhance, ImageFilter
import io
import requests
import qrcode
import random
import string

app = Flask(__name__)

# SECURITY NOTE: Replace with your actual remove.bg API key
REMOVE_BG_API_KEY = "YOUR_ACTUAL_API_KEY_HERE"

@app.route('/')
def home():
    return render_template('index.html')

# 1. AI BACKGROUND REMOVER
@app.route('/remove-bg', methods=['POST'])
def remove_bg():
    try:
        if 'image' not in request.files:
            return "Error: No file uploaded", 400
        file = request.files['image']
        if file.filename == '':
            return "Error: No file selected", 400

        response = requests.post(
            'https://api.remove.bg/v1.0/removebg',
            files={'image_file': file.stream.read()},
            data={'size': 'auto'},
            headers={'X-Api-Key': REMOVE_BG_API_KEY},
        )
        
        if response.status_code == requests.codes.ok:
            img_io = io.BytesIO(response.content)
            img_io.seek(0)
            return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='bg_removed.png')
        else:
            return f"AI Server Error: Please verify your API Key.", 500
    except Exception as e:
        return f"Server Error: {str(e)}", 500

# 2. HD IMAGE RESIZER
@app.route('/resize-image', methods=['POST'])
def resize_image():
    try:
        if 'image' not in request.files: return "No file uploaded", 400
        file = request.files['image']
        width = int(request.form.get('width', 800))
        height = int(request.form.get('height', 600))
        
        img = Image.open(file.stream)
        resized_img = img.resize((width, height), Image.Resampling.LANCZOS)
        
        img_io = io.BytesIO()
        resized_img.save(img_io, 'JPEG', quality=100, subsampling=0)
        img_io.seek(0)
        return send_file(img_io, mimetype='image/jpeg', as_attachment=True, download_name=f'resized_{width}x{height}.jpg')
    except Exception as e:
        return f"Error processing image: {str(e)}", 500

# 3. IMAGE TO PDF CONVERTER
@app.route('/image-to-pdf', methods=['POST'])
def image_to_pdf():
    try:
        if 'image' not in request.files: return "No file uploaded", 400
        file = request.files['image']
        
        img = Image.open(file.stream).convert('RGB')
        pdf_io = io.BytesIO()
        img.save(pdf_io, 'PDF', quality=100)
        pdf_io.seek(0)
        return send_file(pdf_io, mimetype='application/pdf', as_attachment=True, download_name='converted_doc.pdf')
    except Exception as e:
        return f"Conversion failed: {str(e)}", 500

# 4. IMAGE FORMAT CONVERTER
@app.route('/convert-format', methods=['POST'])
def convert_format():
    try:
        if 'image' not in request.files: return "No file uploaded", 400
        file = request.files['image']
        target_format = request.form.get('format', 'PNG').upper()
        
        img = Image.open(file.stream)
        img_io = io.BytesIO()
        
        if target_format in ['JPG', 'JPEG']:
            img = img.convert('RGB')
            img.save(img_io, 'JPEG', quality=95)
            mimetype = 'image/jpeg'
        elif target_format == 'WEBP':
            img = img.convert('RGB')
            img.save(img_io, 'WEBP', quality=95)
            mimetype = 'image/webp'
        else:
            img.save(img_io, 'PNG')
            mimetype = 'image/png'
            
        img_io.seek(0)
        return send_file(img_io, mimetype=mimetype, as_attachment=True, download_name=f'converted.{target_format.lower()}')
    except Exception as e:
        return f"Format conversion failed: {str(e)}", 500

# 5. SMART IMAGE COMPRESSOR
@app.route('/compress-image', methods=['POST'])
def compress_image():
    try:
        if 'image' not in request.files: return "No file uploaded", 400
        file = request.files['image']
        quality = int(request.form.get('quality', 60))
        
        img = Image.open(file.stream).convert('RGB')
        img_io = io.BytesIO()
        img.save(img_io, 'JPEG', quality=quality)
        img_io.seek(0)
        return send_file(img_io, mimetype='image/jpeg', as_attachment=True, download_name='compressed_image.jpg')
    except Exception as e:
        return f"Compression failed: {str(e)}", 500

# 6. QR CODE GENERATOR
@app.route('/generate-qr', methods=['POST'])
def generate_qr():
    try:
        text = request.form.get('qr_text', '').strip()
        if not text: return "Text is required", 400
        
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(text)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='qrcode.png')
    except Exception as e:
        return f"QR Generation failed: {str(e)}", 500

# 7. WORD COUNTER & CASE CONVERTER
@app.route('/text-tools', methods=['POST'])
def text_tools():
    try:
        text = request.form.get('text_input', '')
        action = request.form.get('action', 'count')
        
        if action == 'upper': result = text.upper()
        elif action == 'lower': result = text.lower()
        else:
            words = len(text.split())
            chars = len(text)
            result = f"Analysis Report:\n------------------\nWord Count: {words}\nCharacter Count: {chars}"
            
        text_file = io.BytesIO(result.encode('utf-8'))
        return send_file(text_file, mimetype='text/plain', as_attachment=True, download_name='text_analysis.txt')
    except Exception as e:
        return f"Text processing failed: {str(e)}", 500

# 8. SECURE PASSWORD GENERATOR
@app.route('/generate-password', methods=['POST'])
def generate_password():
    try:
        length = int(request.form.get('length', 12))
        if length < 6 or length > 64: return "Length must be between 6 and 64", 400
        
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(random.choice(characters) for _ in range(length))
        
        text_file = io.BytesIO(password.encode('utf-8'))
        return send_file(text_file, mimetype='text/plain', as_attachment=True, download_name='secure_password.txt')
    except Exception as e:
        return f"Password generation failed: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
