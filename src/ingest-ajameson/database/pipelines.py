import database
import getpass
import logging

from util import time

GET_PIPELINE_ID_QUERY = """
SELECT id
FROM Pipelines
WHERE name = '%s' AND revision = '%s' AND JSON_CONTAINS(configuration, '%s')
LIMIT 1
"""

GET_PIPELINE_QUERY = """
SELECT name, revision, configuration
FROM Pipelines
WHERE id = %d
LIMIT 1
"""

INSERT_PIPELINE_QUERY = """
INSERT INTO Pipelines (name, description, revision, created_at, created_by, configuration)
VALUES ('%s','%s','%s', '%s', '%s', '%s');
"""


class Pipelines:
    def __init__(self, db):
        self.db = db

    def get_id(self, name, revision, configuration, create=False):
        """get the id for the pipeline from the key parameters"""
        query = GET_PIPELINE_ID_QUERY % (name, revision, configuration)
        try:
            output = self.db.get_singular_value(query, "id")
        except Exception as error:
            logging.error(str(error))
            raise error
        if create and output is None:
            output = self.new(name, revision, configuration)
        return output

    def get_config(self, pipeline_id):
        """get the configuration for the pipeline from the id"""
        query = GET_PIPELINE_QUERY % (pipeline_id)
        try:
            output = self.db.execute_query(query)
        except Exception as error:
            logging.error(str(error))
            raise error
        output = self.db.get_output()
        if output is None:
            return None
        return database.util.singular_dict(output)

    def new(self, name, revision, configuration):
        """create a new pipeline from the supplied parameters"""
        description = "None"
        created_at = time.get_current_time()
        created_by = getpass.getuser()
        return self._new(name, description, revision, created_at, created_by, configuration)

    def _new(self, name, description, revision, created_at, created_by, configuration):
        query = INSERT_PIPELINE_QUERY % (name, description, revision, created_at, created_by, configuration)
        try:
            self.db.execute_insert(query)
        except Exception as error:
            logging.error(str(error))
            raise error
        return self.db.get_last_insert_id()
