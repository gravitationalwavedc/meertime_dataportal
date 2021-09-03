from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os


def get_upload_location(instance, filename):
    """
    This method provides a filename to store an uploaded image.
    Inputs:
    instance: instance of a Pipelineimages class
    filename: string

    returns:
    string:
    """
    telescope = instance.processing.observation.telescope.name
    psr = instance.processing.observation.target.name
    beam = instance.processing.observation.instrument_config.beam
    utc = instance.processing.observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S")
    return f"{telescope}/{psr}/{utc}/{beam}/{filename}"


def get_pipeline_upload_location(instance, filename):
    """
    This method provides a filename to store an uploaded file produced by a pipeline.
    Inputs:
    instance: instance of a Pipelinefiles class
    filename: string

    returns:
    string:
    """
    telescope = instance.processing.observation.telescope.name
    pipeline = instance.processing.pipeline.name
    psr = instance.processing.observation.target.name
    beam = instance.processing.observation.instrument_config.beam
    utc = instance.processing.observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S")
    return f"{telescope}/{pipeline}/{psr}/{utc}/{beam}/{filename}"


class OverwriteStorage(FileSystemStorage):
    """
    Provide a storage which will overwrite files if file with the same name is uploaded
    """

    def get_available_name(self, name, max_length=None):

        if self.exists(name):
            os.remove(os.path.join(self.location, name))
        if max_length:
            name = super().get_available_name(name, max_length)
        return name
