from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
import random
import io
import os


def pointillize(image, radius=4, step=8):
    """Apply a simple pointillism effect."""
    w, h = image.size
    result = Image.new('RGBA', (w, h), (255, 255, 255, 0))
    draw = ImageDraw.Draw(result)
    for y in range(0, h, step):
        for x in range(0, w, step):
            color = image.getpixel((x, y))
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
    return result

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

        # Create a base canvas
        canvas_size = (800, 800)
        collage = Image.new('RGBA', canvas_size, (255, 255, 255, 255))

        # Randomly place, rotate, and resize each image
        for img in images:
            scale = random.uniform(0.4, 0.8)
            w = int(canvas_size[0] * scale)
            h = int(img.height * w / img.width)
            img_resized = img.resize((w, h), Image.LANCZOS)
            img_rotated = img_resized.rotate(random.uniform(-30, 30), expand=True)
            x = random.randint(0, max(0, canvas_size[0] - img_rotated.width))
            y = random.randint(0, max(0, canvas_size[1] - img_rotated.height))
            collage.alpha_composite(img_rotated, (x, y))

        collage_height = canvas_size[1] + 50  # extra space for style text

        style_lower = style_prompt.lower()
        if 'pointillism' in style_lower or 'pointilism' in style_lower:
            collage = pointillize(collage)

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
        collage_width = canvas_size[0]
        draw.text(((collage_width - text_width) / 2, collage_height - 40), style_prompt, fill='black', font=font)

        output = io.BytesIO()
        collage.save(output, format='PNG')
        output.seek(0)
        return send_file(output, mimetype='image/png', as_attachment=True, download_name='collage.png')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
