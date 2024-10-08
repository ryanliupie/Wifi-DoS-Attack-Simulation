# Ryan Liu
# Oct 7th, 2024  

#list alphabetically as per PEPE 8 recommendations 

import csv 
# this type of file (CSV) contains rows, this will help us read those rows easier. 
from datetime import datetime
# This will help keep track of the time and date in case we need to such as backing up a copy
import logging
# Tracks specific events that occur when program runs (0-7 levels)
import os
# Acts as a bridge between this python program and the operating system(interact with OS)
import re
# "regular expressions" will filter out specific information from a whole set of text; separating paths
import shutil
# This helps move files to a different folder (CSV)
import subprocess
# This will help running commands on Kali Linux for us
import tempfile
# This will create a temporary folder for backing up existing .CSV file to reduce organizational issues
import time
# This is a timer to pause activites before activating them again


logging.basicConfig(level=logging.INFO)
# Set the logging level (Emily Always Calls Eric When Network Is Down)
# Emergency, Alert, Critical, Error, Warning, Notice, Information, Debug
# Set log level to INFO for general updates

active_wifi_connections = []
# Create list for wireless networks 

def clear_screen():
    subprocess.call("Clear", shell = True)
# This resets the terminal output, so that the user can view clean updated network data

def run_command():
    try:
        result = subprocess.run(command, capture_output = True, check = True)
        return result.stdout.decode()
# We will attempt to run a command to see if it works and return output (true) if it goes through with .stdout   
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {' '.join(command)}\nError: {e}")
        return None
# If error, then time-out and reserves it as e
# We log this error with "command failed" and displays which command fails 
# These components allow a shell command to be executed and handles error with execuation of commands that may occur
