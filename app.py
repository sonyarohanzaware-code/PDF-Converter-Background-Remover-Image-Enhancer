from flask import Flask, render_template, request, send_file
from PIL import Image
import io
import requests

app = Flask(__name__)

# Secure Area: Place your remove.bg API key here
REMOVE_BG_API_KEY = "2eLnhvGX1or4voxbHCsLRYrE"

@app.route('/')
def home():
    return render_template('index.html')

# 1. Premium AI Background Remover
@app.route('/remove-bg', methods=['POST'])
def remove_bg():
    if 'image' not in request.files:
        return "Error: No file uploaded", 400
    file = request.files['image']
    if file.filename == '':
        return "Error: Empty file selection", 400

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
        return f"AI Server Error: {response.text}", 500

# 2. HD Image Resizer (No Quality Loss)
@app.route('/resize-image', methods=['POST'])
def resize_image():
    if 'image' not in request.files:
        return "Error: No file uploaded", 400
        
    file = request.files['image']
    width = int(request.form.get('width', 800))
    height = int(request.form.get('height', 600))
    
    img = Image.open(file.stream)
    
    # Using Resampling.LANCZOS for maximum pixel clarity and sharpness
    resized_img = img.resize((width, height), Image.Resampling.LANCZOS)
    
    img_io = io.BytesIO()
    # Saving with 100% maximum quality to prevent any compression blur
    resized_img.save(img_io, 'JPEG', quality=100, subsampling=0)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg', as_attachment=True, download_name=f'resized_{width}x{height}.jpg')

# 3. Crystal-Clear Image to PDF Converter
@app.route('/image-to-pdf', methods=['POST'])
def image_to_pdf():
    if 'image' not in request.files:
        return "Error: No file uploaded", 400
        
    file = request.files['image']
    img = Image.open(file.stream)
    
    # Converting image to clean RGB without dropping DPI or colors
    pdf_img = img.convert('RGB')
    
    pdf_io = io.BytesIO()
    # Saving with maximum resolution settings for crystal clear printing
    pdf_img.save(pdf_io, 'PDF', quality=100)
    pdf_io.seek(0)
    return send_file(pdf_io, mimetype='application/pdf', as_attachment=True, download_name='clear_document.pdf')

if __name__ == '__main__':
    app.run(debug=True)
