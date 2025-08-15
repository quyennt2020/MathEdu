import os
import uuid
import pathlib
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
    # 1. Check for API Key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return jsonify({"error": "GOOGLE_API_KEY is not set. Please configure it in your .env file."}), 500

    # 2. Get data from request
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "Invalid request, 'prompt' is required."}), 400
    user_prompt = data['prompt']

    # 3. Generate session and paths
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    session_dir = pathlib.Path('public/games') / session_id
    os.makedirs(session_dir, exist_ok=True)

    # 4. Read the HTML template
    try:
        with open('templates/kaboom_template.html', 'r') as f:
            template_content = f.read()
    except FileNotFoundError:
        return jsonify({"error": "Kaboom template not found."}), 500

    # 5. Call the real AI
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Construct the "Super Prompt"
        super_prompt = f"""
        You are an expert game developer specializing in the Kaboom.js framework.
        Your task is to write the JavaScript code for a simple game based on the user's prompt.

        **Constraints:**
        - The code must be self-contained and run within the Kaboom.js environment provided.
        - DO NOT include any HTML, CSS, or markdown formatting (like ```javascript).
        - ONLY respond with the raw JavaScript code for the game logic.
        - Use only built-in Kaboom.js functions and assets (e.g., `loadBean()`, `rect()`, `pos()`, `onKeyDown()`). Do not try to load external assets.
        - The game canvas is already initialized. Do not include `kaboom()` initialization code.

        **User's Game Idea:**
        "{user_prompt}"

        Now, write the JavaScript code for this game.
        """

        response = model.generate_content(super_prompt)

        # Clean the response to get raw JS
        ai_generated_code = clean_ai_response(response.text)

    except Exception as e:
        print(f"AI generation failed: {e}")
        return jsonify({"error": f"Failed to generate game code from AI. Details: {str(e)}"}), 500

    # 6. Inject the AI-generated code into the template
    placeholder = '// AI_GENERATED_CODE_WILL_BE_INSERTED_HERE'
    game_code = template_content.replace(placeholder, ai_generated_code)

    # 7. Save the new game file
    output_path = session_dir / 'game.html'
    with open(output_path, 'w') as f:
        f.write(game_code)

    # 8. Return the success response
    game_url = f"/games/{session_id}/game.html"
    return jsonify({
        'sessionId': session_id,
        'gameUrl': game_url
    })

@app.route('/<path:path>')
def serve_static_file(path):
    """Serves static files from the 'public' directory."""
    return send_from_directory('public', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
