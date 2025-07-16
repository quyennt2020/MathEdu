import React, { useState } from 'react';
import axios from 'axios';

function Flashcard({ concept, userId }) {
  const [showAnswer, setShowAnswer] = useState(false);

  const handleCardClick = (isCorrect) => {
    setShowAnswer(!showAnswer);

    // Send interaction data to the backend
    axios.post('/api/interaction', {
      userId: userId,
      cardId: concept.id,
      isCorrect: isCorrect,
    });
  };

  return (
    <div className="flashcard" onClick={() => handleCardClick(true)}>
      {showAnswer ? (
        <div>
          <p>{concept.answer}</p>
          <button onClick={() => handleCardClick(true)}>Correct</button>
          <button onClick={() => handleCardClick(false)}>Incorrect</button>
        </div>
      ) : (
        <p>{concept.question}</p>
      )}
    </div>
  );
}

export default Flashcard;
