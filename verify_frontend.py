import time
import subprocess
from playwright.sync_api import sync_playwright, expect, Error

def main():
    server_process = None
    try:
        # Start the server as a background process
        print("Starting Flask server...")
        server_process = subprocess.Popen(
            ["python", "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # Give the server a moment to start
        time.sleep(5)

        with sync_playwright() as p:
            print("Launching browser...")
            # Using chromium with flags that are more likely to work in a containerized environment
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-gpu",
                    "--disable-dev-shm-usage"
                ]
            )
            page = browser.new_page()

            print("Navigating to http://localhost:8080...")
            page.goto("http://localhost:8080", timeout=30000)

            print("Successfully navigated to the page.")

            # A simple check to confirm the page is loaded correctly
            expect(page.get_by_role("heading", name="AI Game Generator")).to_be_visible()
            print("Page loaded correctly.")

            print("Typing prompt and creating game...")
            page.locator("#prompt-input").fill("A simple game with a jumping bean character")
            page.locator("#create-btn").click()

            # Wait for the iframe to point to the new game URL.
            # We locate the frame and then wait for an element *inside* the frame to be visible.
            # This is a robust way to ensure the game has loaded.
            # We give it a long timeout to account for the AI generation time.
            game_frame_locator = page.frame_locator("#game-frame")

            # Kaboom.js creates a <canvas> element for the game. Waiting for it is a good sign.
            expect(game_frame_locator.locator("canvas")).to_be_visible(timeout=60000)

            print("Game loaded in iframe. Taking screenshot...")

            # Give the game a second to draw something
            time.sleep(2)

            # Take a screenshot of the game iframe
            page.locator("#game-frame").screenshot(path="game_screenshot.png")

            print("Screenshot 'game_screenshot.png' created successfully.")

            browser.close()

    except Error as e:
        print(f"An error occurred during Playwright execution: {e}")
        # Print server logs if an error occurs
        if server_process:
            stdout, stderr = server_process.communicate()
            print("\n--- Server STDOUT ---")
            print(stdout)
            print("\n--- Server STDERR ---")
            print(stderr)
        # Re-raise the exception to ensure the script exits with a non-zero code
        raise
    finally:
        if server_process and server_process.poll() is None:
            print("Stopping Flask server...")
            server_process.terminate()
            server_process.wait()

if __name__ == "__main__":
    main()
