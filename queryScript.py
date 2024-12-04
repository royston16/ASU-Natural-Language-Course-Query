from flask import Flask, request, jsonify
import os
import openai
import urllib3
from flask_cors import CORS
from elasticsearch import Elasticsearch
from config import key


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Flask app setup
app = Flask(__name__)
CORS(app)  # Enable CORS

# OpenAI API Key
openai.api_key = key

# Elasticsearch Client
es = Elasticsearch('https://localhost:9200', basic_auth=('elastic', 'qWcAXAuUr=lhx78_pAGw'), verify_certs=False)



def generate_elasticsearch_query(user_query):
    """
    Use ChatGPT to generate an Elasticsearch DSL query based on the user query.
    """
    prompt = f"""
    You are an assistant that converts natural language course queries into Elasticsearch DSL queries.

    **Indexed Fields and Their Details:**

    The data is indexed in Elasticsearch with the following structure:

    - **catalog_number** (`keyword`): Unique identifier for the course. *Example*: "CSE507".
    - **course_name** (`text`): Full name of the course. *Example*: "Image Processing and Analysis".
    - **description** (`text`): Detailed description of the course.
    - **department** (`text`): Department offering the course. *Example*: "Computer Science and Engineering".
    - **subject** (`keyword`): Subject code. *Example*: "CSE".
    - **course_level** (`keyword`): Level of the course. Possible values: "graduate", "undergraduate".
    - **credits_min**, **credits_max** (`integer`): Minimum and maximum credit hours. *Example*: 3.
    - **instructors** (`text`): List of instructors' names. *Example*: ["Jianming Liang"].
    - **schedule_days** (`keyword`): Days when the course is scheduled. Possible values: "M", "T", "W", "Th", "F".
    - **start_time**, **end_time** (`keyword`): Class start and end times in 12-hour format. *Example*: "12:00 PM".
    - **start_date**, **end_date** (`date`): Course start and end dates. *Format*: "YYYY-MM-DD".
    - **availability** (`nested` object):
        - **term** (`keyword`): Academic term. *Example*: "2247".
        - **enrolled** (`integer`): Number of students enrolled.
        - **capacity** (`integer`): Total capacity.
        - **available** (`integer`): Seats available (capacity - enrolled).
    - **campus** (`keyword`): Campus code. *Example*: "TEMPE".
    - **academic_group** (`text`): College or school offering the course. *Example*: "Ira A. Fulton Engineering".
    - **instruction_mode** (`keyword`): Instruction mode. Possible values: "P" (in-person), "O" (online), etc.
    - **facility** (`text`): Building or room where the course is held.
    - **prerequisites** (`text`): Course prerequisites.
    - **grading_basis** (`text`): Grading scheme of the course.
    - **class_status** (`keyword`): Status of the class. Possible values: "A" (active), etc.
    - **component** (`keyword`): Component of the course. *Example*: "LEC" (lecture), "LAB" (laboratory).

    - **Nested Fields:**
    - **availability** (`nested` object): Contains information about course availability. Each entry includes:
    - **term** (`keyword`): The academic term. If it is Fall 2024, map it to 2247. If it is Spring 2023, map it to 2241. 
    - **enrolled** (`integer`): The number of students enrolled.
    - **capacity** (`integer`): The total capacity for the course.
    - **available** (`integer`): The number of available seats (capacity - enrolled).

    **Important Notes:**
    1. Use `nested` queries for fields inside the `availability` object.
    2. Combine multiple conditions using `bool` queries with `must`, `filter`, `should`, or `must_not` clauses as appropriate.
    3. Only use valid fields based on the index mapping.
    4. Always ensure the generated query is in valid JSON format.
    5. Make sure you do not add '''json or any other mistakes in the generated query.

    **Instructions:**

    - Use field names exactly as listed in the index mapping.
    - Follow the exact same structure specified in the index mapping to construct queries. 
    - Construct valid Elasticsearch queries always.
    - Always ensure referenced fields exist in the index.
    - Analyze the user's query and extract relevant parameters.
    - Construct an Elasticsearch query in JSON format.
    - Do not include aggs or subject.keyword in the query. 
    - Use the appropriate query types (`term`, `match`, `range`, `bool`, etc.).
    - Use `must`, `filter`, `should`, and `must_not` clauses appropriately.
    - Ensure field names match exactly as listed.
    - Do not include fields that are not indexed.
    - Output only the Elasticsearch query in JSON format, without any explanations.
    - Make sure you do not add '''json or any other mistakes in the generated query.
    
    **Example Queries:**
    - "Find all graduate-level courses in the Computer Science department with at least 3 credits."
    - "List all courses available on the Tempe campus in term 2247."

    **User Query:**

    "{user_query}"

    **Elasticsearch Query:**
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use gpt-4 or gpt-3.5-turbo
            messages=[
                {"role": "system", "content": "You are a helpful assistant for building Elasticsearch queries."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.0
        )
        es_query = response['choices'][0]['message']['content'].strip()
        print("Generated Query:", es_query)  
        return es_query
    except Exception as e:
        return {"error": f"OpenAI API error: {str(e)}"}

def query_elasticsearch(es_query):
    """
    Execute the Elasticsearch query and include detailed course information.
    """
    try:
        response = es.search(index="course_index", body=es_query)
        courses = []
        for hit in response["hits"]["hits"]:
            course = hit["_source"]
            courses.append({
                "catalog_number": course["catalog_number"],
                "course_name": course["course_name"],
                "description": course["description"],
                "department": course["department"],
                "course_level": course["course_level"],
                "credits": f"{course.get('credits_min', '')}-{course.get('credits_max', '')}",
                "schedule_days": course.get("schedule_days", ""),
                "start_time": course.get("start_time", ""),
                "end_time": course.get("end_time", ""),
                "availability": course.get("availability", []),
                "prerequisites": course.get("prerequisites", "None"),
                "grading_basis": course.get("grading_basis", "Standard"),
                "facility": course.get("facility", "Not specified"),
                "academic_group": course.get("academic_group", "Not specified"),
                "term": course.get("availability", [{}])[0].get("term", "N/A")
            })
        return courses
    except Exception as e:
        return {"error": str(e)}

@app.route("/nlp-query", methods=["POST"])
def nlp_query():
    """
    Flask route to handle natural language queries.
    """
    try:
        user_query = request.json.get("query", "")
        if not user_query:
            return jsonify({"error": "No query provided"}), 400

        # Step 1: Generate Elasticsearch query using OpenAI
        es_query = generate_elasticsearch_query(user_query)

        if "error" in es_query:
            return jsonify(es_query), 500

        # Validate that the generated query is valid JSON
        try:
            import json
            es_query_json = json.loads(es_query)
        except json.JSONDecodeError as e:
            return jsonify({"error": f"Invalid Elasticsearch query generated: {str(e)}"}), 500

        # Step 2: Query Elasticsearch
        es_results = query_elasticsearch(es_query_json)

        if isinstance(es_results, dict) and "error" in es_results:
            return jsonify(es_results), 500

        # Step 3: Return the results
        return jsonify({"courses": es_results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)
