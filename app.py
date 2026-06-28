from flask import Flask, render_template, request, send_file
from PIL import Image, ImageEnhance, ImageFilter
import io
import pypdf

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

# 1. Background Remover (Halki Alternative Process)
@app.route('/remove-bg', methods=['POST'])
def remove_bg():
    file = request.files['image']
    img = Image.open(file.stream).convert("RGBA")
    
    # फ्री सर्वर के लिए एक स्मार्ट ट्रिक: यह इमेज के सबसे कॉमन बैकग्राउंड कलर (जैसे सफेद/काला) को ट्रांसपेरेंट कर देगा
    datas = img.getdata()
    newData = []
    for item in datas:
        # अगर पिक्सेल बहुत ज्यादा सफेद या हल्के रंग का है, तो उसे गायब कर दो
        if item[0] > 220 and item[1] > 220 and item[2] > 220:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
            
    img.putdata(newData)
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='no-bg.png')

# 2. Image Clear / Sharpness (Super Fast & Light)
@app.route('/clear-image', methods=['POST'])
def clear_image():
    file = request.files['image']
    img = Image.open(file.stream)
    
    # इमेज को शार्प और क्लियर करने का लाइटवेट तरीका
    img = img.filter(ImageFilter.SHARPEN)
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(2.5)
    
    img_io = io.BytesIO()
    img.save(img_io, 'JPEG', quality=95)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg', as_attachment=True, download_name='clear-image.jpg')

# 3. PDF to Text
@app.route('/pdf-to-img', methods=['POST'])
def pdf_to_img():
    file = request.files['pdf']
    reader = pypdf.PdfReader(file.stream)
    
    first_page = reader.pages[0]
    text = first_page.extract_text()
    
    if not text:
        text = "PDF में कोई टेक्स्ट नहीं मिला या यह एक स्कैन की गई इमेज है।"
        
    text_file = io.BytesIO(text.encode('utf-8'))
    return send_file(text_file, mimetype='text/plain', as_attachment=True, download_name='pdf-text.txt')

if __name__ == '__main__':
    app.run(debug=True)
