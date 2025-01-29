"""turns GDDT into an executable and does other stuff"""

import sys
import os
import subprocess
from pathlib import Path
import shutil
from urllib.request import urlretrieve
from zipfile import ZipFile


# paths
path_current_directory = Path(__file__).parent
path_gddt = path_current_directory / 'src' / 'gddt-gui.py'
path_config = path_current_directory / 'settings-sample.ini'
working_directory = Path.cwd()
path_dist = working_directory / 'dist'

def create_bundle():
    command = [
        "pyinstaller",
        "--onefile",
        str(path_gddt)
        ]

    result = subprocess.run(command, check=False)
    print(result)

def copy_config():
    if not os.path.exists(path_dist): # not sure if this will always work so
        print("\ncouldnt find dist directory because im stupid. please do everything else manually")
        sys.exit(1)
    else:
        shutil.copy(path_config, path_dist / 'settings.ini')
    
    print("copied config to" + str(path_dist / 'settings.ini'))

def download_adb():
    if os.name == "nt":
        url = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
        adb_exe = "adb.exe"
    else:
        # im sorry macos
        url = "https://dl.google.com/android/repository/platform-tools-latest-linux.zip"
        adb_exe = "adb"

    # download platform-tools
    print("downloading platform-tools from " + url)
    path_platform_tools = path_dist / 'platform-tools.zip'
    urlretrieve(url, str(path_platform_tools))
    print("platform-tools downloaded")

    # extract adb executable from zip file
    with ZipFile(str(path_platform_tools), 'r') as platformtools:
        for file in platformtools.namelist():
            if file.endswith(adb_exe):
                platformtools.extract(file, path=path_dist)
                break

    # rename platform-tools folder to adb
    shutil.move(path_dist / 'platform-tools', path_dist / 'adb')

    # remove platform-tools.zip now that we dont need it
    os.remove(path_dist / 'platform-tools.zip')

create_bundle()
copy_config()
download_adb()
