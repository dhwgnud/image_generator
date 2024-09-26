from flask import Flask, render_template, request, send_from_directory
from PIL import Image, ImageDraw, ImageFont
from rembg import remove
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def create_images(uploaded_image, num_images, custom_text):
    fixed_size = (1080, 1080)
    background_color = (255, 255, 255)
    combined_image = Image.new("RGB", fixed_size, background_color)

    input_image = Image.open(uploaded_image)
    output_image = remove(input_image)

    original_size = output_image.size
    scale_ratio = min(fixed_size[0] / original_size[0], fixed_size[1] / original_size[1]) * 2 / 3
    new_size = (int(original_size[0] * scale_ratio), int(original_size[1] * scale_ratio))
    output_image = output_image.resize(new_size, Image.Resampling.LANCZOS)

    x_offset = (fixed_size[0] - output_image.size[0]) // 2
    y_offset = (fixed_size[1] - new_size[1]) // 3  # 이미지가 항상 중앙에 오도록
    combined_image.paste(output_image, (x_offset, y_offset), output_image)

    draw = ImageDraw.Draw(combined_image)
    font_size = int((min(new_size) / 3) * 0.6)
    font_path = "/Library/Fonts/AppleSDGothicNeo.ttc"
    font = ImageFont.truetype(font_path, font_size)

    text = custom_text

    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (fixed_size[0] - text_width) // 2
    text_y = y_offset + new_size[1] + 20  # 이미지 바로 아래에 빈 공간 제공

    padding = 20
    rect_x0 = text_x - padding
    rect_y0 = text_y - padding
    rect_x1 = text_x + text_width + padding
    rect_y1 = text_y + text_height + padding

    draw.rounded_rectangle(
        [(rect_x0, rect_y0), (rect_x1, rect_y1)],
        radius=30,
        outline="black",
        width=3,
        fill="white"
    )

    draw.text((text_x, text_y), text, font=font, fill=(0, 0, 0))

    combined_image.save(f"static/combined_image_{num_images}.png")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        num_images = int(request.form.get("num_images", 1))
        custom_text = request.form.get("custom_text", " ")

        uploaded_file = request.files.get("image_file")
        
        if uploaded_file and uploaded_file.filename != '':
            create_images(uploaded_file, num_images, custom_text)
            return render_template("index.html", num_images=num_images, custom_text=custom_text)

    return render_template("index.html")

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("static", filename)

if __name__ == "__main__":
    app.run(debug=True)
