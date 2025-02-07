from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from rmp_wrapper import *
from queries import *
from werkzeug.exceptions import TooManyRequests

app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app)

CORS(app)

rmp = RMPWrapper()

@app.route("/")
@limiter.exempt
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

    <p><strong>For more details, please make sure to include the required query parameters for each endpoint.</strong></p>
    """

@app.get("/school")
@limiter.limit("5 per minute")
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
@limiter.limit("5 per minute")
def search_professor():
    prof_name = request.args.get("name")
    school_id = request.args.get("id")
    if not prof_name or not school_id:
        return jsonify({"error": "Missing required query parameters: 'name' or 'id'"}), 400

    variables = build_teacher_search_query(prof_name, school_id)
    rsp = rmp.execute_query(PROF_SEARCH_QUERY, variables)
    if not rsp:
        return jsonify({"error": f"Query was unsuccessful for professor name: {prof_name} and school id: {school_id}"}), 400

    for edge in rsp["newSearch"]["schools"]["edges"]:
        node_dict = edge["node"]
        node_dict["url"] = build_rating_link(node_dict["legacyId"])

    return jsonify(rsp), 200

@app.get("/ratings")
@limiter.limit("5 per minute")
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

@app.errorhandler(TooManyRequests)
def handle_rate_limit_error(error):
    return jsonify({"error": "Let's be considerate of RMP's servers. Please try again in a minute."}), 429