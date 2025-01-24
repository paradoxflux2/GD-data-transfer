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

config = ConfigParser(interpolation=None)

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

def read_config():
    local_path_config_file = path_current_directory / "settings.ini"

    # check if config file exists
    if not local_path_config_file.is_file():
        print(f"settings.ini not found at {local_path_config_file}")
        sys.exit(1)

    config.read(local_path_config_file)

    android_dir = config.get('Directories', 'android_dir')
    pc_dir = os.path.expandvars(config.get('Directories', 'pc_dir'))

    # files that will be transferred (ik this technically could
    # also be used for things outside gd but who cares lol)
    files = config.get('Files', 'file_list').split(',')

    # if backups will be saved
    backups = config.getboolean('Files', 'save_backups')

    return local_path_config_file, android_dir, pc_dir, files, backups

path_config_file, ANDROID_DIR, PC_DIR, filelist, save_backups = read_config()

print(f"config path: {path_config_file}")
print(f"android dir: {ANDROID_DIR}")
print(f"pc dir: {PC_DIR}")
print(f"saving backups: {save_backups}")

# get adb path
path_adb = path_current_directory / 'adb' / 'adb'
if os.name == "nt":
    path_adb = path_adb.with_name('adb.exe')

if not path_adb.is_file():
    print(f"adb not found at {path_adb}")
    sys.exit(1)

print(f"adb path: {path_adb}")

def backup_file(origin, savefile):
    if save_backups:
        # create backups directory
        backups_dir = path_current_directory / 'backups'
        backups_dir_path = backups_dir / savefile
        if not os.path.exists(backups_dir):
            os.makedirs(backups_dir)

        if origin == "phone":
            NEW_PC_DIR = Path(PC_DIR)
            savefile_path = NEW_PC_DIR / savefile
            if savefile_path.is_file():
                # adapt copy command to each os
                if os.name == "nt":
                    cmd = ['copy', f"{PC_DIR}{savefile}", backups_dir_path]
                else:
                    cmd = ['cp', f"{PC_DIR}{savefile}", backups_dir_path]
                result = subprocess.call(cmd)
        elif origin == "computer":
            cmd = [str(path_adb), "pull", f"{ANDROID_DIR}{savefile}", backups_dir_path]
            subprocess.run(cmd, capture_output=True, text=True, check=False)
        print(f"saved backup at {backups_dir_path}")

def transfersaves(origin):
    global exitstatus
    for savefile in filelist:
        backup_file(origin, savefile)
        if origin == "phone": # phone to computer
            command = [str(path_adb), "pull", f"{ANDROID_DIR}{savefile}", str(PC_DIR)]
        elif origin == "computer": # computer to phone
            command = [str(path_adb), "push", f"{PC_DIR}{savefile}", ANDROID_DIR]
        else:
            print("invalid origin")
            break

        result = subprocess.run(command, capture_output=True, text=True, check=False)
        exitstatus = result.returncode
        if exitstatus == 0:
            print(f"{savefile} succesfully transferred")
        else:
            print(f"couldnt transfer {savefile}. return code: {exitstatus}")
            print(result.stderr)
    return result

def write_config(section, option, value):
    config.set(section, option, value)
    with open(path_config_file, 'w', encoding="utf-8") as configfile:
        config.write(configfile)

def set_dir(dir, new_path):
    if dir == "android_dir":
        global ANDROID_DIR
        ANDROID_DIR = new_path
    elif dir == "pc_dir":
        global PC_DIR
        PC_DIR = new_path

    write_config('Directories', dir, new_path)

def set_backups_setting(value):
    global save_backups
    save_backups = value

    write_config('Files', 'save_backups', str(save_backups).lower())

if __name__ == "__main__":
    ORIGIN = input("transfer files from: (phone/computer): ").strip().lower()
    transfersaves(ORIGIN)
