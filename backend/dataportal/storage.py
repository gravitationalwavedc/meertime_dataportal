from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
import re
import hashlib


def create_file_hash(file_path):
    sha256_hash = hashlib.sha256()
    # Open the file in binary mode
    with file_path.open('rb') as file:
        # Read the entire file content
        file_content = file.read()
    # Update the hash object with the file content
    sha256_hash.update(file_content)
    # Get the hexadecimal representation of the hash
    return sha256_hash.hexdigest()



def get_upload_location(instance, filename):
    """
    This method provides a filename to store an uploaded image.
    Inputs:
    instance: instance of a Pipelineimages class
    filename: string

    returns:
    string:
    """
    telescope = instance.fold_pulsar_result.observation.telescope.name
    project = instance.fold_pulsar_result.observation.project.code
    psr = instance.fold_pulsar_result.observation.pulsar.name
    beam = instance.fold_pulsar_result.observation.beam
    utc = instance.fold_pulsar_result.observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S")
    return f"{telescope}/{project}/{psr}/{utc}/{beam}/{filename}"


def get_template_upload_location(instance, filename):
    """
    This method provides a filename to store an uploaded image.
    Inputs:
    instance: instance of a Pipelineimages class
    filename: string

    returns:
    string:
    """
    pulsar = instance.pulsar.name
    project_code = instance.project.code
    band = instance.band
    created_at = instance.created_at
    return f"{project_code}/{pulsar}/{band}/{created_at}_{filename}"


def get_pipeline_upload_location(instance, filename):
    """
    This method provides a filename to store an uploaded file produced by a pipeline.
    Inputs:
    instance: instance of a Pipelinefiles class
    filename: string

    returns:
    string:
    """
    telescope = instance.pipeline_run.observation.telescope.name
    project = instance.pipeline_run.observation.project.code
    psr = instance.pipeline_run.observation.pulsar.name
    beam = instance.pipeline_run.observation.beam
    utc = instance.pipeline_run.observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S")
    return f"{telescope}/{project}/{psr}/{utc}/{beam}/{filename}"


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
    s = str(s).strip().replace(" ", "_")
    return re.sub(r"(?u)[^-+\w.]", "", s)


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
