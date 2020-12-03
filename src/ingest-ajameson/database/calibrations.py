import logging
import database

GET_CALIBRATIONS_ID_QUERY = """
SELECT dataportal_calibrations.id
FROM dataportal_calibrations
WHERE calibration_type = '%s' and location ='%s'
LIMIT 1
"""

GET_CALIBRATIONS_CONFIG_QUERY = """
SELECT calibration_type, location
FROM dataportal_calibrations
WHERE id = %d
LIMIT 1
"""

INSERT_CALIBRATIONS_NAME_QUERY = """
INSERT INTO dataportal_calibrations (calibration_type, location)
VALUES ('%s', '%s');
"""


class Calibrations:
    def __init__(self, db):
        self.db = db
        self.cal_dir = "/fred/oz005/users/aparthas/reprocessing_MK/poln_calibration/"
        self.pre_calibration_start_date = "2020-04-04-00:00:00"

    def get_id(self, utc_start, create=False):
        """get the calibration_id for the utc_start"""

        # any observation after this date is pre-calibrated
        if False and utc_start > self.pre_calibration_start_date:
            calibration_type = "pre"
            location = None
        # we must find the closest calibration match
        else:
            # TODO actually check the files with time matching rule
            calibration_type = "post"
            location = "2020-02-17-01:22:25.jones"
        output = self._get_id(calibration_type, location)
        if create and output is None:
            output = self.new(calibration_type, location)
        return output

    def _get_id(self, calibration_type, location):
        """get the id for the calibration from the type and location"""
        query = GET_CALIBRATIONS_ID_QUERY % (calibration_type, location)
        try:
            return self.db.get_singular_value(query, "id")
        except Exception as error:
            logging.error(str(error))
            raise error

    def get_config(self, id):
        """get the calibration dict fro the id"""
        query = GET_CALIBRATIONS_CONFIG_QUERY % (id)
        try:
            self.db.execute_query(query)
        except Exception as error:
            logging.error(str(error))
            raise error
        output = self.db.get_output()
        if output is None:
            return None
        return database.util.singular_dict(output)

    def new(self, calibration_type, location):
        """create a new calibration """
        query = INSERT_CALIBRATIONS_NAME_QUERY % (calibration_type, location)
        try:
            self.db.execute_insert(query)
        except Exception as error:
            logging.error(str(error))
            raise error
        return self.db.get_last_insert_id()
