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
    <h1>Welcome! Here you can find your options:</h1>
    <h2>1. /school</h2>
    <p>Endpoint to search for schools.</p>
    <p><strong>Requires the query parameter 'name' (e.g., <em>/school?name=Harvard</em>)</strong></p>
    <p>This endpoint returns details about schools, including a URL.</p>

    <h2>2. /professor</h2>
    <p>Endpoint to search for professors.</p>
    <p><strong>Requires the query parameters 'name' and 'id' (e.g., <em>/professor?name=John&id=U2Xvasd9sLbg4MA==</em>)</strong></p>
    <p>This endpoint returns details about professors.</p>
    <p><strong>Use /school to help you find the 'id' field for this endpoint.</strong></p>

    <h2>3. /ratings</h2>
    <p>Endpoint to search for professor ratings.</p>
    <p><strong>Requires the query parameter 'id' (e.g., <em>/ratings?id=n32lkanSD9==</em>)</strong></p>
    <p>This endpoint returns details about the professor's ratings, including a URL.</p>
    <p><strong>Use /professor to help you find the 'id' field for this endpoint.</strong></p>
    
    <br>
    <h2><strong>Please be considerate of Rate My Professors' API!</strong> This is supposed to be a fun little side project.</h2>
    <p>Wanna leave feedback? Visit the repo: <a href="https://github.com/drshooby/RMP-Retriever">GitHub link</a>.</p>
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
def search_professor():
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