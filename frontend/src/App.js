import React, { useState, useEffect } from 'react';
import './App.css';
import Flashcard from './Flashcard';
import axios from 'axios';

function App() {
  const [videoId, setVideoId] = useState('dQw4w9WgXcQ');
  const [dubbedAudio, setDubbedAudio] = useState(null);
  const [flashcards, setFlashcards] = useState([
    {
      id: 1,
      question: 'What is the capital of France?',
      answer: 'Paris',
    },
    {
      id: 2,
      question: 'What is 2 + 2?',
      answer: '4',
    },
    {
      id: 3,
      question: 'What is the powerhouse of the cell?',
      answer: 'Mitochondria',
    },
  ]);
  const [reviewSuggestions, setReviewSuggestions] = useState([]);
  const userId = 'user123'; // In a real app, you would get this from authentication

  useEffect(() => {
    // Fetch review suggestions when the component mounts
    axios.get(`/api/review_suggestions?userId=${userId}`)
      .then(response => {
        setReviewSuggestions(response.data.suggestions);
      });
  }, []);

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
        <div className="flashcard-container">
          <h2>Flashcards</h2>
          {flashcards.map((flashcard) => (
            <Flashcard key={flashcard.id} concept={flashcard} userId={userId} />
          ))}
        </div>
        <div className="review-suggestions">
          <h2>Review Suggestions</h2>
          <ul>
            {reviewSuggestions.map(suggestion => (
              <li key={suggestion}>{`Card ID: ${suggestion}`}</li>
            ))}
          </ul>
        </div>
      </header>
    </div>
  );
}

export default App;
