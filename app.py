from flask import Flask, request, jsonify
from flask_cors import CORS
from rmp_wrapper import *
from queries import *

app = Flask(__name__)
CORS(app)

rmp = RMPWrapper()

@app.route("/")
def helper():
    return """
    Welcome! Here you can find your options:
    
    1. /school
       - Endpoint to search for schools.
       - Requires the query parameter 'name' (e.g., /school?name=Harvard).
       - This endpoint returns details about schools, including a URL.

    2. /professor
       - Endpoint to search for professors.
       - Requires the query parameters 'name' and 'id' (e.g., /professor?name=John&id=U2Xvasd9sLbg4MA==).
       - This endpoint returns details about professors.
       - Use /school to help you find the id field for this endpoint.

    3. /ratings
       - Endpoint to search for professor ratings.
       - Requires the query parameter 'id' (e.g., /ratings?id=n32lkanSD9==).
       - This endpoint returns details about the professor's ratings, including a URL.
       - Use /professor to help you find the id field for this endpoint.
    
    For more details, please make sure to include the required query parameters for each endpoint.
    """

@app.get("/school")
def search_school():
    school_name = request.args.get("name")
    if not school_name:
        return jsonify({"error": "Missing required query parameter: 'name'"}), 400

    variables = build_school_search_query(school_name)
    rsp = rmp.execute_query(SCHOOL_SEARCH_QUERY, variables)
    if not rsp:
        return jsonify({"error": f"Query was unsuccessful for school name: {school_name}"}), 400

    for edge in rsp["newSearch"]["schools"]["edges"]:
        node_dict = edge["node"]
        node_dict["url"] = build_school_link(node_dict["legacyId"])

    return jsonify(rsp), 200

@app.get("/professor")
def search_prof():
    prof_name = request.args.get("name")
    school_id = request.args.get("id")
    if not prof_name or not school_id:
        return jsonify({"error": "Missing required query parameters: 'name' or 'id'"}), 400

    variables = build_teacher_search_query(prof_name, school_id)
    rsp = rmp.execute_query(PROF_SEARCH_QUERY, variables)
    if not rsp:
        return jsonify({"error": f"Query was unsuccessful for professor name: {prof_name} and school id: {school_id}"}), 400

    return jsonify(rsp), 200

@app.get("/ratings")
def search_ratings():
    prof_id = request.args.get("id")
    if not prof_id:
        return jsonify({"error": "Missing required query parameter: 'id'"}), 400

    variables = build_rating_query(prof_id)
    rsp = rmp.execute_query(RATINGS_SEARCH_QUERY, variables)
    if not rsp:
        return jsonify({"error": f"Query was unsuccessful for professor id: {prof_id}"}), 400

    rsp["node"]["url"] = build_rating_link(rsp["node"]["legacyId"])

    return jsonify(rsp), 200