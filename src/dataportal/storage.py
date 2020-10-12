from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os


def get_upload_location(instance, filename):
    """
    This method provides a filename to store an uploaded image.
    Inputs:
    instance: instance of an Observation class
    filename: string

    returns:
    string:
    """
    psr = instance.pulsar.jname
    beam = instance.beam
    utc = instance.utc.utc_ts.strftime("%Y-%m-%d-%H:%M:%S")
    return f"{psr}/{utc}/{beam}/{filename}"


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
