import json
import logging
import requests as r
from base64 import b64decode, b64encode
from requests.packages.urllib3.util.retry import Retry
from graphql_client import GraphQLClient

log = logging.getLogger(__name__)


class GraphQLTable:
    """Abstract base class to perform create, update and select GraphQL queries"""

    def __init__(self, client, url, token):

        # the graphQL client may also be a djangodb mock endpoint
        self.client = client
        self.url = url
        self.token = token
        if type(self.client) == GraphQLClient:
            self.header = {"Authorization": f"JWT {token}"}
        else:
            self.header = {"HTTP_AUTHORIZATION": f"JWT {token}"}

        self.create_mutation = None
        self.create_variables = None
        self.update_mutation = None
        self.update_variables = None
        self.list_query = None
        self.list_variables = None

        self.cli_name = None
        self.cli_description = None

    def encode_id(self, id):
        unencoded = f"{self.__class__.__name__ }Node:{id}"
        return b64encode(unencoded.encode("ascii")).decode("utf-8")

    def decode_id(self, encoded):
        decoded = b64decode(encoded).decode("ascii")
        return decoded.split(":")[1]

    def create_graphql(self, vars_values):

        logging.debug(f"Using mutation {self.create_mutation}")
        logging.debug(f"Using mutation vars {self.create_variables}")
        logging.debug(f"Using with values {vars_values}")

        payload = {"query": self.create_mutation, "variables": self.create_variables % vars_values}
        return self.client.post(self.url, payload, **self.header)

    def update_graphql(self, vars_values):

        logging.debug(f"Using mutation {self.update_mutation}")
        logging.debug(f"Using mutation vars {self.update_variables}")
        logging.debug(f"Using with values {vars_values}")

        payload = {"query": self.update_mutation, "variables": self.update_variables % vars_values}
        return self.client.post(self.url, payload, **self.header)

    def list_graphql(self, vars_values, delim="\t"):

        logging.debug(f"Using query {self.list_query}")
        logging.debug(f"Using query vars {self.list_variables}")
        logging.debug(f"Using with values {vars_values}")

        payload = {"query": self.list_query, "variables": self.list_variables % vars_values}
        response = self.client.post(self.url, payload, **self.header)
        if response.status_code == 200:
            content = json.loads(response.content)
            if not "errors" in content.keys():
                for key in content["data"].keys():
                    record_set = content["data"][key]
                    if "edges" in record_set.keys():
                        record_set = record_set["edges"]
                    self.print_record_set(record_set, delim)
        return response

    def build_list_all_query(self):
        table = self.__class__.__name__
        query_name = f"all{table.title()}"
        template = """
        query %s {
            %s {
                edges {
                    node {
                        %s
                    }
                }
            }
        }
        """
        delim = ",\n                        "
        query = template % (query_name, query_name, delim.join(self.field_names))
        return query

    def build_list_id_query(self, singular, id):
        table = self.__class__.__name__
        query_name = f"all{table.title()}"
        id_encoded = b64encode(f"{table.title()}Node:{id}".encode("ascii")).decode("utf-8")
        template = """
        query {
            %s (id: \"%s\") {
                %s
            }
        }
        """
        delim = ",\n                "
        query = template % (singular, id_encoded, delim.join(self.field_names))
        return query

    def build_list_str_query(self, field):
        table = self.__class__.__name__
        query_name = f"all{table.title()}"
        template = """
        query %s ($variable: String!) {
            %s (%s: $variable) {
                edges {
                    node {
                        %s
                    }
                }
            }
        }
        """
        delim = ",\n                        "
        query = template % (query_name, query_name, field, delim.join(self.field_names))
        return query

    def print_record_set_fields(self, record_set, delim):
        if "node" in record_set.keys():
            record_set = record_set["node"]
        print(delim.join(record_set.keys()))

    def print_record_set_values(self, record_set, delim):
        if "node" in record_set.keys():
            record_set = record_set["node"]
        for key in record_set.keys():
            if key == 'id':
                record_set[key] = self.decode_id(record_set[key])
        print(delim.join(record_set.values()))

    def print_record_set(self, record_set, delim):
        num_records = len(record_set)
        if num_records == 0:
            return
        if type(record_set) == list:
            self.print_record_set_fields(record_set[0], delim)
            for record in record_set:
                self.print_record_set_values(record, delim)
        elif type(record_set) == dict:
            self.print_record_set_fields(record_set, delim)
            self.print_record_set_values(record_set, delim)
        else:
            raise RuntimeError("did not understand type of recordset")
