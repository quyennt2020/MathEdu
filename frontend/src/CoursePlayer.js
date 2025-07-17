import React, { useState, useEffect } from 'react';
import axios from 'axios';
import YouTube from 'react-youtube';

function CoursePlayer() {
  const [course, setCourse] = useState(null);
  const [currentVideo, setCurrentVideo] = useState(null);

  useEffect(() => {
    // In a real app, you would fetch the course data
    // For now, we'll just use some sample data
    setCourse({
      id: 1,
      title: 'My First Course',
      videos: [
        { id: 1, title: 'Video 1', youtube_id: 'dQw4w9WgXcQ' },
        { id: 2, title: 'Video 2', youtube_id: 'oHg5SJYRHA0' },
      ],
    });
  }, []);

  useEffect(() => {
    if (course) {
      setCurrentVideo(course.videos[0]);
    }
  }, [course]);

  const handleVideoSelection = (video) => {
    setCurrentVideo(video);
  };

  const opts = {
    height: '390',
    width: '640',
    playerVars: {
      autoplay: 1,
    },
  };

  if (!course) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h2>{course.title}</h2>
      <div>
        <h3>Videos</h3>
        <ul>
          {course.videos.map(video => (
            <li key={video.id} onClick={() => handleVideoSelection(video)}>
              {video.title}
            </li>
          ))}
        </ul>
      </div>
      {currentVideo && (
        <div>
          <h3>{currentVideo.title}</h3>
          <YouTube videoId={currentVideo.youtube_id} opts={opts} />
        </div>
      )}
    </div>
  );
}

export default CoursePlayer;
