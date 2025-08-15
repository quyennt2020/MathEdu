# AI Game Generator (MVP)

This project is a proof-of-concept (MVP) for an AI-powered game generator. It allows a user to enter a text prompt describing a game idea, and it generates a simple, playable web-based game using the Kaboom.js framework.

The current MVP uses a mocked AI response, meaning it generates the same simple platformer game regardless of the user's input.

## Project Structure

- `app.py`: The core backend server built with Python and Flask. It handles API requests and serves all files.
- `public/`: Contains all static frontend files.
  - `index.html`: The main web page for the user interface.
  - `script.js`: The client-side JavaScript that communicates with the backend.
- `templates/`: Contains HTML templates used by the server.
  - `kaboom_template.html`: The base template for a Kaboom.js game. The AI-generated code is injected into this template.
- `requirements.txt`: A list of Python dependencies for the project.

## Setup and Installation

### Prerequisites

- Python 3.x
- pip (Python package installer)

### Installation

1.  Clone the repository to your local machine.
2.  Navigate to the project directory.
3.  Install the required Python packages using pip:
    ```bash
    pip install -r requirements.txt
    ```

## How to Run

1.  Make sure you are in the root directory of the project.
2.  Run the Flask application:
    ```bash
    python app.py
    ```
3.  The server will start, typically on `http://localhost:8080`. You will see output in your terminal indicating the server is running.

## How to Use

1.  Open your web browser and navigate to `http://localhost:8080`.
2.  You will see the AI Game Generator interface.
3.  Type an idea for a game into the text box (e.g., "A red square that can jump").
4.  Click the "Create Game" button.
5.  The generated game will appear in the iframe on the right-hand side of the screen.