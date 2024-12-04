import React, { useState } from "react";
import "./QueryForm.css";

function QueryForm() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [error, setError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setResults([]);
    try {
      const response = await fetch("http://localhost:5001/nlp-query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
      const data = await response.json();
      if (data.error) {
        setError(data.error);
      } else {
        setResults(data.courses || []);
      }
    } catch (err) {
      setError("Failed to fetch results. Please try again.");
    }
  };

  return (
    <div className="query-form">
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask about courses (e.g., 'Show me all graduate CSE courses with 3 credits')"
        />
        <button type="submit" disabled={!query}>
          Search
        </button>
      </form>
      {error && <div className="error">{error}</div>}
      <div className="response-container">
        {results.length > 0 && (
          <ul>
            {results.map((course, index) => (
              <li key={index}>
                <h3>{course.course_name} ({course.catalog_number})</h3>
                <p><strong>Description:</strong> {course.description}</p>
                <p><strong>Department:</strong> {course.department}</p>
                <p><strong>Level:</strong> {course.course_level}</p>
                <p><strong>Credits:</strong> {course.credits}</p>
                <p><strong>Schedule:</strong> {course.schedule_days} ({course.start_time} - {course.end_time})</p>
                <p><strong>Facility:</strong> {course.facility}</p>
                <p><strong>Prerequisites:</strong> {course.prerequisites}</p>
                <p><strong>Grading Basis:</strong> {course.grading_basis}</p>
                <p><strong>Academic Group:</strong> {course.academic_group}</p>
                <p><strong>Availability:</strong></p>
                <ul>
                  {course.availability.map((term, idx) => (
                    <li key={idx}>
                      Term: {term.term}, Seats Available: {term.available}, Enrolled: {term.enrolled}, Capacity: {term.capacity}
                    </li>
                  ))}
                </ul>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default QueryForm;
