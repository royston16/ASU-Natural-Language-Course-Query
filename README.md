# ASU CourseQuery - A Natural Language Course Query Application

CourseFinder is a powerful web application designed to make searching for ASU university courses simple and intuitive. By leveraging Elasticsearch, Flask, and React.js, this application allows users to query course data using natural language and access detailed information like schedules, seat availability, prerequisites, and more.

---

## Features
- **Natural Language Search**: Search for courses using conversational queries such as "Find graduate courses with 3 credits in CSE."
- **Comprehensive Data**: Includes details such as department, schedule, seat availability, credits, prerequisites, and more.
- **Fuzzy Matching**: Handles partial matches and typos for a seamless search experience.
- **Real-Time Results**: Instant responses powered by Elasticsearch's robust querying capabilities.

---

## Prerequisites
1. **Elasticsearch**: Ensure Elasticsearch is running locally or accessible remotely.
2. **Node.js and npm**: Required to run the frontend application.
3. **Python**: For running backend scripts and the Flask server.
4. **Environment Configuration**:
   - Update `insertionScript.py` and `queryScript.py` with your Elasticsearch credentials and OpenAI API key.

---

## Installation and Setup

1. Clone the repository:
   ```bash
   git remote add origin git@github.com:royston16/ASU-Natural-Language-Course-Query.git
   ```


3. Install Node.js dependencies:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. Start Elasticsearch: Ensure Elasticsearch is running and accessible at the host and port specified in your scripts.

---

## Usage

### Step 1: Insert Records into Elasticsearch
Run the `insertionScript.py` to fetch course data and index it into Elasticsearch. Modify the term parameter in the script to insert records for the academic terms you want to query.

```bash
python3 insertionScript.py
```

### Step 2: Start the Flask Backend
Run the `queryScript.py` Flask server to handle natural language queries and API requests.

```bash
python3 queryScript.py
```

### Step 3: Start the React Frontend
Navigate to the `frontend` directory and start the React application to provide the user interface.

```bash
cd frontend
npm start
```

---

## How It Works

### Data Collection & Indexing:
The `insertionScript.py` fetches course data from the ASU catalog API and indexes it into Elasticsearch with a detailed mapping structure.

### Backend Query Processing:
The `queryScript.py` Flask server translates natural language queries into Elasticsearch DSL using OpenAI’s API and executes the query.

### Frontend User Interface:
The React frontend provides a user-friendly interface for inputting natural language queries and displaying results in an organized manner.

---

## Example Prompts
Here are some example prompts you can try:

- "Find all graduate-level courses in the Computer Science department with at least 3 credits."
- "List all courses available on the Tempe campus for term 2247."
- "Show courses in the Computer Science and Engineering department with 5 seats available."

---

## Project Structure
- **`insertionScript.py`**: Fetches data from the ASU catalog API and indexes it into Elasticsearch.
- **`queryScript.py`**: Backend server for processing natural language queries and querying Elasticsearch.
- **`frontend/`**: Contains React.js files for the user interface.
  - **`index.js`**: Entry point for the React application.
  - **`QueryForm.jsx`**: Component for the search form.
  - **`QueryForm.css`**: Styling for the search form and results display.
  - **`index.css`**: Global styles for the application.
- **`prompts.txt`**: Sample prompts for testing the application.

---

## Contributing
Contributions are welcome! Feel free to fork this repository and submit pull requests. For major changes, please open an issue to discuss your ideas.

