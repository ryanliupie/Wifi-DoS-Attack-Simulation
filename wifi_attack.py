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
# If error, then time-out and reserves it as e (why failure occured)
# We log this error with "command failed" and displays which command fails 
# These components allow a shell command to be executed and handles error with execution of commands that may occur

def is_essid_present(essid, lst): 
    return not any(essid in item["ESSID"] for item in lst)
# This checks if a given ESSID (Extended Service Set Identifer) which represents the name of a wireless network, it already present in the list of access points 
# If ESSID  is found in list (network is available), returns 'false" as we do not need to add to avoid duplication 
# If ESSID is not found, returns "true" as you can add ESSID to list 

def check_superuser(): 
    if os.geteuid() != 0: 
        logging.error("Script must run with Sudo")
        exit(1)
# This ensures the program is ran with superuser/superadmin/root privileges for elevated permissions to perform tasks
# If user is not 0, (!=) then it logs an error that it must run with "Sudo" superuser do
# EUID must be 0 

def archive_csv_files():
    with tempfile.TemporaryDirectory() as temp_backup_dir:
        for current_file in os.listdir():
            if current_file.endswith(".csv"):
                logging.info("Moving existing .csv files to backup directory")
                shutil.move(current_file, os.path.join(temp_backup_dir, f"{datetime.now()}-{current_file}"))
# This function moves .csv files in current directory to a temporary backup 
# backs up existing files to prevent overwrite and auto deletes temp using "with"
# Ensures only recent file remain in main directory, avoiding conflict if new files are created

def discover_wireless_adapters():
    adapter_pattern = re.compile("^wlan[0-9]+")
#can be "wlan0", cannot be "eth0" or "wlan-0" as it does not follow pattern
    iwconfig_output = run_command(["iwconfig"])
    wireless_interfaces = adapter_pattern.findall(iwconfig_output)
    if not wireless_interfaces:
        logging.error("No Wi-Fi adapters available. Connect one and try again")
        exit(1)
    return(wireless_interfaces)
# This finds/detects wireless interfaces on a system 
# We use re module to compile a regular expression of only "wlan" and "0 to 9" such as "wlan5"
# Run iwconfig to get wireless interface information 
# if not wireless interfaces = no wireless interfaces --> log as error with text for clarity
# exit (1) as in signals error --> script does not keep running, preventing loop

def terminate_conflicting_processes(): 
    logging.info("Terminating conflicting processes")
    run_command(["airmon-ng", "sudo", "check", "terminate"])
# Used for terminating any processes that coflict with "airmon-ng" which this is used to manage wireless networks
# We will log this at level 6 as script will terminate conflicting process
# Run command to verify if process was terminated 

def enable_monitor_mode(interface):
    logging.info(f"Starting monitor mode{interface}")
    run_command(["sudo", "airmon-ng", "check", "terminate"])
# Places wireless network interface into "monitor mode" allowing the wireless adapter to listen/capture wireless traffic
# Log at level 6 that monitor mode will begin along with the specific interface such as "wlan3"

def scan_networks(interface):
    logging.info(f"Scanning for networks on {interface}")
    process = subprocess.Popen(["sudo", "airdump-ng", "-w", "file", "--write-interval", "1", "--output-format", "csv", f"{interface}mon"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
# Responsible for scanning close wireless networks using wireless interface that was put in monitor mode previously
# "Popen" starts the command and executes the rest of the script; allows commands to run in backround as network scanning is being conducted 
# stdout.DEVNULL will redirect standard output; silencing it to avoid clutter
# stderr- does the same thing, ensuring no error messages from "airodump" are displayed in the terminal
    try:
        while True:
            clear_screen()
            load_access_points()
            display_access_points()
            time.sleep(3)
    except KeyboardInterrupt:
        logging.info("Select target network")
        process.terminate()
# This is a loop meant for continuously displaying detected wireless access points per 3 seconds reducing cpu usage
# When targeted SSID is met, we must stop it with "KeybaordInterrupt" -- Ctrl+C
# As airodump-ng (network scan) was started as background process with "Popen", we can terminate it freeeing up the wireless interface to conduct further actions 
#             












