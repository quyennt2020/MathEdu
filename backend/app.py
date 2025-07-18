from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flashcards.db'
app.config['SECRET_KEY'] = 'supersecretkey'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_reminder_emails():
    users_to_remind = User.query.join(Flashcard).filter(Flashcard.next_review <= datetime.utcnow()).all()
    for user in users_to_remind:
        message = Mail(
            from_email='from_email@example.com',
            to_emails=user.email,
            subject='Time to review your flashcards!',
            html_content='<strong>You have flashcards due for review. Log in to the app to review them!</strong>')
        try:
            sendgrid_client = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sendgrid_client.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e)

scheduler = BackgroundScheduler()
scheduler.add_job(func=send_reminder_emails, trigger="interval", days=1)
scheduler.start()

from functools import wraps

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(80), default='Creator', nullable=False) # Creator, Editor, Admin

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                return jsonify({'error': 'Unauthorized'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    videos = db.relationship('Video', backref='course', lazy=True)

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    youtube_id = db.Column(db.String(80), nullable=False)
    status = db.Column(db.String(80), default='Draft', nullable=False) # Draft, In Review, Published
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

class Flashcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
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

from scripts.download_transcript import download_transcript
from scripts.translate_transcript import translate_text
from scripts.generate_audio import generate_audio_segments
from scripts.generate_flashcards import generate_flashcards_from_transcript
import os

@app.route('/api/dub', methods=['POST'])
def dub_video():
    data = request.get_json()
    video_id = data.get('videoId')

    # 1. Download transcript
    transcript = download_transcript(video_id)
    if not transcript:
        return jsonify({'error': 'Could not download transcript'}), 500

    # 2. Translate transcript
    for line in transcript:
        line['text'] = translate_text(line['text'])

    # 3. Generate audio segments
    audio_dir = os.path.join('static', 'audio', video_id)
    audio_files = generate_audio_segments(transcript, output_dir=audio_dir)

    # 4. Return transcript with audio filenames
    for i, line in enumerate(transcript):
        line['audio_src'] = os.path.join(audio_dir, f"segment_{i}.mp3")

    return jsonify(transcript)


@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    new_user = User(
        username=data['username'],
        email=data['email'],
        password=data['password'] # In a real app, you should hash the password
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.password == data['password']: # In a real app, you should check the hashed password
        login_user(user)
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401

@app.route('/api/logout')
def logout():
    logout_user()
    return jsonify({'status': 'success'})

@app.route('/api/courses', methods=['POST'])
@role_required('Creator')
def create_course():
    data = request.get_json()
    new_course = Course(
        title=data['title'],
        description=data.get('description'),
        creator_id=current_user.id
    )
    db.session.add(new_course)
    db.session.commit()
    return jsonify(new_course.to_dict())

@app.route('/api/courses/<int:course_id>', methods=['PUT'])
@role_required('Creator')
def update_course(course_id):
    course = Course.query.get(course_id)
    if not course or course.creator_id != current_user.id:
        return jsonify({'error': 'Not found or unauthorized'}), 404

    data = request.get_json()
    course.title = data.get('title', course.title)
    course.description = data.get('description', course.description)
    db.session.commit()
    return jsonify(course.to_dict())

@app.route('/api/courses/<int:course_id>/videos', methods=['POST'])
@role_required('Creator')
def add_video_to_course(course_id):
    course = Course.query.get(course_id)
    if not course or course.creator_id != current_user.id:
        return jsonify({'error': 'Not found or unauthorized'}), 404

    data = request.get_json()
    new_video = Video(
        title=data['title'],
        youtube_id=data['youtube_id'],
        course_id=course.id
    )
    db.session.add(new_video)
    db.session.commit()
    return jsonify(new_video.to_dict())

@app.route('/api/courses/<int:course_id>/submit', methods=['POST'])
@role_required('Creator')
def submit_course(course_id):
    course = Course.query.get(course_id)
    if not course or course.creator_id != current_user.id:
        return jsonify({'error': 'Not found or unauthorized'}), 404

    for video in course.videos:
        video.status = 'In Review'
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/api/courses/<int:course_id>/approve', methods=['POST'])
@role_required('Editor')
def approve_course(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Not found'}), 404

    for video in course.videos:
        video.status = 'Published'
    db.session.commit()
    return jsonify({'status': 'success'})


@app.route('/api/generate_flashcards', methods=['POST'])
def auto_generate_flashcards():
    data = request.get_json()
    transcript = data.get('transcript')
    if not transcript:
        return jsonify({'error': 'Transcript not provided'}), 400

    flashcards = generate_flashcards_from_transcript(transcript)
    return jsonify(flashcards)

if __name__ == '__main__':
    app.run(debug=True)
