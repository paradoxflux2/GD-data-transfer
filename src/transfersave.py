"""
this file handles reading config and transferring data

GUI stuff is in gddt.py

uses python 3.11
"""

import os
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
    IS_BUNDLE = True
else:
    path_current_directory = Path(__file__).parent
    IS_BUNDLE = False

# === config ===

def read_config():
    """take things from config"""
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

    # the last transfer done. "None" by default
    last_transfer_done = config.get('Files', 'last_transfer')

    return local_path_config_file, android_dir, pc_dir, files, backups, last_transfer_done

path_config_file, ANDROID_DIR, PC_DIR, filelist, save_backups, last_transfer = read_config()

def write_config(section, option, value):
    """write to config"""
    config.set(section, option, value)
    with open(path_config_file, 'w', encoding="utf-8") as configfile:
        config.write(configfile)

def set_dir(directory, new_path):
    """set new directory and write it to config"""
    if directory == "android_dir":
        global ANDROID_DIR
        ANDROID_DIR = new_path
    elif directory == "pc_dir":
        global PC_DIR
        PC_DIR = new_path

    write_config('Directories', directory, new_path)

def set_backups_setting(value):
    """change backups setting to a boolean value"""
    global save_backups
    save_backups = value

    # convert to string and lowercase so that configparser takes it as a boolean
    # (i actually think its case-insensitive but at this point it's so ingrained into the code
    # that its easier to leave it like that)
    write_config('Files', 'save_backups', str(save_backups).lower())

def set_last_transfer(new_last_transfer):
    global last_transfer
    last_transfer = new_last_transfer

    write_config('Files', 'last_transfer', new_last_transfer)

# get adb path
path_adb = path_current_directory / 'adb' / 'adb'
if os.name == "nt":
    path_adb = path_adb.with_name('adb.exe')

if not path_adb.is_file():
    print(f"adb not found at {path_adb}")
    sys.exit(1)

def backup_file(source, savefile):
    if save_backups:
        # create backups directory
        backups_dir = path_current_directory / 'backups'
        backups_dir_path = backups_dir / savefile
        if not os.path.exists(backups_dir):
            os.makedirs(backups_dir)

        if source == "phone":
            new_pc_dir = Path(PC_DIR)
            savefile_path = new_pc_dir / savefile
            if savefile_path.is_file():
                # adapt copy command to each os
                if os.name == "nt":
                    cmd = ['copy', f"{PC_DIR}{savefile}", backups_dir_path]
                else:
                    cmd = ['cp', f"{PC_DIR}{savefile}", backups_dir_path]
                result = subprocess.call(cmd)
                print(result)
        elif source == "computer":
            cmd = [str(path_adb), "pull", f"{ANDROID_DIR}{savefile}", backups_dir_path]
            subprocess.run(cmd, capture_output=True, text=True, check=False)
        print(f"saved backup at {backups_dir_path}")

def revert_last_transfer():
    for savefile in filelist:
        backups_dir = path_current_directory / 'backups'
        backups_dir_path = backups_dir / savefile

        if last_transfer == "phonetopc":
            new_pc_dir = Path(PC_DIR)
            savefile_path = new_pc_dir / savefile
            if savefile_path.is_file():
                # adapt copy command to each os
                if os.name == "nt":
                    cmd = ['copy', backups_dir_path, f"{PC_DIR}{savefile}"]
                else:
                    cmd = ['cp', backups_dir_path, f"{PC_DIR}{savefile}"]

                result = subprocess.call(cmd)
                print(result)
        elif last_transfer == "pctophone":
            cmd = [str(path_adb), "push", backups_dir_path, f"{ANDROID_DIR}{savefile}"]
            subprocess.run(cmd, capture_output=True, text=True, check=False)
        else:
            print("stupid")
            break

def transfersaves(source):
    global exitstatus
    for savefile in filelist:
        backup_file(source, savefile)
        if source == "phone": # phone to computer
            command = [str(path_adb), "pull", f"{ANDROID_DIR}{savefile}", str(PC_DIR)]
            set_last_transfer("phonetopc")
        elif source == "computer": # computer to phone
            command = [str(path_adb), "push", f"{PC_DIR}{savefile}", ANDROID_DIR]
            set_last_transfer("pctophone")
        else:
            print("invalid source")
            break

        result = subprocess.run(command, capture_output=True, text=True, check=False)
        exitstatus = result.returncode
        if exitstatus == 0:
            print(f"{savefile} succesfully transferred")
        else:
            print(f"couldnt transfer {savefile}. return code: {exitstatus}")
            print(result.stderr)
            set_last_transfer("None")
            print("all other files have been skipped")
            break
    return result

# print everything
if IS_BUNDLE:
    print(f"running as bundle, on {os.name}")
else:
    print(f"running directly, on {os.name}")
print(f"application directory: {path_current_directory}")
print(f"config path: {path_config_file}")
print(f"android dir: {ANDROID_DIR}")
print(f"pc dir: {PC_DIR}")
print(f"adb path: {path_adb}")
#print(f"last transfer: {last_transfer}")

if __name__ == "__main__":
    SOURCE = input("transfer files from: (phone/computer): ").strip().lower()
    transfersaves(SOURCE)
