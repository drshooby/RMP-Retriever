from gql import Client
from gql.transport.aiohttp import AIOHTTPTransport
from constants import *

class RMPWrapper:

    def __init__(self, endpoint_url=ENDPOINT, auth_header=AUTH):
        self.transport = AIOHTTPTransport(
            url=endpoint_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": auth_header,
            }
        )
        self.client = Client(
            transport=self.transport,
            fetch_schema_from_transport=True
        )

    def execute_query(self, query, variables):
        try:
            return self.client.execute(query, variable_values=variables)
        except Exception as e:
            return None

def build_school_link(legacy_id):
    return f"https://www.ratemyprofessors.com/school/{legacy_id}"

def build_rating_link(legacy_id):
    return f"https://www.ratemyprofessors.com/professor/{legacy_id}"

def build_school_search_query(school_name):
    return {"query": {"text": school_name}}

def build_teacher_search_query(prof_name, school_id, count=10):
    return {"query": {"text": prof_name, "schoolID": school_id}, "count": count}

def build_rating_query(prof_id):
    return {"id": prof_id}
