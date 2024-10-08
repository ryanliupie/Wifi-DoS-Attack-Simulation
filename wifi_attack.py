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


