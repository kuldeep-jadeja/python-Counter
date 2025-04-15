from flask import Flask, request
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

app = Flask(__name__)

def generate_salary_png_sequence(annual_salary, duration_sec=10, fps=30, font_path="Meghana.ttf", output_dir="output_frames"):
    output_dir = os.path.join(os.getcwd(), output_dir)
    os.makedirs(output_dir, exist_ok=True)

    per_frame = annual_salary / (365 * 24 * 60 * 60) / fps
    total_frames = int(duration_sec * fps)
    resolution = (1280, 720)

    font_size = 80
    font = ImageFont.truetype(font_path, font_size)

    for i in range(total_frames):
        current_salary = per_frame * i
        salary_text = f"${current_salary:,.2f}"

        img = Image.new("RGBA", resolution, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        text_size = draw.textbbox((0, 0), salary_text, font=font)
        text_width = text_size[2] - text_size[0]
        text_height = text_size[3] - text_size[1]
        position = ((resolution[0] - text_width) // 2, (resolution[1] - text_height) // 2)

        draw.text(position, salary_text, font=font, fill=(0, 255, 0, 255))

        frame_path = os.path.join(output_dir, f"frame_{i:04d}.png")
        with open(frame_path, "wb") as f:
            img.save(f, format="PNG")

    print(f"✅ Saved {total_frames} transparent PNG frames to '{output_dir}/'")


def generate_gif_from_frames(frame_dir, output_gif="salary_counter.gif", duration=100):
    frames = []
    frame_dir = os.path.join(os.getcwd(), frame_dir)
    frame_files = sorted([
        os.path.join(frame_dir, file)
        for file in os.listdir(frame_dir)
        if file.endswith(".png")
    ])

    for filename in frame_files:
        img = Image.open(filename).convert("RGBA")
        frames.append(img)

    if frames:
        output_gif_path = os.path.join(os.getcwd(), output_gif)
        frames[0].save(
            output_gif_path,
            save_all=True,
            append_images=frames[1:],
            optimize=False,
            duration=duration,
            loop=0
        )
        print(f"✅ GIF saved as '{output_gif_path}'")


@app.route('/', methods=["GET", "POST"])
def home():
    if request.method == 'POST':
        try:
            annual_salary = float(request.form.get("annual_salary", 50000000))
            duration_sec = float(request.form.get("duration_sec", 10))
            fps = float(request.form.get("fps", 30))
        except ValueError:
            return "Invalid input.", 400
        font_path = request.form.get("font_path", "Meghana.ttf")
        output_dir = request.form.get("output_dir", "output_frames")

        generate_salary_png_sequence(
            annual_salary=annual_salary,
            duration_sec=duration_sec,
            fps=fps,
            font_path=font_path,
            output_dir=output_dir
        )

        generate_gif_from_frames(output_dir)

        return f"✅ Frames generated in '{output_dir}' and GIF saved as 'salary_counter.gif'!"

    return """
    <h2>Visual Counter Generator</h2>
    <form method="post">
        <label>Annual Salary:</label>
        <input type="text" name="annual_salary" value="50000000"><br>
        <label>Duration (sec):</label>
        <input type="text" name="duration_sec" value="10"><br>
        <label>FPS:</label>
        <input type="text" name="fps" value="30"><br>
        <label>Font Path:</label>
        <input type="text" name="font_path" value="Meghana.ttf"><br>
        <label>Output Folder:</label>
        <input type="text" name="output_dir" value="output_frames"><br><br>
        <input type="submit" value="Generate">
    </form>
    """


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
