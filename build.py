"""
turns GDDT into an executable and does other stuff
"""

import sys
import os
import subprocess
from pathlib import Path
import shutil
from urllib.request import urlretrieve
from zipfile import ZipFile
import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "-a",
    "--archive",
    action="store_true",
    help="Creates an archive of all files in the dist folder",
)
parser.add_argument(
    "-d",
    "--download_adb",
    action="store_true",
    help="Automatically downloads ADB for the current os",
)

args = parser.parse_args()


# paths
path_current_directory = Path(__file__).parent
path_gddt_py = path_current_directory / "src" / "gddt-gui.py"
path_config = path_current_directory / "settings-sample.ini"
working_directory = Path.cwd()
path_dist = working_directory / "dist"


def create_bundle():
    command = ["pyinstaller", "--onefile", "--windowed", str(path_gddt_py)]

    print("creating bundle...")
    result = subprocess.run(command, check=False)
    print(result)


def move_files():
    # copy config
    if not os.path.exists(path_dist):  # not sure if this will always work so
        print(
            "\ncouldnt find dist directory because im stupid. please do everything else manually"
        )
        sys.exit(1)
    else:
        shutil.copy(path_config, path_dist / "settings.ini")

    print("copied config to" + str(path_dist / "settings.ini"))

    # rename gddt-gui to gddt
    executable_name = "gddt-gui"
    new_executable_name = "gddt"

    if os.name == "nt":
        executable_name += ".exe"
        new_executable_name += ".exe"

    os.rename(str(path_dist / executable_name), str(path_dist / new_executable_name))

    # copy icon.png to dist
    shutil.copy(path_current_directory / "assets" / "icon.png", path_dist / "icon.png")
    print("copied icon.png")


def download_adb():
    # adapt url and adb files for each os
    if os.name == "nt":
        url = (
            "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
        )
        adb_files = ["adb.exe", "AdbWinUsbApi.dll", "AdbWinApi.dll"]

    elif sys.platform == "linux":
        url = "https://dl.google.com/android/repository/platform-tools-latest-linux.zip"
        adb_files = ["adb"]

    elif sys.platform == "darwin":
        url = (
            "https://dl.google.com/android/repository/platform-tools-latest-darwin.zip"
        )
        adb_files = ["adb"]
    else:
        sys.exit(1)

    # download platform-tools
    print("downloading platform-tools from " + url)
    path_platform_tools = path_dist / "platform-tools.zip"
    urlretrieve(url, str(path_platform_tools))
    print("platform-tools downloaded")

    # extract necessary adb files
    # (couldnt figure out a better way to do this im sorry)

    print("extracting adb files")

    def extract(file_name: str):
        with ZipFile(str(path_platform_tools), "r") as platformtools:
            for file in platformtools.namelist():
                if file.endswith(file_name):
                    platformtools.extract(file, path=path_dist)
                    break

    for file in adb_files:
        extract(file)

    # rename platform-tools folder to adb
    shutil.move(path_dist / "platform-tools", path_dist / "adb")

    # remove platform-tools.zip now that we dont need it
    os.remove(path_dist / "platform-tools.zip")
    print("removed platform-tools.zip")


def create_archive():
    prefix = "gddt-"

    if os.name == "nt":
        name = f"{prefix}windows"
    elif sys.platform == "linux":
        name = f"{prefix}linux"
    else:
        name = f"{prefix}macos"

    # the archive will be made in the dist parent to avoid compressing itself
    path = path_dist.parent / name

    shutil.make_archive(
        path,
        "zip",
        path_dist,
    )


create_bundle()
move_files()

if args.download_adb:
    download_adb()

if args.archive:
    create_archive()

print("done :D")

if sys.platform == "linux":
    path_adb = path_dist / "adb" / "adb"
    print("please give executable permission for ADB with this command:")
    print(f"chmod +x {path_adb}")
