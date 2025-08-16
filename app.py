import os
import uuid
import pathlib
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Configure the generative AI model
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    # This error is raised if the GOOGLE_API_KEY is not set.
    # We will handle this gracefully in the create_game endpoint.
    pass

app = Flask(__name__)

def log_interaction(log_data):
    """Appends a log entry to the design loop log file."""
    os.makedirs('logs', exist_ok=True)
    log_file = 'logs/design_loop.jsonl'

    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        **log_data
    }

    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

@app.route('/')
def serve_index():
    """Serves the main index.html page."""
    return send_from_directory('public', 'index.html')

def clean_ai_response(text):
    """
    Removes markdown backticks and the 'javascript' keyword from the AI's response.
    """
    if text.strip().startswith("```javascript"):
        text = text.strip()[11:] # Remove ```javascript
        if text.strip().endswith("```"):
            text = text.strip()[:-3] # Remove ```
    return text.strip()

@app.route('/api/v1/games', methods=['POST'])
def create_game():
    """
    Creates a new game session by calling the Gemini AI with a user prompt.
    """
    log_data = {"interactionType": "create", "success": False}
    try:
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY is not set.")

        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({"error": "Invalid request, 'prompt' is required."}), 400

        user_prompt = data['prompt']
        log_data["userPrompt"] = user_prompt

        session_id = f"session_{uuid.uuid4().hex[:8]}"
        log_data["sessionId"] = session_id
        session_dir = pathlib.Path('public/games') / session_id
        os.makedirs(session_dir, exist_ok=True)

        with open('templates/kaboom_template.html', 'r') as f:
            template_content = f.read()

        model = genai.GenerativeModel('gemini-1.5-flash')

        super_prompt = f"""<role>You are an expert game developer specializing in the Kaboom.js framework.</role>
<task>Your task is to write the JavaScript code for a simple game based on the user's prompt.</task>
<constraints>
- The code must be self-contained and run within the Kaboom.js environment provided.
- DO NOT include any HTML, CSS, or markdown formatting (like ```javascript).
- ONLY respond with the raw JavaScript code for the game logic.
- Use only built-in Kaboom.js functions and assets (e.g., `loadBean()`, `rect()`, `pos()`, `onKeyDown()`).
- The game canvas is already initialized. Do not include `kaboom()` initialization code.
</constraints>
<user_idea>
{user_prompt}
</user_idea>
"""
        log_data["aiPrompt"] = super_prompt

        response = model.generate_content(super_prompt)
        log_data["aiResponse"] = response.text

        ai_generated_code = clean_ai_response(response.text)

        placeholder = '// AI_GENERATED_CODE_WILL_BE_INSERTED_HERE'
        output_code = template_content.replace(placeholder, ai_generated_code)
        log_data["outputCode"] = output_code

        output_path = session_dir / 'game.html'
        with open(output_path, 'w') as f:
            f.write(output_code)

        log_data["success"] = True
        game_url = f"/games/{session_id}/game.html"
        return jsonify({'sessionId': session_id, 'gameUrl': game_url})

    except Exception as e:
        error_message = str(e)
        print(f"Create game failed: {error_message}")
        log_data["error"] = error_message
        return jsonify({"error": f"An internal error occurred: {error_message}"}), 500
    finally:
        log_interaction(log_data)

def clean_html_response(text):
    """
    Removes markdown backticks and the 'html' keyword from the AI's response.
    """
    if text.strip().startswith("```html"):
        text = text.strip()[7:] # Remove ```html
        if text.strip().endswith("```"):
            text = text.strip()[:-3] # Remove ```
    return text.strip()

@app.route('/api/v1/games/<session_id>/refine', methods=['POST'])
def refine_game(session_id):
    """
    Refines an existing game by sending its code and a new prompt to the AI.
    """
    log_data = {
        "interactionType": "refine",
        "sessionId": session_id,
        "success": False
    }
    try:
        data = request.get_json()
        if not data or 'prompt' not in data or 'code' not in data:
            return jsonify({"error": "Invalid request, 'prompt' and 'code' are required."}), 400

        user_prompt = data['prompt']
        current_code = data['code']
        log_data["userPrompt"] = user_prompt
        log_data["inputCode"] = current_code

        refine_prompt = f"""<role>You are an expert game developer who specializes in editing code for the Kaboom.js framework.</role>
<task>Your task is to modify the complete HTML source code of an existing game based on a user's request.</task>
<user_request>
{user_prompt}
</user_request>
<current_html_code>
{current_code}
</current_html_code>
<instructions>
- Read the user's request and the provided HTML code carefully.
- Modify the JavaScript portion within the `<script>` tag to implement the user's request.
- **Crucially, respond with ONLY the complete, full, and updated HTML source code for the entire file.**
- Do not add any explanations, comments, or markdown formatting around the code. Just the raw HTML.
</instructions>
"""
        log_data["aiPrompt"] = refine_prompt

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(refine_prompt)
        log_data["aiResponse"] = response.text

        updated_code = clean_html_response(response.text)
        log_data["outputCode"] = updated_code

        game_file_path = pathlib.Path('public/games') / session_id / 'game.html'
        if not game_file_path.is_file():
            raise FileNotFoundError("Game session file not found.")

        with open(game_file_path, 'w') as f:
            f.write(updated_code)

        log_data["success"] = True
        return jsonify({"message": "Game refined successfully."})

    except Exception as e:
        error_message = str(e)
        print(f"Refine game failed: {error_message}")
        log_data["error"] = error_message
        return jsonify({"error": f"An internal error occurred: {error_message}"}), 500
    finally:
        log_interaction(log_data)


@app.route('/<path:path>')
def serve_static_file(path):
    """Serves static files from the 'public' directory."""
    return send_from_directory('public', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
