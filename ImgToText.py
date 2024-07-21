import google.generativeai as genai # type: ignore
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from PIL import Image
import os
import pyttsx3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads/'

model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/', methods=['GET', 'POST'])
def index():
    response_text = None
    image_url = None
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['image']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            img = Image.open(file_path)
            res = model.generate_content(img)
            response_text = res.text
            image_url = file.filename  # Store the filename for URL generation 
    return render_template('ImgToText.html', response=response_text, image_url=image_url)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/speak', methods=['POST'])
def speak():
    text = request.form.get('response')
    if text:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    return render_template('ImgToText.html')

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
