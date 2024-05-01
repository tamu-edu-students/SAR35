# -------------------------------------------------------------
# ECEN 404
# Search and rescue team
#
# This file contains the function that reads the latest stop/start data and writes it to a new csv for the move system
# NOTE:
# -------------------------------------------------------------

import csv

def read_first_entry_of_emg_stop_csv(csv_file):
    """
    Read the first entry of a CSV file and return it as an integer.

    Parameters:
        csv_file (str): Path to the CSV file.

    Returns:
        int: The first entry of the CSV file as an integer.
    """
    # Open the CSV file in read mode
    with open(csv_file, 'r') as file:
        # Create a CSV reader object
        csv_reader = csv.reader(file)

        # Get the first row using next() function
        first_row = next(csv_reader)

        # Convert data to int
        try:
            first_entry = int(first_row[0])
        except Exception as e:
            print("Error reading data from emg stop file: %s", str(e))

    return first_entry
