import logging

GET_PIPELINEIMAGES_ID_QUERY = """
SELECT id
FROM PipelineImages
WHERE processing_id = %d AND rank = %d AND image_type='%s' AND image = '%s'
LIMIT 1
"""

GET_PIPELINEIMAGES_QUERY = """
SELECT processing_id, rank, image_type, image
FROM PipelineImages
WHERE id = %d
LIMIT 1
"""

INSERT_PIPELINEIMAGES_QUERY = """
INSERT INTO PipelineImages (processing_id, rank, image_type, image)
VALUES (%d, %d, '%s', '%s')
"""


class PipelineImages:
    def __init__(self, db):
        self.db = db

    def get_id(self, processing_id, rank, image_type, image, create=False):
        """get the id for the pipeline images from the key parameters"""
        query = GET_PIPELINEIMAGES_ID_QUERY % (processing_id, rank, image_type, image)
        try:
            output = self.db.get_singular_value(query, "id")
        except Exception as error:
            logging.error(str(error))
            raise error
        if create and output is None:
            output = self.new(processing_id, rank, image_type, image)
        return output

    def get_config(self, processing_id, rank, image_type, image):
        """get the configuration for the pipeline images from the id"""
        query = GET_PIPELINEIMAGES_QUERY % (processing_id, rank, image_type, image)
        try:
            output = self.db.execute_query(query)
        except Exception as error:
            logging.error(str(error))
            raise error
        output = self.db.get_output()
        if output is None:
            return None
        return database.util.singular_dict(output)

    def new(self, processing_id, rank, image_type, image):
        """create a new pipeline images from the supplied parameters"""
        query = INSERT_PIPELINEIMAGES_QUERY % (processing_id, rank, image_type, image)
        try:
            self.db.execute_insert(query)
        except Exception as error:
            logging.error(str(error))
            raise error
        return self.db.get_last_insert_id()
