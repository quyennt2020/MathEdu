import React, { useState, useEffect } from 'react';
import './App.css';
import Flashcard from './Flashcard';
import axios from 'axios';

function App() {
  const [videoId, setVideoId] = useState('dQw4w9WgXcQ');
  const [dubbedAudio, setDubbedAudio] = useState(null);
  const [flashcards, setFlashcards] = useState([]);
  const [newQuestion, setNewQuestion] = useState('');
  const [newAnswer, setNewAnswer] = useState('');
  const [showAll, setShowAll] = useState(false);
  const userId = 'user123'; // In a real app, you would get this from authentication

  useEffect(() => {
    // Fetch flashcards when the component mounts
    axios.get(`/api/flashcards?userId=${userId}`)
      .then(response => {
        setFlashcards(response.data);
      });
  }, [userId]);

  const handleVideoIdChange = (event) => {
    setVideoId(event.target.value);
  };

  const handleDubbing = async () => {
    // In a real application, you would make an API call to your backend here
    // to get the dubbed audio. For now, we'll just simulate it.
    // This will be replaced with a proper API call in a later step.
    console.log(`Dubbing video with ID: ${videoId}`);
    // Simulate a delay to mimic a network request
    await new Promise(resolve => setTimeout(resolve, 2000));
    // In a real app, the backend would return the URL to the dubbed audio file.
    // For now, we'll use a placeholder.
    setDubbedAudio('/output.mp3');
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

  return (
    <div className="App">
      <header className="App-header">
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
          <iframe
            title="YouTube Video Player"
            width="560"
            height="315"
            src={`https://www.youtube.com/embed/${videoId}`}
            frameBorder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          ></iframe>
        </div>
        {dubbedAudio && (
          <div className="audio-container">
            <h2>Dubbed Audio</h2>
            <audio controls>
              <source src={dubbedAudio} type="audio/mpeg" />
              Your browser does not support the audio element.
            </audio>
          </div>
        )}
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
      </header>
    </div>
  );
}

export default App;
