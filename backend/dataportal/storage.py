from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
import re


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


def get_valid_filename(s):
    """
    Return the given string converted to a string that can be used for a clean
    filename. Remove leading and trailing spaces; convert other spaces to
    underscores; and remove anything that is not an alphanumeric, dash,
    underscore, dot, or plus.
    >>> get_valid_filename("john's portrait in 2004.jpg")
    'johns_portrait_in_2004.jpg'
    >>> get_valid_filename("J1234+5678.dat")
    'J1234+5678.dat'
    >>> get_valid_filename("J1234-5678.dat")
    'J1234-5678.dat'
    """
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-+\w.]', '', s)


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

    def get_valid_name(self, name):
        """
        Return a filename, based on the provided filename, that's suitable for
        use in the target storage system.
        """
        return get_valid_filename(name)
