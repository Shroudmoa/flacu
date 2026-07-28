import hashlib
import os
import shutil
import subprocess
import tempfile
import requests


UPDATE_URL = "https://vm-tiaas.visionmaxx.net/ti-gw/timan/timan_update.json"

timan = "/usr/local/bin/timan"
BACKUP = "/usr/local/bin/timan.backup"

TIMEOUT = 30


def sha256sum(filename):
    h = hashlib.sha256()

    with open(filename, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)

    return h.hexdigest()


def download_file(url):
    tmp = tempfile.NamedTemporaryFile(delete=False)

    with requests.get(
        url,
        stream=True,
        timeout=TIMEOUT
    ) as r:

        r.raise_for_status()

        for chunk in r.iter_content(8192):
            if chunk:
                tmp.write(chunk)

    tmp.close()

    return tmp.name


#new update funktion mit version check 



#from packaging.version import Version
CURRENT_VERSION = "4.0"


def update():

    print("Checking for updates...")

    try:
        r = requests.get(
            UPDATE_URL,
            timeout=TIMEOUT
        )
        r.raise_for_status()

        data = r.json()

    except Exception as e:
        print("Update check failed:", e)
        return

    if not data.get("update", False):
        print("No update available")
        return

    version = data.get("version")
    url = data.get("download")
    checksum = data.get("checksum")

    if not version or not url or not checksum:
        print("Invalid update information")
        return

    if version == CURRENT_VERSION:
        print("Already running version", version)
        return

    print("New version:", version)

    try:

        print("Downloading...")

        new_file = download_file(url)

    except Exception as e:

        print("Download failed:", e)
        return

    print("Checking checksum...")

    local_hash = sha256sum(new_file)

    if local_hash.lower() != checksum.lower():

        print("Checksum mismatch!")
        print("Expected:", checksum)
        print("Got:", local_hash)

        os.remove(new_file)
        return

    print("Stopping timan...")

    subprocess.run(
        [
            "rc-service",
            "timan",
            "stop"
        ],
        check=False
    )

    try:

        print("Installing new binary...")

        shutil.copy2(
            new_file,
            timan
        )

        os.chmod(
            timan,
            0o755
        )

    except Exception as e:

        print("Install failed:", e)

        subprocess.run(
            [
                "rc-service",
                "timan",
                "start"
            ],
            check=False
        )

        return

    finally:

        if os.path.exists(new_file):
            os.remove(new_file)

    print("Starting timan...")

    subprocess.run(
        [
            "rc-service",
            "timan",
            "start"
        ],
        check=False
    )

    print("Update completed:", version)
   
if __name__ == "__main__":
    update()
