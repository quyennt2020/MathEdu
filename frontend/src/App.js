import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import Flashcard from './Flashcard';
import axios from 'axios';
import YouTube from 'react-youtube';
import Login from './Login';
import Signup from './Signup';
import CourseEditor from './CourseEditor';
import ReviewDashboard from './ReviewDashboard';
import CoursePlayer from './CoursePlayer';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';

function App() {
  const [videoId, setVideoId] = useState('dQw4w9WgXcQ');
  const [dubbedTranscript, setDubbedTranscript] = useState([]);
  const [flashcards, setFlashcards] = useState([]);
  const [newQuestion, setNewQuestion] = useState('');
  const [newAnswer, setNewAnswer] = useState('');
  const [showAll, setShowAll] = useState(false);
  const [loggedIn, setLoggedIn] = useState(false);
  const [showLogin, setShowLogin] = useState(true);
  const userId = 'user123'; // This should be replaced with the logged in user's ID
  const playerRef = useRef(null);
  const audioRef = useRef(null);

  useEffect(() => {
    if (loggedIn) {
      // Fetch flashcards when the component mounts
      axios.get(`/api/flashcards?userId=${userId}`)
        .then(response => {
          setFlashcards(response.data);
        });
    }
  }, [loggedIn, userId]);

  const handleVideoIdChange = (event) => {
    setVideoId(event.target.value);
  };

  const handleDubbing = async () => {
    axios.post('/api/dub', { videoId }).then(response => {
      setDubbedTranscript(response.data);
    });
  };

  const onPlayerReady = (event) => {
    playerRef.current = event.target;
  };

  const onPlayerStateChange = (event) => {
    if (event.data === YouTube.PlayerState.PLAYING) {
      setInterval(() => {
        const currentTime = playerRef.current.getCurrentTime();
        const currentTranscriptLine = dubbedTranscript.find(
          line => currentTime >= line.start && currentTime <= line.start + line.duration
        );
        if (currentTranscriptLine && audioRef.current) {
          audioRef.current.src = currentTranscriptLine.audio_src;
          audioRef.current.play();
        }
      }, 1000);
    }
  };

  const handleCreateFlashcard = () => {
    axios.post('/api/flashcards', {
      userId: userId,
      question: newQuestion,
      answer: newAnswer,
    }).then(response => {
      setFlashcards([...flashcards, response.data]);
      setNewQuestion('');
      setNewAnswer('');
    });
  };

  const handleUpdateFlashcard = (updatedFlashcard) => {
    setFlashcards(flashcards.map(f => f.id === updatedFlashcard.id ? updatedFlashcard : f));
  };

  const handleDeleteFlashcard = (flashcardId) => {
    setFlashcards(flashcards.filter(f => f.id !== flashcardId));
  };

  const getDueFlashcards = () => {
    const now = new Date();
    return flashcards.filter(f => new Date(f.next_review) <= now);
  };

  const opts = {
    height: '390',
    width: '640',
    playerVars: {
      // https://developers.google.com/youtube/player_parameters
      autoplay: 1,
    },
  };

  if (!loggedIn) {
    return (
      <div className="App">
        <header className="App-header">
          {showLogin ? (
            <div>
              <Login />
              <p>
                Don't have an account?{' '}
                <button onClick={() => setShowLogin(false)}>Sign up</button>
              </p>
            </div>
          ) : (
            <div>
              <Signup />
              <p>
                Already have an account?{' '}
                <button onClick={() => setShowLogin(true)}>Log in</button>
              </p>
            </div>
          )}
        </header>
      </div>
    );
  }

  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <nav>
            <ul>
              <li>
                <Link to="/">Home</Link>
              </li>
              <li>
                <Link to="/courses">Course Editor</Link>
              </li>
              <li>
                <Link to="/review">Review Dashboard</Link>
              </li>
              <li>
                <Link to="/player">Course Player</Link>
              </li>
            </ul>
          </nav>

          <Routes>
            <Route path="/courses" element={<CourseEditor />} />
            <Route path="/review" element={<ReviewDashboard />} />
            <Route path="/player" element={<CoursePlayer />} />
            <Route path="/" element={
              <div>
                <h1>YouTube Video Dubber</h1>
                <div className="video-input">
                  <input
                    type="text"
                    placeholder="Enter YouTube Video ID"
                    value={videoId}
                    onChange={handleVideoIdChange}
                  />
                  <button onClick={handleDubbing}>Dub Video</button>
                </div>
                <div className="video-container">
                  <YouTube videoId={videoId} opts={opts} onReady={onPlayerReady} onStateChange={onPlayerStateChange} />
                </div>
                <audio ref={audioRef} />
                <div className="create-flashcard">
                  <h2>Create New Flashcard</h2>
                  <input
                    type="text"
                    placeholder="Question"
                    value={newQuestion}
                    onChange={(e) => setNewQuestion(e.target.value)}
                  />
                  <input
                    type="text"
                    placeholder="Answer"
                    value={newAnswer}
                    onChange={(e) => setNewAnswer(e.target.value)}
                  />
                  <button onClick={handleCreateFlashcard}>Create</button>
                </div>
                <div className="flashcard-container">
                  <h2>
                    {showAll ? 'All Flashcards' : 'Due for Review'}
                    <button onClick={() => setShowAll(!showAll)}>
                      {showAll ? 'Show Due' : 'Show All'}
                    </button>
                  </h2>
                  {(showAll ? flashcards : getDueFlashcards()).map((flashcard) => (
                    <Flashcard
                      key={flashcard.id}
                      concept={flashcard}
                      userId={userId}
                      onUpdate={handleUpdateFlashcard}
                      onDelete={handleDeleteFlashcard}
                    />
                  ))}
                </div>
              </div>
            } />
          </Routes>
        </header>
      </div>
    </Router>
  );
}

export default App;
