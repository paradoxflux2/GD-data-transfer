"""
this file handles reading config and transferring data

GUI stuff is in gddt.py

uses python 3.11
"""

import os # for adb i will use ppadb one day
import subprocess
import sys
from configparser import ConfigParser
from pathlib import Path

config = ConfigParser()

exitstatus = ""

# get application path (thank you random person from stackoverflow
# that wrote this like 5 years ago)
if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app 
    # path into variable executable'.
    path_current_directory = Path(sys.executable).parent
    print(f"running as bundle, on {os.name}")
else:
    path_current_directory = Path(__file__).parent
    print(f"running directly, on {os.name}")

print(f"application directory: {path_current_directory}")

# config stuff
path_config_file = path_current_directory / "settings.ini"

# check if config file exists
if not path_config_file.is_file():
    print(f"settings.ini not found at {path_config_file}")
    sys.exit(1)

print(f"config path: {path_config_file}")

config.read(path_config_file)

ANDROID_DIR = config.get('Directories', 'android_dir')
PC_DIR = os.path.expandvars(config.get('Directories', 'pc_dir'))

print(f"android dir: {ANDROID_DIR}")
print(f"pc dir: {PC_DIR}")

# get adb path
path_adb = path_current_directory / 'adb' / 'adb'
if os.name == "nt":
    path_adb = path_adb.with_name('adb.exe')

if not path_adb.is_file():
    print(f"adb not found at {path_adb}")
    sys.exit(1)


print(f"adb path: {path_adb}")

# files that will be transferred (ik this technically could
# also be used for things outside gd but who cares lol)
filelist = config.get('Files', 'file_list').split(',')

def transfersaves(origin):
    """transfer save data with adb commands"""  
    global exitstatus
    if origin == "phone": # phone to pc
        for savefile in filelist:
            pullcommand = [str(path_adb), "pull", f"{ANDROID_DIR}{savefile}", str(PC_DIR)]
            #print(pullcommand)
            result = subprocess.run(pullcommand, capture_output=True, text=True, check=False)
            exitstatus = result.returncode
            if exitstatus == 0:
                print(f"{savefile} succesfully transferred")
            else:
                print(f"couldnt transfer {savefile}. return code: {exitstatus}")
                print(result.stderr)

    elif origin == "computer": # pc to phone
        for savefile in filelist:
            pushcommand = [str(path_adb), "push", f"{PC_DIR}{savefile}", ANDROID_DIR]
            #print(pushcommand)
            result = subprocess.run(pushcommand, capture_output=True, text=True, check=False)
            exitstatus = result.returncode
            if exitstatus == 0:
                print(f"{savefile} succesfully transferred")
            else:
                print(f"couldnt transfer {savefile}. return code: {exitstatus}")
                print(result.stderr)
    else:
        print("invalid origin")

def set_android_dir(new_path):
    global ANDROID_DIR
    ANDROID_DIR = new_path
    config.set('Directories', 'android_dir', new_path)
    with open(path_config_file, 'w') as configfile:
        config.write(configfile)

def set_pc_dir(new_path):
    global PC_DIR
    PC_DIR = new_path
    
    config.set('Directories', 'pc_dir', new_path)
    with open(str(path_config_file), 'w') as configfile:
        config.write(configfile)

if __name__ == "__main__":
    ORIGIN = input("transfer files from: (phone/computer): ").strip().lower()
    transfersaves(ORIGIN)
