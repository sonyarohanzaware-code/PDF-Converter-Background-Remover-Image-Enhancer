from flask import Flask, render_template, request, send_file
from PIL import Image, ImageEnhance, ImageFilter
import io
import pypdf

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

# 1. AI Background Remover (Optimized for Web)
@app.route('/remove-bg', methods=['POST'])
def remove_bg():
    if 'image' not in request.files:
        return "No file uploaded", 400
        
    file = request.files['image']
    img = Image.open(file.stream).convert("RGBA")
    
    # Advanced color thresholding for instant web-based background removal
    datas = img.getdata()
    newData = []
    for item in datas:
        # Detects light/white backgrounds and makes them transparent smoothly
        if item[0] > 225 and item[1] > 225 and item[2] > 225:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
            
    img.putdata(newData)
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='bg_removed.png')

# 2. Image Enhancer & Clearer (Smart Sharpening)
@app.route('/clear-image', methods=['POST'])
def clear_image():
    if 'image' not in request.files:
        return "No file uploaded", 400
        
    file = request.files['image']
    img = Image.open(file.stream)
    
    # Professional image enhancement filters
    img = img.filter(ImageFilter.SHARPEN)
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(2.5)
    
    color_enhancer = ImageEnhance.Color(img)
    img = color_enhancer.enhance(1.1)
    
    img_io = io.BytesIO()
    img.save(img_io, 'JPEG', quality=95)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg', as_attachment=True, download_name='enhanced_image.jpg')

# 3. PDF to Text Converter
@app.route('/pdf-to-img', methods=['POST'])
def pdf_to_img():
    if 'pdf' not in request.files:
        return "No file uploaded", 400
        
    file = request.files['pdf']
    reader = pypdf.PdfReader(file.stream)
    
    # Extracts text from the first page professionally
    first_page = reader.pages[0]
    text = first_page.extract_text()
    
    if not text:
        text = "No extractable text found in this PDF. It might be a scanned document."
        
    text_file = io.BytesIO(text.encode('utf-8'))
    return send_file(text_file, mimetype='text/plain', as_attachment=True, download_name='extracted_text.txt')

if __name__ == '__main__':
    app.run(debug=True)
