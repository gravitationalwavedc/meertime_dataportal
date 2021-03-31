import json
import logging
import requests as r
from base64 import b64decode, b64encode
import binascii
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
        self.create_variables = {}
        self.update_mutation = None
        self.update_variables = {}
        self.list_query = None
        self.list_variables = None

        self.cli_name = None
        self.cli_description = None

        # record name is the singular form of the record
        records = self.__class__.__name__.lower()

        if records.endswith("ides"):
            self.record_name = records.rstrip("ides") + "is"
        elif records.endswith("es"):
            self.record_name = records.rstrip("es")
        elif records.endswith("s"):
            self.record_name = records.rstrip("s")
        else:
            raise RuntimeError("Could not determine singular form of record from " + records)

        self.human_readable = True
        self.literal_field_names = []
        self.field_names = []

    def set_literal(self, literal):
        if literal:
            if len(self.literal_field_names) > 0:
                self.field_names = self.literal_field_names
        self.human_readable = not literal

    def encode_table_id(self, table, id):
        unencoded = f"{table}Node:{id}"
        return b64encode(unencoded.encode("ascii")).decode("utf-8")

    def encode_id(self, id):
        return self.encode_table_id(self.__class__.__name__, id)

    def decode_id(self, encoded):
        decoded = b64decode(encoded).decode("ascii")
        return decoded.split(":")[1]

    def create_graphql(self,):

        logging.debug(f"Using mutation {self.create_mutation}")
        logging.debug(f"Using mutation vars in a dict {self.create_variables}")

        payload = {"query": self.create_mutation, "variables": json.dumps(self.create_variables)}
        response = self.client.post(self.url, payload, **self.header)
        if response.status_code == 200:
            content = json.loads(response.content)
            if not "errors" in content.keys():
                for key in content["data"].keys():
                    record_set = content["data"][key]
                    if self.record_name in record_set.keys():
                        print(record_set[self.record_name]["id"])
                    else:
                        logging.warning(f"Record {self.record_name} did not exist in returned json")
            else:
                logging.warning(f"Errors returned in content {content['errors']}")
        else:
            logging.warning(f"Bad response status_code={response.status_code}")
        return response

    def update_graphql(self, delim="\t"):

        logging.debug(f"Using mutation {self.update_mutation}")
        logging.debug(f"Using mutation vars dict {self.update_variables}")

        payload = {"query": self.update_mutation, "variables": json.dumps(self.update_variables)}
        response = self.client.post(self.url, payload, **self.header)
        if response.status_code == 200:
            content = json.loads(response.content)
            if not "errors" in content.keys():
                for key in content["data"].keys():
                    record_set = content["data"][key]
                    if "edges" in record_set.keys():
                        record_set = record_set["edges"]
                    if self.record_name in record_set.keys():
                        self.print_record_set(record_set[self.record_name], delim)
                    else:
                        logging.warning(f"Record {self.record_name} did not exist in returned json")
        return response

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
                    if type(record_set) == dict:
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

    def build_list_join_id_query(self, join, field, id):
        table = self.__class__.__name__
        query_name = f"all{table.title()}"
        id_encoded = b64encode(f"{join.title()}Node:{id}".encode("ascii")).decode("utf-8")
        template = """
        query %s {
            %s (%s: \"%s\") {
                edges {
                    node {
                        %s
                    }
                }
            }
        }
        """
        delim = ",\n                        "
        query = template % (query_name, query_name, field, id_encoded, delim.join(self.field_names))
        return query

    def print_record_set_fields(self, record_set, delim):
        if "node" in record_set.keys():
            record_set = record_set["node"]
        print(delim.join(record_set.keys()))

    def get_record_set_value(self, key, value):
        if key == "id":
            try:
                result = self.decode_id(value)
            except binascii.Error:
                result = value
        elif type(value) is dict:
            k = list(value.keys())[0]
            v = list(value.values())[0]
            result = self.get_record_set_value(k, v)
        else:
            result = value
        return result

    def print_record_set_values(self, record_set, delim):
        if "node" in record_set.keys():
            record_set = record_set["node"]
        for key in record_set.keys():
            record_set[key] = self.get_record_set_value(key, record_set[key])
        print(delim.join([str(value) for value in record_set.values()]))

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
