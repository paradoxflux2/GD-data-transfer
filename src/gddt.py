"""
this file handles reading config and transferring data

while it's functional by itself it is usually only used for testing. 
gui has more features (e.g. reverting transfer)
"""

import os
import subprocess
import sys
from configparser import ConfigParser
from pathlib import Path
from shutil import copy, which
from urllib.request import urlretrieve  # for downloading adb
from zipfile import ZipFile

config = ConfigParser(interpolation=None)

# get application path
if getattr(sys, "frozen", False):
    path_current_directory = Path(sys.executable).parent
    IS_BUNDLE = True
else:
    path_current_directory = Path(__file__).parent
    IS_BUNDLE = False

# === config ===


class ConfigManager:
    """manages config"""

    def __init__(self, path: Path):
        self.path_config_file = path / "settings.ini"
        self.read_config()

    def create_config(self):
        """create config file with default values"""
        config["Directories"] = {
            "android_dir": "/storage/emulated/0/Android/media/com.geode.launcher/save/",
            "pc_dir": "%LOCALAPPDATA%\\GeometryDash\\",
        }
        config["Files"] = {
            "file_list": "CCGameManager.dat,CCLocalLevels.dat",
            "save_backups": "True",
            "last_transfer": "None",
        }
        config["Other"] = {
            "theme": "arc",
            "hide_ugly_themes": "True",
            "show_actual_error_messages": "False",
            "first_run": "True",
        }

        with open(self.path_config_file, "w", encoding="utf-8") as configfile:
            config.write(configfile)

        print("config file created")

    def read_config(self):
        """take things from config"""
        # check if config file exists
        if not self.path_config_file.is_file():
            print(f"settings.ini not found at {self.path_config_file}. creating it...")
            self.create_config()

        config.read(self.path_config_file)

        # [Directories]
        self.android_dir = config.get("Directories", "android_dir")
        self.pc_dir = os.path.expandvars(config.get("Directories", "pc_dir"))
        # [Files]
        self.filelist = config.get("Files", "file_list").split(",")
        self.save_backups = config.getboolean("Files", "save_backups")
        self.last_transfer = config.get("Files", "last_transfer")
        # [Other]
        self.theme = config.get("Other", "theme")
        self.hide_ugly_themes = config.getboolean("Other", "hide_ugly_themes")
        self.show_actual_error_messages = config.getboolean(
            "Other", "show_actual_error_messages"
        )
        self.first_run = config.getboolean("Other", "first_run")

    def write_config(self, section: str, option: str, value: str):
        """writes to config and sets value"""
        config.set(section, option, str(value))

        with open(self.path_config_file, "w", encoding="utf-8") as configfile:
            config.write(configfile)

        setattr(self, option, value)

        # get all options
        valid_sections = ["Directories", "Files", "Other"]
        valid_options = []

        for valid_section in valid_sections:
            valid_options += config.options(valid_section)

        if option in valid_options:
            setattr(self, option, value)


config_manager = ConfigManager(path_current_directory)

# === transferring data ===


def subprocess_run(command: str) -> str:
    """wrapper for subprocess.run with some preset parameters"""
    if IS_BUNDLE and os.name == "nt":
        flags = subprocess.CREATE_NO_WINDOW
    else:
        flags = 0

    return subprocess.run(
        command,
        creationflags=flags,
        capture_output=True,
        text=True,
        check=False,
    )


# check if adb is installed
def adb_exists():
    """
    check if adb is on PATH or in the gddt folder

    can return three values:
    0: ADB is not installed,
    1: ADB is on PATH,
    2: ADB is in the gddt folder,
    """
    # check if its in path
    if which("adb") is not None:
        return 1

    # check if its in gddt folder
    path_adb_gddt = path_current_directory / "adb" / "adb"
    if os.name == "nt":
        path_adb_gddt = path_adb_gddt.with_name("adb.exe")

    if path_adb_gddt.is_file():
        return 2

    # neither of those are true
    return 0


if adb_exists() == 1:  # it's on PATH
    ADB_EXE = "adb"

elif adb_exists() == 2:  # it's in the gddt folder
    ADB_EXE = path_current_directory / "adb" / "adb"
    if os.name == "nt":
        ADB_EXE = ADB_EXE.with_name("adb.exe")


def backup_file(source: str, savefile: str):
    """backs up a file into backups directory"""

    if config_manager.save_backups:
        print(f"backing up {savefile}...")

        backups_dir = path_current_directory / "backups"
        savefile_backup_path = backups_dir / savefile
        # create backups directory
        if not os.path.exists(backups_dir):
            os.makedirs(backups_dir)

        # if it's phone to pc, we copy savefile from pc_dir
        if source == "phone":
            savefile_path = Path(config_manager.pc_dir) / savefile
            if savefile_path.is_file():
                copy(savefile_path, savefile_backup_path)

        # if its pc to phone, we pull savefile from android_dir
        elif source == "computer":
            savefile_path = Path(config_manager.android_dir) / savefile
            cmd = [
                str(ADB_EXE),
                "pull",
                str(savefile_path.as_posix()),
                str(savefile_backup_path),
            ]
            subprocess_run(cmd)


def undo_last_transfer() -> str:
    """reverts last transfer by copying whats inside /backups into
    save folder"""

    pc_dir = config_manager.pc_dir
    android_dir = config_manager.android_dir
    filelist = config_manager.filelist
    last_transfer = config_manager.last_transfer

    for savefile in filelist:
        backups_dir = path_current_directory / "backups"
        savefile_backup_path = backups_dir / savefile

        if last_transfer == "phonetopc":
            savefile_path = Path(pc_dir) / savefile
            if savefile_path.is_file():
                result = copy(savefile_backup_path, savefile_path)
                print(f"copied {str(savefile_backup_path)} to {str(savefile_path)}")

        elif last_transfer == "pctophone":
            savefile_path = Path(android_dir) / savefile
            cmd = [
                str(ADB_EXE),
                "push",
                str(savefile_backup_path),
                str(savefile_path.as_posix()),
            ]
            result = subprocess_run(cmd)
        else:
            print("stupid")
            break

    config_manager.write_config("Files", "last_transfer", "None")
    return result


def transfer_saves(source: str, destination: str) -> str:
    """transfers save files between devices"""
    pc_dir = Path(config_manager.pc_dir)
    android_dir = Path(config_manager.android_dir)
    filelist = config_manager.filelist

    for savefile in filelist:
        backup_file(source, savefile)

        print(f"moving {savefile} to {destination}...")

        if destination == "computer":  # phone to computer
            android_savefile_path = android_dir / savefile
            command = [
                str(ADB_EXE),
                "pull",
                android_savefile_path.as_posix(),
                str(pc_dir),
            ]

            config_manager.write_config("Files", "last_transfer", "phonetopc")

        elif destination == "phone":  # computer to phone
            pc_savefile_path = pc_dir / savefile
            command = [
                str(ADB_EXE),
                "push",
                str(pc_savefile_path),
                android_dir.as_posix(),
            ]

            config_manager.write_config("Files", "last_transfer", "pctophone")
        else:
            print("invalid source")
            break

        result = subprocess_run(command)

        if result.returncode != 0:
            print(f"couldnt transfer {savefile}. return code: {result.returncode}")
            print(result.stderr)
            config_manager.write_config("Files", "last_transfer", "None")
            print("all other files have been skipped")
            break

    return result


def download_adb():
    if os.name == "nt":
        url = (
            "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
        )
        adb_files = ["adb.exe", "AdbWinUsbApi.dll", "AdbWinApi.dll", "NOTICE.txt"]

    elif sys.platform == "linux":
        url = "https://dl.google.com/android/repository/platform-tools-latest-linux.zip"
        adb_files = ["adb", "NOTICE.txt"]

    elif sys.platform == "darwin":
        url = (
            "https://dl.google.com/android/repository/platform-tools-latest-darwin.zip"
        )
        adb_files = ["adb", "NOTICE.txt"]
    else:
        sys.exit(1)

    # download platform-tools
    print("downloading platform-tools from " + url)
    path_platform_tools = path_current_directory / "platform-tools.zip"
    urlretrieve(url, str(path_platform_tools))
    print("platform-tools downloaded")

    # extract necessary adb files
    # (couldnt figure out a better way to do this im sorry)

    print("extracting adb files")

    def extract(file_name: str):
        with ZipFile(str(path_platform_tools), "r") as platformtools:
            for file in platformtools.namelist():
                if file.endswith(file_name):
                    platformtools.extract(file, path=path_current_directory)
                    break

    for file in adb_files:
        extract(file)

    # rename platform-tools folder to adb
    os.rename(path_current_directory / "platform-tools", path_current_directory / "adb")

    # remove platform-tools.zip now that we dont need it
    os.remove(path_current_directory / "platform-tools.zip")
    print("removed platform-tools.zip")


if __name__ == "__main__":
    if adb_exists() == 0:
        should_download_adb = input(
            "adb is not installed. do you want to download it? (y/N): "
        )
        if should_download_adb.lower() == "y":
            download_adb()
            ADB_EXE = path_current_directory / "adb" / "adb"
            if os.name == "nt":
                ADB_EXE = ADB_EXE.with_name("adb.exe")
        else:
            sys.exit()

    DST = input("transfer files to: (phone/computer): ").strip().lower()
    SRC = "phone" if DST == "computer" else "computer"

    transfer_saves(SRC, DST)
