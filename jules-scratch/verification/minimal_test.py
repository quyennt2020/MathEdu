import subprocess
import time
from playwright.sync_api import sync_playwright, Error

def run_minimal_test():
    """
    Starts the server, launches Playwright with special flags,
    and attempts to navigate to the homepage.
    """
    server_process = None
    try:
        # 1. Start the Flask server as a background process
        print("Starting server...")
        server_process = subprocess.Popen(["python", "app.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(5)  # Give the server a moment to start

        # Check if server started correctly
        if server_process.poll() is not None:
            stdout, stderr = server_process.communicate()
            print(f"Server failed to start. Exit code: {server_process.returncode}")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return

        print("Server started. Launching browser...")

        with sync_playwright() as p:
            # 2. Launch Chromium with flags for restricted environments
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-gpu',
                    '--disable-dev-shm-usage'
                ]
            )
            page = browser.new_page()

            # 3. Attempt to navigate to the page
            print("Navigating to http://localhost:8080...")
            page.goto("http://localhost:8080", timeout=30000)

            # 4. If navigation is successful, print a success message
            print("\n--- TEST SUCCEEDED! ---")
            print(f"Successfully navigated to page with title: '{page.title()}'")

            browser.close()

    except Error as e:
        print("\n--- TEST FAILED ---")
        print(f"A Playwright error occurred: {e}")
        # The error message from Playwright is often very informative.

    except Exception as e:
        print("\n--- SCRIPT FAILED ---")
        print(f"An unexpected error occurred: {e}")

    finally:
        # 5. Ensure the server process is always terminated
        if server_process and server_process.poll() is None:
            print("Stopping server...")
            server_process.kill()
            server_process.wait()
            print("Server stopped.")

if __name__ == "__main__":
    run_minimal_test()
