import logging


GET_TELESCOPE_ID_QUERY = """
SELECT Telescopes.id
FROM Telescopes
WHERE name = '%s'
LIMIT 1
"""

GET_TELESCOPE_NAME_QUERY = """
SELECT Telescopes.name
FROM Telescopes
WHERE id = %d
LIMIT 1
"""

INSERT_TELESCOPE_NAME_QUERY = """
INSERT INTO Telescopes (name)
VALUES ('%s');
"""


class Telescopes:
    def __init__(self, db):
        self.db = db

    def get_id(self, hdr, create=False):
        """get the id for the telescope from the hdr"""
        output = self._get_id(hdr.telescope)
        if create and output is None:
            output = self.new(hdr)
        return output

    def _get_id(self, name):
        """get the id for the telescope from the name"""
        query = GET_TELESCOPE_ID_QUERY % (name)
        try:
            return self.db.get_singular_value(query, "id")
        except Exception as error:
            logging.error(str(error))
            raise error

    def get_name(self, id):
        """get the name for the telescope from the id"""
        query = GET_TELESCOPE_NAME_QUERY % (id)
        try:
            return self.db.get_singular_value(query, "id")
        except Exception as error:
            logging.error(str(error))
            raise error

    def new(self, hdr):
        """create a new telescope from the hdr"""
        return self._new(hdr.telescope)

    def _new(self, name):
        query = INSERT_TELESCOPE_NAME_QUERY % (name)
        try:
            self.db.execute_insert(query)
        except Exception as error:
            logging.error(str(error))
            raise error
        return self.db.get_last_insert_id()
