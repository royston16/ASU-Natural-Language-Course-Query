import requests
from elasticsearch import Elasticsearch
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Elasticsearch setup
es = Elasticsearch('https://localhost:9200', basic_auth=('elastic', 'qWcAXAuUr=lhx78_pAGw'), verify_certs=False)

# API configuration
PRIMARY_API_URL = "https://eadvs-cscc-catalog-api.apps.asu.edu/catalog-microservices/api/v1/search/classes"
SECONDARY_API_URL = "https://eadvs-cscc-catalog-api.apps.asu.edu/catalog-microservices/api/v1/search/courses"

HEADERS = {
    "Authorization": "Bearer null", 
    "Accept": "application/json",
}

PRIMARY_PARAMS = {
    "refine": "Y",
    "campusOrOnlineSelection": "A",
    "honors": "F",
    "campus": "TEMPE",
    "promod": "F",
    "level": "grad",
    "searchType": "all",
    # "subject": "CSE",
    "term": "2247",  
}

# Create Elasticsearch index with detailed mapping
def create_index():
    mapping = {
        "mappings": {
            "properties": {
                "catalog_number": {"type": "keyword"},
                "course_name": {"type": "text"},
                "description": {"type": "text"},
                "department": {"type": "text"},
                "subject": {"type": "keyword"},
                "course_level": {"type": "keyword"},
                "credits_min": {"type": "integer"},
                "credits_max": {"type": "integer"},
                "instructors": {"type": "text"},
                "schedule_days": {"type": "keyword"},
                "start_time": {"type": "keyword"},
                "end_time": {"type": "keyword"},
                "start_date": {"type": "date"},
                "end_date": {"type": "date"},
                "availability": {
                    "type": "nested",
                    "properties": {
                        "term": {"type": "keyword"},
                        "enrolled": {"type": "integer"},
                        "capacity": {"type": "integer"},
                        "available": {"type": "integer"}
                    }
                },
                "campus": {"type": "keyword"},
                "academic_group": {"type": "text"},
                "instruction_mode": {"type": "keyword"},
                "facility": {"type": "text"},
                "prerequisites": {"type": "text"},
                "grading_basis": {"type": "text"},
                "class_status": {"type": "keyword"},
                "component": {"type": "keyword"}
            }
        }
    }
    es.indices.create(index="course_index", body=mapping, ignore=400)

# Fetch metadata for each course from the secondary API
def fetch_course_metadata(catalog_nbr, course_id, subject, term):
    params = {
        "refine": "Y",
        "catalogNbr": catalog_nbr,
        "course_id": course_id,
        "subject": subject,
        "term": term
    }
    response = requests.get(SECONDARY_API_URL, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching metadata for catalog number {catalog_nbr}. Status code: {response.status_code}")
        return None

# Process and index data into Elasticsearch
def index_course_data(primary_data):
    for course in primary_data.get("classes", []):
        catalog_nbr = course.get("CLAS", {}).get("CATALOGNBR")
        course_id = course.get("CLAS", {}).get("CRSEID")
        term = course.get("CLAS", {}).get("STRM")
        subject = course.get("CLAS", {}).get("SUBJECT")
        campus = course.get("CLAS", {}).get("CAMPUS", "")
        schedule_days = course.get("CLAS", {}).get("DAYLIST", "")
        start_time = course.get("CLAS", {}).get("STARTTIME", "")
        end_time = course.get("CLAS", {}).get("ENDTIME", "")
        start_date = course.get("CLAS", {}).get("STARTDATE", "")
        end_date = course.get("CLAS", {}).get("ENDDATE", "")
        credits_min = int(course.get("CLAS", {}).get("UNITSMINIMUM", 0))
        credits_max = int(course.get("CLAS", {}).get("UNITSMAXIMUM", 0))
        level = "graduate" if catalog_nbr.startswith(("4", "5")) else "undergraduate"

        # Create a unique document ID using catalog number and term
        doc_id = f"{catalog_nbr}_{term}"

        # Fetch additional metadata
        metadata = fetch_course_metadata(catalog_nbr, course_id, subject, term)
        if not metadata or not metadata[0]:
            continue

        # Prepare document for Elasticsearch
        doc = {
            "catalog_number": catalog_nbr,
            "course_name": metadata[0].get("COURSETITLELONG", ""),
            "description": metadata[0].get("DESCRLONG", ""),
            "department": metadata[0].get("SUBJECTDESCR", ""),
            "subject": subject,
            "course_level": level,
            "credits_min": credits_min,
            "credits_max": credits_max,
            "instructors": course.get("CLAS", {}).get("INSTRUCTORSLIST", []),
            "schedule_days": schedule_days,
            "start_time": start_time,
            "end_time": end_time,
            "start_date": start_date,
            "end_date": end_date,
            "availability": [
                {
                    "term": term,
                    "enrolled": course.get("seatInfo", {}).get("ENRL_TOT", 0),
                    "capacity": course.get("seatInfo", {}).get("ENRL_CAP", 0),
                    "available": course.get("seatInfo", {}).get("ENRL_CAP", 0) - course.get("seatInfo", {}).get("ENRL_TOT", 0)
                }
            ],
            "campus": campus,
            "academic_group": metadata[0]["COLLEGEMAP"][0]["INFO"].get("DESCRFORMAL", ""),
            "instruction_mode": course.get("CLAS", {}).get("INSTRUCTIONMODE", ""),
            "facility": course.get("CLAS", {}).get("FACILITYID", ""),
            "prerequisites": metadata[0]["COLLEGEMAP"][0]["INFO"].get("ENROLLREQ", ""),
            "grading_basis": metadata[0].get("GRADINGBASISDESCR", ""),
            "class_status": course.get("CLAS", {}).get("CLASSSTAT", ""),
            "component": course.get("CLAS", {}).get("COMPONENTPRIMARY", "")
        }

        # Index document into Elasticsearch
        es.index(index="course_index",id=doc_id, body=doc)
        print(f"Indexed course {catalog_nbr}: {metadata[0].get('COURSETITLELONG', '')}")

# Main function to execute the script
def main():
    # Step 1: Create Elasticsearch index
    create_index()

    # Step 2: Fetch primary course data
    response = requests.get(PRIMARY_API_URL, headers=HEADERS, params=PRIMARY_PARAMS)
    if response.status_code == 200:
        primary_data = response.json()
        # Step 3: Process and index data
        index_course_data(primary_data)
    else:
        print(f"Failed to fetch primary course data. Status code: {response.status_code}")

# Run the script
if __name__ == "__main__":
    main()
