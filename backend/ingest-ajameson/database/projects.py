import logging


GET_PROJECT_ID_QUERY = """
SELECT dataportal_projects.id
FROM dataportal_projects
WHERE code = '%s'
LIMIT 1
"""

GET_PROJECT_CODE_QUERY = """
SELECT dataportal_projects.code
FROM dataportal_projects
WHERE id = %d
LIMIT 1
"""

INSERT_PROJECT_CODE_QUERY = """
INSERT INTO dataportal_projects (code)
VALUES ('%s');
"""

INSERT_PROJECT_CODE_SHORT_QUERY = """
INSERT INTO dataportal_projects (code, short)
VALUES ('%s', '%s');
"""

INSERT_PROJECT_CODE_SHORT_DESCRIPTION_EMBARGO_QUERY = """
INSERT INTO dataportal_projects (code, short, description, embargo_period)
VALUES ('%s', '%s', '%s', %d);
"""


class Projects:
    def __init__(self, db):
        self.db = db

    def get_id(self, embargo_period, hdr, create=False):
        """get the id for the project from the hdr"""
        output = self._get_id(hdr.proposal_id)
        if create and output is None:
            output = self.new(embargo_period, hdr)
        return output

    def _get_id(self, code):
        """get the id for the project from the code"""
        query = GET_PROJECT_ID_QUERY % (code)
        try:
            return self.db.get_singular_value(query, "id")
        except Exception as error:
            logging.error(str(error))
            raise error

    def get_code(self, id):
        """get the code for the project from the id"""
        query = GET_PROJECT_CODE_QUERY % (id)
        try:
            return self.db.get_singular_value(query, "id")
        except Exception as error:
            logging.error(str(error))
            raise error

    def new(self, embargo_period, hdr):
        """create a new pulsar from the hdr"""
        return self._new(hdr.proposal_id, None, None, embargo_period)

    def _new(self, code, short, description, embargo_period):
        query = INSERT_PROJECT_CODE_SHORT_DESCRIPTION_EMBARGO_QUERY % (code, short, description, embargo_period)
        try:
            self.db.execute_insert(query)
        except Exception as error:
            logging.error(str(error))
            raise error
        return self.db.get_last_insert_id()
