from flask import Flask, request, send_file
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

        img = Image.new("RGBA", resolution, (0, 0, 0, 0))  # transparent background
        draw = ImageDraw.Draw(img)

        text_size = draw.textbbox((0, 0), salary_text, font=font)
        text_width = text_size[2] - text_size[0]
        text_height = text_size[3] - text_size[1]
        position = ((resolution[0] - text_width) // 2, (resolution[1] - text_height) // 2)

        draw.text(position, salary_text, font=font, fill=(0, 255, 0, 255))

        frame_path = os.path.join(output_dir, f"frame_{i:04d}.png")
        img.save(frame_path, format="PNG")

    print(f"Saved {total_frames} PNG frames to '{output_dir}/'")


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

        # Convert to P mode and set transparency
        alpha = img.getchannel('A')
        mask = Image.eval(alpha, lambda a: 255 if a <= 0 else 0)
        img = img.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)
        img.paste(255, mask)  # set transparency index
        img.info['transparency'] = 255

        frames.append(img)

    if frames:
        output_gif_path = os.path.join(os.getcwd(), output_gif)
        frames[0].save(
            output_gif_path,
            save_all=True,
            append_images=frames[1:],
            optimize=False,
            duration=duration,
            loop=0,
            transparency=255,
            disposal=2  # clear before drawing next
        )
        print(f"Transparent GIF saved as '{output_gif_path}'")


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

        return '''
        <p>Transparent GIF saved as <code>salary_counter.gif</code>.</p>
        <a href="/download" download>
            <button>Download GIF</button>
        </a>
        <a href="/view" target="_blank" style="margin-left:10px;">
            <button>View GIF</button>
        </a>
        '''

    return """
    <html>
    <head>
        <title>Visual Counter Generator</title>
        <style>
            body {
                margin: 0;
                padding: 0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #0f0f0f, #1f1f1f);
                color: #00ffcc;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .panel {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 30px 40px;
                backdrop-filter: blur(10px);
                box-shadow: 0 0 15px rgba(0, 255, 204, 0.3);
            }
            h2 {
                margin-top: 0;
                text-align: center;
                font-size: 26px;
                color: #00ffe1;
            }
            label {
                display: block;
                margin-top: 15px;
                margin-bottom: 5px;
                font-size: 14px;
            }
            input[type="text"] {
                width: 100%;
                padding: 10px;
                font-size: 16px;
                background: rgba(0, 0, 0, 0.6);
                border: 1px solid #00ffcc;
                color: #00ffcc;
                border-radius: 8px;
                outline: none;
                transition: border 0.3s;
            }
            input[type="text"]:focus {
                border-color: #00ffe1;
                box-shadow: 0 0 5px #00ffe1;
            }
            input[type="submit"] {
                margin-top: 20px;
                width: 100%;
                padding: 12px;
                background: #00ffcc;
                color: #000;
                border: none;
                font-size: 16px;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            input[type="submit"]:hover {
                background: #00ffe1;
                box-shadow: 0 0 10px #00ffe1, 0 0 20px #00ffe1 inset;
            }
        </style>
    </head>
    <body>
        <div class="panel">
            <h2>Visual Counter Generator</h2>
            <form method="post">
                <label>Annual Salary:</label>
                <input type="text" name="annual_salary" value="50000000">
                
                <label>Duration (sec):</label>
                <input type="text" name="duration_sec" value="10">
                
                <label>FPS:</label>
                <input type="text" name="fps" value="30">
                
                <label>Font Path:</label>
                <input type="text" name="font_path" value="Meghana.ttf">
                
                <label>Output Folder:</label>
                <input type="text" name="output_dir" value="output_frames">
                
                <input type="submit" value="Generate GIF">
            </form>
        </div>
    </body>
    </html>
    """


@app.route('/download')
def download():
    gif_path = os.path.join(os.getcwd(), "salary_counter.gif")
    return send_file(gif_path, as_attachment=True)


@app.route('/view')
def view():
    gif_path = os.path.join(os.getcwd(), "salary_counter.gif")
    return send_file(gif_path, mimetype='image/gif')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
