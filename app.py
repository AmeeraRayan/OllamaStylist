from flask import Flask, request, render_template_string, url_for
import requests
import re
import os
import time
from dotenv import load_dotenv
from pathlib import Path
if Path('.env').exists():
    load_dotenv(dotenv_path=Path('.')/'.env')
else:
    load_dotenv(dotenv_path=Path('/home/ubuntu/OllamaStylist/.env'))

app = Flask(__name__)

# AI Server private IP
AI_SERVER = "http://16.170.237.40:8000/generate"
print(AI_SERVER)
HUGGINGFACE_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
print("Token loaded:", HUGGINGFACE_TOKEN)

HEADERS = {
    "Authorization": f"Bearer {HUGGINGFACE_TOKEN}",
    "Accept": "image/png"
}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fashion Stylist</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700;400&family=Playfair+Display:wght@700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
</head>
<body>
    <div class="main-flex">
        <div class="illustration-side">
            <img src="{{ url_for('static', filename='fashion.svg') }}" alt="Fashion Illustration" class="fashion-illustration">
        </div>
        <div class="center-box">
            <div class="title-row">
                <h1 class="main-title">What should I wear for...</h1>
                <span class="icon-clothes"><i class="fa-solid fa-shirt"></i></span>
            </div>
            <form method="post" class="question-form">
                <input name="question" class="question-input" placeholder="e.g. a romantic dinner" required value="{{ request.form.get('question', '') }}">
                <input type="submit" value="Ask" class="ask-btn">
            </form>
            {% if options %}
                <h2 class="left-title">Choose an outfit:</h2>
                <form method="post" class="options-form">
                    <div class="outfit-cards">
                    {% for opt in options %}
                        <button name="choice" value="{{ opt }}" class="outfit-card">
                            <span class="option-number">{{ loop.index }}.</span>
                            <span class="option-text">{{ opt }}</span>
                        </button>
                    {% endfor %}
                    </div>
                    <input type="hidden" name="options_str" value="{{ options_str }}">
                </form>
            {% endif %}
            {% if selected_option %}
                <div class="result-section">
                    <h3 class="left-title">You chose:</h3>
                    <p class="selected-text left-align">{{ selected_option }}</p>
                    <h3 class="left-title">Here's how it might look:</h3>
                    <div class="image-container">
                        {% if image_filename %}
                        <img src="{{ url_for('static', filename=image_filename) }}" class="fashion-image">
                        {% endif %}                  
                    </div>
                </div>
            {% endif %}
            {% if duration %}
                <p style="margin-top: 1rem; color: #999;">Response time: {{ duration }} seconds</p>
            {% endif %}
        </div>
    </div>
    <script src="{{ url_for('static', filename='script.js') }}"></script>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def home():
    options = []
    selected_option = None
    image_filename = None

    if request.method == 'POST':
        if 'question' in request.form:
            question = request.form['question']
            try:
                response = requests.post(AI_SERVER, json={
                    "prompt": f"""So , You are a fashion stylist. Given the event: '{question}', respond with only 3 complete outfit ideas for a girls, in the following numbered format:
                    1.
                    2.
                    3.
                    Each outfit must be clearly,Please make sure the suggestions are stylish"""
                }, timeout=80)
                raw_text = response.json().get('response', '')
                matches = re.findall(r"\d+\.\s*(.*?)(?=\d+\.\s|$)", raw_text, re.DOTALL)
                if len(matches) < 3:
                   return {"error": "Failed to extract 3 outfits from the model. Try again or adjust the prompt."}
                options = [match.strip().replace("Format #", "").split("Option")[0].strip() for match in matches]
                if not options:
                    options = ["Sorry, no outfit suggestions were found."]
            except Exception as e:
                options = [f"AI server error: {e}"]
            options_str = "|~|".join(options)

        elif 'choice' in request.form:
            selected_option = request.form['choice']
            options_str = request.form['options_str']
            options = options_str.split("|~|")
            try:
                img_response = requests.post(
                    HUGGINGFACE_URL,
                    headers=HEADERS,
                    json={"inputs": selected_option}
                )
                if img_response.status_code == 200:
                    timestamp=str(int(time.time()))
                    image_filename = f"result_{timestamp}.png"
                    with open(f"static/{image_filename}", "wb") as f:
                        f.write(img_response.content)
                else:
                    selected_option += f" (Image error: {img_response.status_code})"
            except Exception as e:
                selected_option = f"Image generation failed: {e}"

    else:
        options_str = ""

    return render_template_string(HTML_TEMPLATE, options=options, selected_option=selected_option, options_str=options_str, image_filename=image_filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)