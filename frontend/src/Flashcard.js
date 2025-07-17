import React, { useState } from 'react';
import axios from 'axios';

function Flashcard({ concept, userId, onUpdate, onDelete }) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedQuestion, setEditedQuestion] = useState(concept.question);
  const [editedAnswer, setEditedAnswer] = useState(concept.answer);

  const handleUpdate = () => {
    axios.put(`/api/flashcards/${concept.id}`, {
      question: editedQuestion,
      answer: editedAnswer,
    }).then(response => {
      onUpdate(response.data);
      setIsEditing(false);
    });
  };

  const handleDelete = () => {
    axios.delete(`/api/flashcards/${concept.id}`).then(() => {
      onDelete(concept.id);
    });
  };

  const handleReview = (quality) => {
    axios.post('/api/review', {
      flashcardId: concept.id,
      quality: quality,
    });
  };

  return (
    <div className="flashcard">
      {isEditing ? (
        <div>
          <input
            type="text"
            value={editedQuestion}
            onChange={(e) => setEditedQuestion(e.target.value)}
          />
          <input
            type="text"
            value={editedAnswer}
            onChange={(e) => setEditedAnswer(e.target.value)}
          />
          <button onClick={handleUpdate}>Save</button>
          <button onClick={() => setIsEditing(false)}>Cancel</button>
        </div>
      ) : (
        <div>
          <p>{concept.question}</p>
          <p>{concept.answer}</p>
          <button onClick={() => setIsEditing(true)}>Edit</button>
          <button onClick={handleDelete}>Delete</button>
          <div>
            <p>How well did you know this?</p>
            <button onClick={() => handleReview(5)}>Perfect</button>
            <button onClick={() => handleReview(4)}>Good</button>
            <button onClick={() => handleReview(3)}>Okay</button>
            <button onClick={() => handleReview(2)}>Bad</button>
            <button onClick={() => handleReview(1)}>Forgot</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default Flashcard;
