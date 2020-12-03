import logging
import database


GET_PROCESSINGS_ID_QUERY = """
SELECT id
FROM dataportal_processings
WHERE observation_id = %d AND pipeline_id = %d AND location = '%s' AND JSON_CONTAINS(results, '%s')
LIMIT 1
"""

GET_PROCESSINGS_QUERY = """
SELECT observation_id, pipeline_id, parent_id, embargo_end, location, job_state, job_output, results
FROM dataportal_processings
WHERE id = %d
LIMIT 1
"""

INSERT_PROCESSINGS_ORPHAN_QUERY = """
INSERT INTO dataportal_processings (observation_id, pipeline_id, embargo_end, location, job_state, job_output, results)
VALUES (%d, %d, '%s', '%s', '%s', '%s', '%s')
"""

INSERT_PROCESSINGS_QUERY = """
INSERT INTO dataportal_processings (observation_id, pipeline_id, parent_id, embargo_end, location, job_state, job_output, results)
VALUES (%d, %d, %d, '%s', '%s', '%s', '%s', '%s')
"""


class Processings:
    def __init__(self, db):
        self.db = db

    def get_id(self, observation_id, pipeline_id, parent_id, embargo_end, location, results, create=False):
        """get the id for the specified instrument config"""
        query = GET_PROCESSINGS_ID_QUERY % (observation_id, pipeline_id, location, results)
        try:
            output = self.db.get_singular_value(query, "id")
        except Exception as error:
            logging.error(str(error))
            raise error
        if create and output is None:
            job_state = "None"
            job_output = "{}"
            output = self.new(
                observation_id, pipeline_id, parent_id, embargo_end, location, job_state, job_output, results
            )
        return output

    def get_config(self, id):
        """get the instrument config dict for specified id"""
        query = GET_PROCESSINGS_QUERY % (id)
        try:
            self.db.execute_query(query)
            return self.db.get_singular_value(query, "id")
        except Exception as error:
            logging.error(str(error))
            raise error
        output = self.db.get_output()
        return database.util.singular_dict(output)

    def new(self, observation_id, pipeline_id, parent_id, embargo_end, location, job_state, job_output, results):
        if parent_id is None:
            query = INSERT_PROCESSINGS_ORPHAN_QUERY % (
                observation_id,
                pipeline_id,
                embargo_end,
                location,
                job_state,
                job_output,
                results,
            )
        else:
            query = INSERT_PROCESSINGS_QUERY % (
                observation_id,
                pipeline_id,
                parent_id,
                embargo_end,
                location,
                job_state,
                job_output,
                results,
            )
        try:
            self.db.execute_insert(query)
        except Exception as error:
            logging.error(str(error))
            raise error
        return self.db.get_last_insert_id()
