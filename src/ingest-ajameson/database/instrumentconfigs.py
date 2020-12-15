import logging
import database


GET_INSTRUMENTCONFIGS_ID_QUERY = """
SELECT id
FROM dataportal_instrumentconfigs
WHERE name = '%s' and bandwidth = %f and frequency = %f and nchan = %d and npol = %d and beam = '%s'
LIMIT 1
"""

GET_INSTRUMENTCONFIGS_QUERY = """
SELECT name, bandwidth, frequency, nchan, npol, beam 
FROM dataportal_instrumentconfigs
WHERE id = %d
LIMIT 1
"""

INSERT_INSTRUMENTCONFIGS_QUERY = """
INSERT INTO dataportal_instrumentconfigs (name, bandwidth, frequency, nchan, npol, beam)
VALUES ('%s', %f, %f, %d, %d, '%s')
"""


class InstrumentConfigs:
    def __init__(self, db):
        self.db = db

    def get_id(self, name, hdr, create=False):
        """get the id for the telescope from the hdr"""
        output = self._get_id(name, hdr.bandwidth, hdr.frequency, hdr.nchan, hdr.npol, hdr.beam)
        if create and output is None:
            output = self.new(name, hdr)
        return output

    def _get_id(self, name, bandwidth, frequency, nchan, npol, beam):
        """get the id for the specified instrument config"""
        query = GET_INSTRUMENTCONFIGS_ID_QUERY % (name, bandwidth, frequency, nchan, npol, beam)
        try:
            return self.db.get_singular_value(query, "id")
        except Exception as error:
            logging.error(str(error))
            raise error

    def get_config(self, id):
        """get the instrument config dict for specified id"""
        query = GET_INSTRUMENTCONFIGS_QUERY % (id)
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

    def new(self, name, hdr):
        """create a new instrument config from the hdr"""
        return self._new(name, hdr.bandwidth, hdr.frequency, hdr.nchan, hdr.npol, hdr.beam)

    def _new(self, name, bandwidth, frequency, nchan, npol, beam):
        query = INSERT_INSTRUMENTCONFIGS_QUERY % (name, bandwidth, frequency, nchan, npol, beam)
        try:
            self.db.execute_insert(query)
        except Exception as error:
            logging.error(str(error))
            raise error
        return self.db.get_last_insert_id()