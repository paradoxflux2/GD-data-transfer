"""
this file handles reading config and transferring data

GUI stuff is in gddt-gui.py

uses python 3.11
"""

import os
import subprocess
import sys
from configparser import ConfigParser
from pathlib import Path
import shutil

config = ConfigParser(interpolation=None)

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

class ConfigManager:
    """manages config"""
    def __init__(self, path):
        self.path_config_file = path / "settings.ini"
        self.android_dir = ""
        self.pc_dir = ""
        self.filelist = []
        self.save_backups = None
        self.last_transfer = ""

    def read_config(self):
        """take things from config"""
        # check if config file exists
        if not self.path_config_file.is_file():
            print(f"settings.ini not found at {self.path_config_file}")
            sys.exit(1)

        config.read(self.path_config_file)

        # directories
        self.android_dir = config.get('Directories', 'android_dir')
        self.pc_dir = os.path.expandvars(config.get('Directories', 'pc_dir'))

        # files that will be transferred (ik this technically could
        # also be used for things outside gd but who cares lol)
        self.filelist = config.get('Files', 'file_list').split(',')

        # if backups will be saved
        self.save_backups = config.getboolean('Files', 'save_backups')

        # the last transfer done. "None" by default
        self.last_transfer = config.get('Files', 'last_transfer')

    def write_config(self, section, option, value):
        """writes to config and sets value"""
        config.set(section, option, value)

        if option == "android_dir":
            self.android_dir = value
        elif option == "pc_dir":
            self.pc_dir = value
        elif option == "filelist":
            self.filelist = value
        elif option == "save_backups":
            self.save_backups = value
        elif option == "last_transfer":
            self.last_transfer = value

        with open(self.path_config_file, 'w', encoding="utf-8") as configfile:
            config.write(configfile)

    def set_dir(self, directory, new_path):
        """sets new directory and writes it to config"""
        if directory == "android_dir":
            self.android_dir = new_path
        elif directory == "pc_dir":
            self.pc_dir = new_path

        self.write_config('Directories', directory, new_path)

    def set_backups_setting(self, new_value):
        """changes backups setting to a boolean value"""
        self.write_config('Files', 'save_backups', str(new_value))

    def set_last_transfer(self, new_last_transfer):
        """sets new last transfer"""
        self.write_config('Files', 'last_transfer', new_last_transfer)

config_manager = ConfigManager(path_current_directory)

config_manager.read_config()

# === transferring data ===

# get adb path
path_adb = path_current_directory / 'adb' / 'adb'
if os.name == "nt":
    path_adb = path_adb.with_name('adb.exe')

if not path_adb.is_file():
    print(f"adb not found at {path_adb}")
    sys.exit(1)

def backup_file(source, savefile):
    """backs up a file into backups directory"""

    if config_manager.save_backups:
        # create backups directory
        backups_dir = path_current_directory / 'backups'
        backups_savefile_path = backups_dir / savefile
        if not os.path.exists(backups_dir):
            os.makedirs(backups_dir)

        # if it's phone to pc, we copy savefile from pc_dir
        if source == "phone":
            savefile_path = Path(config_manager.pc_dir) / savefile
            if savefile_path.is_file():
                shutil.copy(f"{config_manager.pc_dir}{savefile}", backups_savefile_path)

        # if its pc to phone, we pull savefile from android_dir
        elif source == "computer":
            cmd = [str(path_adb), "pull", f"{config_manager.android_dir}{savefile}", str(backups_savefile_path)]
            subprocess.run(cmd, capture_output=True, text=True, check=False)

        print(f"saved backup at {backups_savefile_path}")

def revert_last_transfer():
    """reverts last transfer by copying whats inside /backups into
    save folder"""

    pc_dir = config_manager.pc_dir
    android_dir = config_manager.android_dir
    filelist = config_manager.filelist
    last_transfer = config_manager.last_transfer

    for savefile in filelist:
        backups_dir = path_current_directory / 'backups'
        backups_savefile_path = backups_dir / savefile

        if last_transfer == "phonetopc":
            savefile_path = Path(pc_dir) / savefile
            if savefile_path.is_file():
                shutil.copy(f"{pc_dir}{savefile}", backups_savefile_path)
                print(f"copied {pc_dir}{savefile} to {backups_savefile_path}")

        elif last_transfer == "pctophone":
            cmd = [str(path_adb), "push", backups_savefile_path, f"{android_dir}{savefile}"]
            subprocess.run(cmd, capture_output=True, text=True, check=False)
        else:
            print("stupid")
            break

def transfersaves(source, destination):
    """transfers save files between devices"""
    pc_dir = config_manager.pc_dir
    android_dir = config_manager.android_dir
    filelist = config_manager.filelist

    for savefile in filelist:
        print(f"backing up {savefile}")
        backup_file(source, savefile)

        print(f"moving {savefile} to {destination}")

        if destination == "computer": # phone to computer
            command = [str(path_adb), "pull", f"{android_dir}{savefile}", str(pc_dir)]
            config_manager.set_last_transfer("phonetopc")

        elif destination == "phone": # computer to phone
            command = [str(path_adb), "push", f"{pc_dir}{savefile}", android_dir]
            config_manager.set_last_transfer("pctophone")
        else:
            print("invalid source")
            break

        result = subprocess.run(command, capture_output=True, text=True, check=False)

        if result.returncode == 0:
            print(f"{savefile} succesfully transferred")
        else:
            print(f"couldnt transfer {savefile}. return code: {result.returncode}")
            print(result.stderr)
            config_manager.set_last_transfer("None")
            print("all other files have been skipped")
            break

    return result

# print everything
if IS_BUNDLE:
    print(f"running as bundle, on {os.name}")
else:
    print(f"running directly, on {os.name}")
print(f"application directory: {path_current_directory}")
print(f"config path: {config_manager.path_config_file}")
print(f"android dir: {config_manager.android_dir}")
print(f"pc dir: {config_manager.pc_dir}")
print(f"adb path: {path_adb}")

if __name__ == "__main__":
    DST = input("transfer files to: (phone/computer): ").strip().lower()
    SRC = "phone" if DST == "computer" else "computer"

    transfersaves(SRC, DST)
