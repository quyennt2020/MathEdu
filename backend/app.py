from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory storage for user interactions (for simplicity)
user_interactions = {}

@app.route('/api/interaction', methods=['POST'])
def record_interaction():
    """
    Records a user's interaction with a flashcard.
    """
    data = request.get_json()
    user_id = data.get('userId')
    card_id = data.get('cardId')
    is_correct = data.get('isCorrect')

    if user_id not in user_interactions:
        user_interactions[user_id] = {}

    user_interactions[user_id][card_id] = {
        'is_correct': is_correct,
        'timestamp': 'now' # in a real app, you would use a proper timestamp
    }

    return jsonify({'status': 'success'})

@app.route('/api/review_suggestions', methods=['GET'])
def get_review_suggestions():
    """
    Provides suggestions for which flashcards to review.
    """
    user_id = request.args.get('userId')
    if user_id not in user_interactions:
        return jsonify({'suggestions': []})

    # Simple suggestion logic: suggest cards the user got wrong.
    suggestions = []
    for card_id, interaction in user_interactions[user_id].items():
        if not interaction['is_correct']:
            suggestions.append(card_id)

    return jsonify({'suggestions': suggestions})

if __name__ == '__main__':
    app.run(debug=True)
