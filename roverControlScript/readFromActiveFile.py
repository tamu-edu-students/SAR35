# -------------------------------------------------------------
# ECEN 404
# Search and rescue team
#
# This file contains the function for reading from a file that is actively being written to
# NOTE:
# NOTE:
# -------------------------------------------------------------

# imports
import fcntl

# Function to read data from a file that is actively being written to
def read_from_active_file(filePath):
    try:
        with open(filePath, 'r') as f:
            fcntl.flock(f, fcntl.LOCK_SH)  # Acquire shared lock

            # Read data from the file
            file_data = f.read()

            fcntl.flock(f, fcntl.LOCK_UN)  # Release lock

        # Process sensor data
        return file_data
    except Exception as e:
        print("Error from reading 'active file' function: %s", str(e))
