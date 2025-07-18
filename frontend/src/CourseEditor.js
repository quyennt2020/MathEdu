import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import FlashcardReview from './FlashcardReview';

function CourseEditor() {
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [generatedFlashcards, setGeneratedFlashcards] = useState([]);

  useEffect(() => {
    // In a real app, you would fetch the user's courses
    // For now, we'll just use some sample data
    setCourses([
      { id: 1, title: 'My First Course', videos: [{ id: 1, title: 'Video 1' }, { id: 2, title: 'Video 2' }] },
      { id: 2, title: 'My Second Course', videos: [{ id: 3, title: 'Video 3' }] },
    ]);
  }, []);

  const handleCourseSelection = (course) => {
    setSelectedCourse(course);
  };

  const onDragEnd = (result) => {
    if (!result.destination) {
      return;
    }

    const items = Array.from(selectedCourse.videos);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);

    setSelectedCourse({ ...selectedCourse, videos: items });
  };

  const handleGenerateFlashcards = (video) => {
    axios.post('/api/generate_flashcards', {
      transcript: video.transcript, // Assuming the transcript is available on the video object
    }).then(response => {
      setGeneratedFlashcards(response.data);
    });
  };

  return (
    <div>
      <h2>Course Editor</h2>
      <div>
        <h3>My Courses</h3>
        <ul>
          {courses.map(course => (
            <li key={course.id} onClick={() => handleCourseSelection(course)}>
              {course.title}
            </li>
          ))}
        </ul>
      </div>
      {selectedCourse && (
        <div>
          <h3>{selectedCourse.title}</h3>
          <DragDropContext onDragEnd={onDragEnd}>
            <Droppable droppableId="videos">
              {(provided) => (
                <ul {...provided.droppableProps} ref={provided.innerRef}>
                  {selectedCourse.videos.map((video, index) => (
                    <Draggable key={video.id} draggableId={String(video.id)} index={index}>
                      {(provided) => (
                        <li
                          ref={provided.innerRef}
                          {...provided.draggableProps}
                          {...provided.dragHandleProps}
                        >
                          {video.title}
                          <button onClick={() => handleGenerateFlashcards(video)}>
                            Auto-generate Flashcards
                          </button>
                        </li>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}
                </ul>
              )}
            </Droppable>
          </DragDropContext>
        </div>
      )}
      {generatedFlashcards.length > 0 && (
        <FlashcardReview generatedFlashcards={generatedFlashcards} />
      )}
    </div>
  );
}

export default CourseEditor;
