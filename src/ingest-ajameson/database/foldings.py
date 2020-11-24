import logging


GET_FOLDINGS_ID_QUERY = """
SELECT id
FROM Foldings
WHERE processing_id = %d and ephemeris_id = %d
LIMIT 1
"""

GET_FOLDINGS_QUERY = """
SELECT processing_id, ephemeris_id, nbin, npol, nchan, dm, tsubint
FROM Foldings
WHERE id = %d
LIMIT 1
"""

INSERT_FOLDINGS_QUERY = """
INSERT INTO Foldings (processing_id, ephemeris_id, nbin, npol, nchan, dm, tsubint)
VALUES (%d, %d, %d, %d, %d, %f, %d)
"""


class Foldings:
    def __init__(self, db):
        self.db = db

    def get_id(self, processing_id, ephemeris_id, hdr, create=False):
        """get the id for the specified folding, creating is necessary"""
        return self._get_id(
            processing_id,
            ephemeris_id,
            hdr.fold_nbin,
            hdr.fold_npol,
            hdr.fold_nchan,
            hdr.fold_dm,
            hdr.fold_tsubint,
            create,
        )

    def _get_id(self, processing_id, ephemeris_id, nbin, npol, nchan, dm, tsubint, create=False):
        """get the id for the specified instrument config"""
        query = GET_FOLDINGS_ID_QUERY % (processing_id, ephemeris_id)
        try:
            output = self.db.get_singular_value(query, "id")
        except Exception as error:
            logging.error(str(error))
            raise error
        if create and output is None:
            output = self.new(processing_id, ephemeris_id, nbin, npol, nchan, dm, tsubint)
        return output

    def get_config(self, id):
        """get the instrument config dict for specified id"""
        query = GET_FOLDINGS_QUERY % (id)
        try:
            self.db.execute_query(query)
            return self.db.get_singular_value(query, "id")
        except Exception as error:
            logging.error(str(error))
            raise error
        output = self.db.get_output()
        return singular_dict(output)

    def new(self, processing_id, ephemeris_id, nbin, npol, nchan, dm, tsubint):
        query = INSERT_FOLDINGS_QUERY % (processing_id, ephemeris_id, nbin, npol, nchan, dm, tsubint)
        try:
            self.db.execute_insert(query)
        except Exception as error:
            logging.error(str(error))
            raise error
        return self.db.get_last_insert_id()
