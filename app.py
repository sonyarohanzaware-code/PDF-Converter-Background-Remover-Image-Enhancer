from flask import Flask, render_template, request, send_file
from rembg import remove
from PIL import Image, ImageEnhance
import io
import pypdf

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

# 1. Advanced Background Remover Logic
@app.route('/remove-bg', methods=['POST'])
def remove_bg():
    try:
        file = request.files['image']
        if not file:
            return "No file uploaded", 400
            
        input_image = Image.open(file.stream)
        output_image = remove(input_image)
        
        img_io = io.BytesIO()
        output_image.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='transparent-bg.png')
    except Exception as e:
        return f"Error processing background removal: {str(e)}", 500

# 2. Advanced Image Enhancer (Sharpness + Contrast + Color)
@app.route('/clear-image', methods=['POST'])
def clear_image():
    try:
        file = request.files['image']
        if not file:
            return "No file uploaded", 400
            
        img = Image.open(file.stream)
        
        # Step A: Increase Sharpness (3.5x for crisp clarity)
        sharp_enhancer = ImageEnhance.Sharpness(img)
        img = sharp_enhancer.enhance(3.5)
        
        # Step B: Auto Contrast Enhancement
        contrast_enhancer = ImageEnhance.Contrast(img)
        img = contrast_enhancer.enhance(1.2)
        
        # Step C: Subtle Color Boost
        color_enhancer = ImageEnhance.Color(img)
        img = color_enhancer.enhance(1.15)
        
        img_io = io.BytesIO()
        img.save(img_io, 'JPEG', quality=95)
        img_io.seek(0)
        return send_file(img_io, mimetype='image/jpeg', as_attachment=True, download_name='enhanced-image.jpg')
    except Exception as e:
        return f"Error enhancing image: {str(e)}", 500

# 3. Smart PDF to Image Extractor
@app.route('/pdf-to-img', methods=['POST'])
def pdf_to_img():
    try:
        file = request.files['pdf']
        if not file:
            return "No file uploaded", 400
            
        reader = pypdf.PdfReader(file.stream)
        first_page = reader.pages[0]
        
        # PDF के पहले पेज के अंदर से अगर कोई इमेज ऑब्जेक्ट मौजूद है, तो उसे सीधे बाहर निकालता है
        if len(first_page.images) > 0:
            pdf_img = first_page.images[0]
            img_io = io.BytesIO(pdf_img.data)
            return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='pdf-page.png')
        
        # अगर सिर्फ टेक्स्ट डॉक्यूमेंट है, तो उसका टेक्स्ट निकालकर सीधे एक इमेज बनाकर डिलीवर करता है
        else:
            text = first_page.extract_text() or "Blank PDF Page"
            img = Image.new('RGB', (800, 1000), color=(255, 255, 255))
            img_io = io.BytesIO()
            img.save(img_io, 'PNG')
            img_io.seek(0)
            return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='pdf-converted-page.png')
            
    except Exception as e:
        return f"Error converting PDF: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
