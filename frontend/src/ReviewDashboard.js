import React, { useState, useEffect } from 'react';
import axios from 'axios';

function ReviewDashboard() {
  const [courses, setCourses] = useState([]);

  useEffect(() => {
    // In a real app, you would fetch the courses that are in review
    // For now, we'll just use some sample data
    setCourses([
      { id: 1, title: 'Course 1 for Review', status: 'In Review' },
      { id: 2, title: 'Course 2 for Review', status: 'In Review' },
    ]);
  }, []);

  const handleApprove = (courseId) => {
    axios.post(`/api/courses/${courseId}/approve`).then(() => {
      setCourses(courses.filter(c => c.id !== courseId));
    });
  };

  return (
    <div>
      <h2>Review Dashboard</h2>
      <ul>
        {courses.map(course => (
          <li key={course.id}>
            {course.title}
            <button onClick={() => handleApprove(course.id)}>Approve</button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default ReviewDashboard;
