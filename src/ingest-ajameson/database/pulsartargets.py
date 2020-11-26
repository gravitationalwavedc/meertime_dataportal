import logging

GET_PULSAR_TARGET_ID_QUERY = """
SELECT pulsar_id, target_id
FROM dataportal_pulsartargets
WHERE pulsar_id = %d AND target_id = %d
"""

GET_PULSAR_IDS_QUERY = """
SELECT pulsar_id
FROM dataportal_pulsartargets
WHERE target_id = %d
"""

GET_TARGET_IDS_QUERY = """
SELECT target_id
FROM dataportal_pulsartargets
WHERE pulsar_id = %d
"""

INSERT_PULSAR_TARGET_QUERY = """
INSERT INTO dataportal_pulsartargets (pulsar_id, target_id)
VALUES (%d, %d)
"""


class PulsarTargets:
    def __init__(self, db):
        self.db = db

    def get_pulsar_target(self, pulsar_id, target_id, create=False):
        """return true if the pulsar_id, target_id tuple exists"""
        query = GET_PULSAR_TARGET_ID_QUERY % (pulsar_id, target_id)
        try:
            self.db.execute_query(query)
        except Exception as error:
            logging.error(str(error))
            raise error
        output = self.db.get_output()
        if create and output is None:
            self.new(pulsar_id, target_id)
            output = self.db.get_output()
        return output is not None

    def get_pulsars(self, target_id):
        """get the pulsars for the specified target_id"""
        query = GET_PULSAR_IDS_QUERY % (target_id)
        try:
            self.db.execute_query(query)
        except Exception as error:
            logging.error(str(error))
            raise error
        return self.db.get_output()

    def get_targets(self, pulsar_id):
        """get the tagets which match the specifid pulsar_id"""
        query = GET_TARGET_IDS_QUERY % (id)
        try:
            self.db.execute_query(query)
        except Exception as error:
            logging.error(str(error))
            raise error
        return self.db.get_output()

    def new(self, pulsar_id, target_id):
        """create a new pulsartarget"""
        if self.get_pulsar_target(pulsar_id, target_id):
            return
        query = INSERT_PULSAR_TARGET_QUERY % (pulsar_id, target_id)
        try:
            self.db.execute_insert(query)
        except Exception as error:
            logging.error(str(error))
            raise error
