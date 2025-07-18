import React, { useState } from 'react';
import axios from 'axios';

function FlashcardReview({ generatedFlashcards }) {
  const [flashcards, setFlashcards] = useState(generatedFlashcards);

  const handleSave = (flashcard) => {
    // In a real app, you would save the flashcard to the database
    console.log('Saving flashcard:', flashcard);
  };

  const handleInputChange = (index, event) => {
    const newFlashcards = [...flashcards];
    newFlashcards[index][event.target.name] = event.target.value;
    setFlashcards(newFlashcards);
  };

  return (
    <div>
      <h2>Review Generated Flashcards</h2>
      {flashcards.map((flashcard, index) => (
        <div key={index}>
          <input
            type="text"
            name="question"
            value={flashcard.question}
            onChange={(e) => handleInputChange(index, e)}
          />
          <input
            type="text"
            name="answer"
            value={flashcard.answer}
            onChange={(e) => handleInputChange(index, e)}
          />
          <button onClick={() => handleSave(flashcard)}>Save</button>
        </div>
      ))}
    </div>
  );
}

export default FlashcardReview;
