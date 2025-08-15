document.addEventListener('DOMContentLoaded', () => {
    const promptInput = document.getElementById('prompt-input');
    const createBtn = document.getElementById('create-btn');
    const gameFrame = document.getElementById('game-frame');

    if (!promptInput || !createBtn || !gameFrame) {
        console.error('Required DOM elements not found!');
        return;
    }

    createBtn.addEventListener('click', () => {
        const prompt = promptInput.value.trim();

        if (prompt === '') {
            alert('Please enter a game idea first!');
            return;
        }

        // --- Provide user feedback ---
        createBtn.disabled = true;
        createBtn.textContent = 'Creating...';
        // Clear the previous game from the iframe
        gameFrame.src = 'about:blank';

        // --- Call the backend API ---
        fetch('/api/v1/games', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ prompt: prompt }),
        })
        .then(response => {
            if (!response.ok) {
                // If the server returns an error, try to parse it as JSON
                return response.json().then(err => {
                    throw new Error(err.error || `HTTP error! Status: ${response.status}`);
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.gameUrl) {
                // Success: Load the game into the iframe
                gameFrame.src = data.gameUrl;
            } else {
                throw new Error('Invalid response from server: missing gameUrl.');
            }
        })
        .catch(error => {
            console.error('Error during game creation:', error);
            alert(`Failed to create game: ${error.message}`);
            // Show error in iframe for visibility
            gameFrame.contentWindow.document.body.innerHTML = `<div style="padding: 20px; color: red;">Error: ${error.message}</div>`;
        })
        .finally(() => {
            // --- Reset button state ---
            createBtn.disabled = false;
            createBtn.textContent = 'Create Game';
        });
    });
});
