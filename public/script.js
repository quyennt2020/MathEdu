document.addEventListener('DOMContentLoaded', () => {
    // --- Get DOM Elements ---
    const promptInput = document.getElementById('prompt-input');
    const createBtn = document.getElementById('create-btn');
    const gameFrame = document.getElementById('game-frame');

    const refineControls = document.getElementById('refine-controls');
    const refinePromptInput = document.getElementById('refine-prompt-input');
    const refineBtn = document.getElementById('refine-btn');

    // --- State Management ---
    let currentSession = null;

    // --- Event Listener for Initial Creation ---
    createBtn.addEventListener('click', () => {
        const prompt = promptInput.value.trim();
        if (prompt === '') {
            alert('Please enter a game idea first!');
            return;
        }

        createBtn.disabled = true;
        createBtn.textContent = 'Creating...';
        gameFrame.src = 'about:blank';

        fetch('/api/v1/games', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: prompt }),
        })
        .then(response => response.json().then(data => ({ ok: response.ok, data })))
        .then(({ ok, data }) => {
            if (!ok) throw new Error(data.error || 'Unknown error');

            currentSession = { sessionId: data.sessionId, gameUrl: data.gameUrl };
            gameFrame.src = data.gameUrl;

            // --- Enable Refine Controls ---
            refineControls.style.display = 'flex';
            refineBtn.disabled = false;
        })
        .catch(handleError)
        .finally(() => {
            createBtn.disabled = false;
            createBtn.textContent = 'Create Game';
        });
    });

    // --- Event Listener for Refinement ---
    refineBtn.addEventListener('click', () => {
        const refinePrompt = refinePromptInput.value.trim();
        if (refinePrompt === '') {
            alert('Please enter a refinement instruction!');
            return;
        }
        if (!currentSession) {
            alert('You must create a game before you can refine it.');
            return;
        }

        refineBtn.disabled = true;
        refineBtn.textContent = 'Refining...';

        // 1. Fetch the current game's source code
        fetch(currentSession.gameUrl)
            .then(response => response.text())
            .then(gameSourceCode => {
                // 2. Call the refine API with the source code
                return fetch(`/api/v1/games/${currentSession.sessionId}/refine`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        prompt: refinePrompt,
                        code: gameSourceCode,
                    }),
                });
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => {
                        throw new Error(err.error || 'Failed to refine game.');
                    });
                }
                return response.json();
            })
            .then(() => {
                // 3. Reload the iframe to show the updated game
                // Appending a timestamp busts the cache
                gameFrame.src = `${currentSession.gameUrl}?t=${new Date().getTime()}`;
                refinePromptInput.value = ''; // Clear the input
            })
            .catch(handleError)
            .finally(() => {
                refineBtn.disabled = false;
                refineBtn.textContent = 'Refine Game';
            });
    });

    function handleError(error) {
        console.error('An error occurred:', error);
        alert(`An error occurred: ${error.message}`);
    }
});
