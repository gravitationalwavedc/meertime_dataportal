import database
import logging


GET_OBSERVATIONS_ID_QUERY = """
SELECT id
FROM dataportal_observations
WHERE target_id = %d and utc_start = '%s' and obs_type = '%s' and telescope_id = %d and instrument_config_id = %d
LIMIT 1
"""

GET_OBSERVATIONS_QUERY = """
SELECT target_id, utc_start, duration, obs_type, telescope_id, instrument_config_id, suspect, comment
FROM dataportal_observations
WHERE id = %d
LIMIT 1
"""

INSERT_OBSERVATIONS_QUERY = """
INSERT INTO dataportal_observations (target_id, utc_start, duration, obs_type, telescope_id, instrument_config_id, suspect, comment)
VALUES (%d, '%s', %f, '%s', %d, %d, %s, '%s')
"""


class Observations:
    def __init__(self, db):
        self.db = db

    def get_id(
        self,
        target_id,
        utc_start,
        duration,
        obs_type,
        telescope_id,
        instrument_config_id,
        suspect="FALSE",
        comment=None,
        create=False,
    ):
        query = GET_OBSERVATIONS_ID_QUERY % (target_id, utc_start, obs_type, telescope_id, instrument_config_id)
        try:
            output = self.db.get_singular_value(query, "id")
        except Exception as error:
            logging.error(str(error))
            raise error
        if create and output is None:
            output = self.new(
                target_id, utc_start, duration, obs_type, telescope_id, instrument_config_id, suspect, comment
            )
        return output

    def get_config(self, id):
        """get the instrument config dict for specified id"""
        query = GET_OBSERVATIONS_QUERY % (id)
        try:
            self.db.execute_query(query)
            return self.db.get_singular_value(query, "id")
        except Exception as error:
            logging.error(str(error))
            raise error
        output = self.db.get_output()
        if output is None:
            return None
        return database.util.singular_dict(output)

    def new(self, target_id, utc_start, duration, obs_type, telescope_id, instrument_config_id, suspect, comment):
        """insert a new record"""
        query = INSERT_OBSERVATIONS_QUERY % (
            target_id,
            utc_start,
            duration,
            obs_type,
            telescope_id,
            instrument_config_id,
            suspect,
            comment,
        )
        try:
            self.db.execute_insert(query)
        except Exception as error:
            logging.error(str(error))
            raise error
        return self.db.get_last_insert_id()
