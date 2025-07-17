from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flashcards.db'
db = SQLAlchemy(app)

class Flashcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False)
    question = db.Column(db.String(200), nullable=False)
    answer = db.Column(db.String(200), nullable=False)
    next_review = db.Column(db.DateTime, default=datetime.utcnow)
    ease_factor = db.Column(db.Float, default=2.5)
    interval = db.Column(db.Integer, default=1)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'question': self.question,
            'answer': self.answer,
            'next_review': self.next_review.isoformat(),
        }

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/api/flashcards', methods=['GET'])
def get_flashcards():
    user_id = request.args.get('userId')
    flashcards = Flashcard.query.filter_by(user_id=user_id).all()
    return jsonify([f.to_dict() for f in flashcards])

@app.route('/api/flashcards', methods=['POST'])
def create_flashcard():
    data = request.get_json()
    new_flashcard = Flashcard(
        user_id=data['userId'],
        question=data['question'],
        answer=data['answer']
    )
    db.session.add(new_flashcard)
    db.session.commit()
    return jsonify(new_flashcard.to_dict())

@app.route('/api/flashcards/<int:flashcard_id>', methods=['PUT'])
def update_flashcard(flashcard_id):
    flashcard = Flashcard.query.get(flashcard_id)
    if not flashcard:
        return jsonify({'error': 'Flashcard not found'}), 404

    data = request.get_json()
    flashcard.question = data.get('question', flashcard.question)
    flashcard.answer = data.get('answer', flashcard.answer)
    db.session.commit()
    return jsonify(flashcard.to_dict())

@app.route('/api/flashcards/<int:flashcard_id>', methods=['DELETE'])
def delete_flashcard(flashcard_id):
    flashcard = Flashcard.query.get(flashcard_id)
    if not flashcard:
        return jsonify({'error': 'Flashcard not found'}), 404

    db.session.delete(flashcard)
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/api/review', methods=['POST'])
def review_flashcard():
    data = request.get_json()
    flashcard_id = data.get('flashcardId')
    quality = data.get('quality') # Quality of recall (0-5)

    flashcard = Flashcard.query.get(flashcard_id)
    if not flashcard:
        return jsonify({'error': 'Flashcard not found'}), 404

    # SM-2 algorithm implementation
    if quality >= 3:
        if flashcard.interval == 1:
            flashcard.interval = 6
        else:
            flashcard.interval = round(flashcard.interval * flashcard.ease_factor)
        flashcard.ease_factor = flashcard.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        if flashcard.ease_factor < 1.3:
            flashcard.ease_factor = 1.3
    else:
        flashcard.interval = 1

    flashcard.next_review = datetime.utcnow() + timedelta(days=flashcard.interval)
    db.session.commit()

    return jsonify(flashcard.to_dict())

if __name__ == '__main__':
    app.run(debug=True)
