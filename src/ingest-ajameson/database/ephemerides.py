import logging
import getpass
import json

import database
from util import time, ephemeris

GET_EPHEMERIDES_ID_QUERY = """
SELECT id
FROM dataportal_ephemerides
WHERE pulsar_id = %d AND JSON_CONTAINS(ephemeris,'%s')
LIMIT 1
"""

GET_EPHEMERIDES_QUERY = """
SELECT pulsar_id, created_at, created_by, p0, dm, rm, ephemeris, valid_from, valid_to, comment
FROM dataportal_ephemerides
WHERE id = %d
LIMIT 1
"""

INSERT_EPHEMERIDES_QUERY = """
INSERT INTO dataportal_ephemerides (pulsar_id, created_at, created_by, p0, dm, rm, ephemeris, valid_from, valid_to, comment)
VALUES (%d, '%s', '%s', %f, %f, %f, '%s', '%s', '%s', '%s')
"""


class Ephemerides:
    def __init__(self, db):
        self.db = db

    def get_id(self, pulsar_id, ephemeris, create=False):
        """get the id from the pulsar_id and the ephemeris(object)"""
        return self._get_id(pulsar_id, ephemeris.p0, ephemeris.dm, ephemeris.rm, json.dumps(ephemeris.ephem), create)

    def _get_id(self, pulsar_id, p0, dm, rm, ephemeris_json, create=False):
        """get the id from the pulsar_id and the ephemeris(JSON)"""
        query = GET_EPHEMERIDES_ID_QUERY % (pulsar_id, ephemeris_json)
        try:
            output = self.db.get_singular_value(query, "id")
        except Exception as error:
            logging.error(str(error))
            raise error
        if create and output is None:
            output = self._new(pulsar_id, p0, dm, rm, ephemeris_json)
        return output

    def get_ephemeris(self, ephemeris_id):
        """get the ephemeris dict for specified id"""
        query = GET_EPHEMERIDES_QUERY % (ephemeris_id)
        try:
            self.db.execute_query(query)
        except Exception as error:
            logging.error(str(error))
            raise error
        output = self.db.get_output()
        if output is None:
            return None
        return database.util.singular_dict(output)

    def new(self, pulsar_id, ephemeris):
        """create a new ephemeris from the pulsar_id and ephemeris(object)"""
        return self._new(pulsar_id, ephemeris.p0, ephemeris.dm, ephemeris.rm, ephemeris.json)

    def _new(self, pulsar_id, p0, dm, rm, ephemeris_json):
        """create a new ephemeris, creating the missing parameters"""
        created_at = time.get_current_time()
        created_by = getpass.getuser()
        valid_from = time.get_time(0)
        valid_to = time.get_time(4294967295)
        comment = "Created by database.ephemeris.new"
        query = INSERT_EPHEMERIDES_QUERY % (
            pulsar_id,
            created_at,
            created_by,
            p0,
            dm,
            rm,
            ephemeris_json,
            valid_from,
            valid_to,
            comment,
        )
        try:
            self.db.execute_insert(query)
        except Exception as error:
            logging.error(str(error))
            raise error
        return self.db.get_last_insert_id()
