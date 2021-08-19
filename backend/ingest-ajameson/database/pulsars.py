import logging


GET_PULSAR_ID_QUERY = """
SELECT dataportal_pulsars.id
FROM dataportal_pulsars
WHERE jname = '%s'
LIMIT 1
"""

GET_PULSAR_JNAME_QUERY = """
SELECT dataportal_pulsars.jname
FROM dataportal_pulsars
WHERE id = %d
LIMIT 1
"""

INSERT_PULSAR_JNAME_QUERY = """
INSERT INTO dataportal_pulsars (jname, state, comment)
VALUES ('%s','%s','%s');
"""


class Pulsars:
    def __init__(self, db):
        self.db = db

    def get_id(self, hdr, create=False):
        """get the id for the pulsar from the hdr"""
        output = self._get_id(hdr.source)
        if create and output is None:
            output = self.new(hdr)
        return output

    def _get_id(self, jname):
        """get the id for the pulsar from the jname"""
        query = GET_PULSAR_ID_QUERY % (jname)
        try:
            return self.db.get_singular_value(query, "id")
        except Exception as error:
            logging.error(str(error))
            raise error

    def get_jname(self, id):
        """get the jname for the pulsar from the id"""
        query = GET_PULSAR_JNAME_QUERY % (id)
        try:
            return self.db.get_singular_value(query, "id")
        except Exception as error:
            logging.error(str(error))
            raise error

    def new(self, hdr):
        """create a new pulsar from the hdr"""
        return self._new(hdr.source, None, None)

    def _new(self, jname, state, comment):
        query = INSERT_PULSAR_JNAME_QUERY % (jname, state, comment)
        try:
            self.db.execute_insert(query)
        except Exception as error:
            logging.error(str(error))
            raise error
        return self.db.get_last_insert_id()
