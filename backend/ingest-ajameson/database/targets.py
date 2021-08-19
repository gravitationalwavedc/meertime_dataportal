import logging


GET_TARGET_ID_QUERY = """
SELECT dataportal_targets.id
FROM dataportal_targets
WHERE name = '%s'
LIMIT 1
"""

GET_TARGET_NAME_QUERY = """
SELECT dataportal_targets.name
FROM dataportal_targets
WHERE id = %d
LIMIT 1
"""

INSERT_TARGET_NAME_QUERY = """
INSERT INTO dataportal_targets (name, raj, decj)
VALUES ('%s','%s','%s');
"""


class Targets:
    def __init__(self, db):
        self.db = db

    def get_id(self, hdr, create=False):
        """get the id for the target from the hdr"""
        output = self._get_id(hdr.source)
        if create and output is None:
            output = self.new(hdr)
        return output

    def _get_id(self, name):
        """get the id for the target from the name"""
        query = GET_TARGET_ID_QUERY % (name)
        try:
            return self.db.get_singular_value(query, "id")
        except Exception as error:
            logging.error(str(error))
            raise error

    def get_name(self, id):
        """get the name for the target from the id"""
        query = GET_TARGET_NAME_QUERY % (id)
        try:
            return self.db.get_singular_value(query, "id")
        except Exception as error:
            logging.error(str(error))
            raise error

    def new(self, hdr):
        """create a new target from the hdr"""
        return self._new(hdr.source, hdr.tied_beam_ra, hdr.tied_beam_dec)

    def _new(self, name, ra, dec):
        query = INSERT_TARGET_NAME_QUERY % (name, ra, dec)
        try:
            self.db.execute_insert(query)
        except Exception as error:
            logging.error(str(error))
            raise error
        return self.db.get_last_insert_id()
