# Settings related to the file download functionality
from meertime.settings import env

# Directory where MeerTime data is mounted
MEERTIME_DATA_DIR = env("MEERTIME_DATA_DIR", default="/mnt/meertime_data")
