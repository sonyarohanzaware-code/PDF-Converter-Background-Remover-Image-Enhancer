from flask import Flask, render_template, request, send_file
from rembg import remove
from PIL import Image, ImageEnhance
import io
import pypdf

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

# 1. Background Remover Logic
@app.route('/remove-bg', methods=['POST'])
def remove_bg():
    file = request.files['image']
    input_image = Image.open(file.stream)
    output_image = remove(input_image) # rembg लाइब्रेरी बैकग्राउंड हटा देगी
    
    img_io = io.BytesIO()
    output_image.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='no-bg.png')

# 2. Image Clear / Sharpness Logic
@app.route('/clear-image', methods=['POST'])
def clear_image():
    file = request.files['image']
    img = Image.open(file.stream)
    
    # इमेज को साफ़ और शार्प करने के लिए बेसिक AI/PIL फ़िल्टर
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(3.0) # 3 गुना शार्पनेस बढ़ाएगा
    enhancer_color = ImageEnhance.Color(img)
    img = enhancer_color.enhance(1.2) # थोड़ा कलर बेहतर करेगा
    
    img_io = io.BytesIO()
    img.save(img_io, 'JPEG', quality=95)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg', as_attachment=True, download_name='clear-image.jpg')

# 3. PDF Text Reader/Converter Logic (Basic Example)
@app.route('/pdf-to-img', methods=['POST'])
def pdf_to_img():
    file = request.files['pdf']
    reader = pypdf.PdfReader(file.stream)
    
    # यहाँ हम सुरक्षा और सरलता के लिए PDF का पहला पेज टेक्स्ट के रूप में निकाल रहे हैं
    # (पूरी PDF को इमेज बनाने के लिए बड़ी लाइब्रेरी चाहिए होती है जो सर्वर भारी करती है)
    first_page = reader.pages[0]
    text = first_page.extract_text()
    
    text_file = io.BytesIO(text.encode('utf-8'))
    return send_file(text_file, mimetype='text/plain', as_attachment=True, download_name='pdf-text.txt')

if __name__ == '__main__':
    app.run(debug=True)