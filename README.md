# ASU CourseFinder - A Natural Language Course Query Application

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
   npm install
   ```

4. Insert your OpenAI API key into a config file called `config.py`
    
5. Start Elasticsearch: Ensure Elasticsearch is running and accessible at the host and port specified in your scripts.

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
npm start
```

---

## Example Prompts
Here are some example prompts you can try:

- "Find all graduate-level courses in the Computer Science department with at least 3 credits."
- "List all courses available on the Tempe campus for term 2247."
- "Show courses in the Computer Science and Engineering department with 5 seats available."

---


