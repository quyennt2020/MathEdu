import subprocess
import time
from playwright.sync_api import sync_playwright, expect, Error

def run_verification():
    """
    Runs the full frontend verification: starts server, automates UI to generate a game,
    and takes a screenshot of the result inside the iframe.
    """
    server_process = None
    try:
        # 1. Start the Flask server
        print("Starting server...")
        # Using preexec_fn=os.setsid to create a new process group.
        # This allows us to kill the server and all its children reliably.
        server_process = subprocess.Popen(
            ["python", "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, # Redirect stderr to stdout
            text=True
        )
        time.sleep(5)  # Allow server to initialize

        if server_process.poll() is not None:
            output = server_process.communicate()[0]
            raise RuntimeError(f"Server failed to start. Output:\n{output}")

        print("Server started successfully.")

        with sync_playwright() as p:
            # 2. Launch browser with special flags
            browser = p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage']
            )
            page = browser.new_page()

            # 3. Navigate and interact
            print("Navigating to http://localhost:8080...")
            page.goto("http://localhost:8080", timeout=30000)

            prompt_text = "A game with a green player that can jump and a red enemy that moves back and forth"
            print(f"Typing prompt: '{prompt_text}'")
            page.locator("#prompt-input").fill(prompt_text)

            print("Clicking 'Create Game' button...")
            page.locator("#create-btn").click()

            # 4. Wait for the game to load in the iframe
            print("Waiting for game to load in iframe...")
            game_iframe = page.frame_locator("#game-frame")

            # The most reliable way to know the game is ready is to wait for the canvas element
            # that Kaboom.js creates to be present and visible inside the iframe.
            canvas_in_iframe = game_iframe.locator("canvas")
            expect(canvas_in_iframe).to_be_visible(timeout=60000) # Generous 60s timeout for the AI call

            print("Game has loaded in iframe!")
            time.sleep(2) # A small extra wait for assets to potentially render

            # 5. Take a screenshot
            screenshot_path = "jules-scratch/verification/game_screenshot.png"
            print(f"Taking screenshot of the game iframe and saving to {screenshot_path}...")
            game_iframe.locator("body").screenshot(path=screenshot_path)

            print("Screenshot successful.")
            browser.close()

    except Exception as e:
        print("\n--- VERIFICATION FAILED ---")
        print(f"An error occurred: {e}")

        # Kill the server to flush its output
        if server_process and server_process.poll() is None:
            server_process.kill()

        # Read and print the server logs for debugging
        server_output = server_process.communicate()[0]
        print("\n--- Server Logs ---")
        print(server_output)
        print("--- End Server Logs ---\n")

        # Re-raise the exception to fail the process
        raise

    finally:
        # 6. Clean up the server process
        if server_process and server_process.poll() is None:
            print("Stopping server...")
            server_process.kill()
            server_process.wait()
            print("Server stopped.")

if __name__ == "__main__":
    run_verification()
