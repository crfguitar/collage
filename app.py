from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
import io
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        style_prompt = request.form.get('style', '')
        files = request.files.getlist('images')
        images = []
        for f in files:
            if f and f.filename:
                img = Image.open(f.stream).convert('RGBA')
                images.append(img)
        if not images:
            return render_template('index.html', error='No images uploaded')

        # Determine collage size (simple grid)
        cols = int(len(images) ** 0.5)
        if cols * cols < len(images):
            cols += 1
        width = max(img.width for img in images)
        height = max(img.height for img in images)
        collage_width = cols * width
        rows = (len(images) + cols - 1) // cols
        collage_height = rows * height + 50  # extra space for style text

        collage = Image.new('RGBA', (collage_width, collage_height), (255, 255, 255, 255))

        for idx, img in enumerate(images):
            x = (idx % cols) * width
            y = (idx // cols) * height
            collage.paste(img.resize((width, height)), (x, y))

        # Add style prompt text at bottom
        draw = ImageDraw.Draw(collage)
        font_size = 20
        try:
            font = ImageFont.truetype('arial.ttf', font_size)
        except IOError:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), style_prompt, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        draw.text(((collage_width - text_width) / 2, collage_height - 40), style_prompt, fill='black', font=font)

        output = io.BytesIO()
        collage.save(output, format='PNG')
        output.seek(0)
        return send_file(output, mimetype='image/png', as_attachment=True, download_name='collage.png')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
