import os
import uuid
import pathlib
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Game Generation Server is running!'

@app.route('/api/v1/games', methods=['POST'])
def create_game():
    """
    Creates a new game session based on a user prompt.
    """
    # 1. Get data from request
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "Invalid request, 'prompt' is required."}), 400

    # The prompt is not used in the MVP, but this would be where you'd pass it to the AI
    # prompt = data['prompt']

    # 2. Generate session ID and create directories
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    session_dir = pathlib.Path('public/games') / session_id
    os.makedirs(session_dir, exist_ok=True)

    # 3. Read the HTML template
    try:
        with open('templates/kaboom_template.html', 'r') as f:
            template_content = f.read()
    except FileNotFoundError:
        return jsonify({"error": "Kaboom template 'templates/kaboom_template.html' not found."}), 500

    # 4. Mock the AI call for the MVP
    # This snippet creates a player that can move and jump on a platform.
    # It uses the built-in "bean" sprite, so no external assets are needed.
    mocked_ai_code = """
    // Load the default sprite
    loadBean();

    // Add a player character
    const player = add([
        sprite("bean"),
        pos(120, 80),
        area(),
        body(), // Make it a physical body that responds to gravity
    ]);

    // Add a ground platform
    add([
        rect(width(), 48),
        pos(0, height() - 48),
        outline(4),
        area(),
        solid(), // Make it solid so other objects can't pass through
        color(127, 200, 255),
    ]);

    // Player movement controls
    const SPEED = 320;
    onKeyDown("left", () => {
        player.move(-SPEED, 0);
    });

    onKeyDown("right", () => {
        player.move(SPEED, 0);
    });

    onKeyPress("space", () => {
        // .isGrounded() is a Kaboom function that checks if the object is on a solid surface
        if (player.isGrounded()) {
            player.jump();
        }
    });
    """

    # 5. Inject the mocked code into the template
    placeholder = '// AI_GENERATED_CODE_WILL_BE_INSERTED_HERE'
    game_code = template_content.replace(placeholder, mocked_ai_code)

    # 6. Save the new game file
    output_path = session_dir / 'game.html'
    with open(output_path, 'w') as f:
        f.write(game_code)

    # 7. Return the success response
    game_url = f"/games/{session_id}/game.html"
    return jsonify({
        'sessionId': session_id,
        'gameUrl': game_url
    })

@app.route('/games/<session_id>/<path:filename>')
def serve_game(session_id, filename):
    """
    Serves the static files for a specific game session.
    """
    directory = pathlib.Path('public/games') / session_id
    return send_from_directory(directory, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
