import hashlib
import os
import shutil
import subprocess
import tempfile

import requests


CURRENT_VERSION = "4.0"

UPDATE_URL = "https://vm-tiaas.visionmaxx.net/ti-gw/timan/strong_update.json"

BINARY_PATH = "/usr/local/bin/strongman"
BACKUP_PATH = "/usr/local/bin/strongman.backup"

REQUEST_TIMEOUT = 30 #useless like joe biden



def sha256sum(filename):
    h = hashlib.sha256()

    with open(filename, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)

    return h.hexdigest()




def check_update():

    print("Checking for updates...")

    try:
        response = requests.get(UPDATE_URL, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()

    except Exception as e:
        return f"Could not read update information:\n{e}"

    if not data.get("update", False):
        return "No update available."

    remote_version = data.get("version", "")
    download_url = data.get("download", "")
    expected_hash = data.get("checksum", "").lower()

    if remote_version == CURRENT_VERSION:
        return f"Already running latest version ({CURRENT_VERSION})"

    print(f"Downloading version {remote_version}...")

    try:

        with tempfile.NamedTemporaryFile(delete=False) as tmp:

            tmp_name = tmp.name

            r = requests.get(download_url, stream=True, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()

            for chunk in r.iter_content(8192):
                if chunk:
                    tmp.write(chunk)

    except Exception as e:
        return f"Download failed:\n{e}"

    print("Verifying checksum...")

    calculated = sha256sum(tmp_name).lower()

    if calculated != expected_hash:

        os.remove(tmp_name)

        return (
            "Checksum mismatch!\n\n"
            f"Expected : {expected_hash}\n"
            f"Received : {calculated}"
        )

    print("Installing update...")

    try:

        if os.path.exists(BINARY_PATH):
            shutil.copy2(BINARY_PATH, BACKUP_PATH)

        shutil.copy2(tmp_name, BINARY_PATH)

        os.chmod(BINARY_PATH, 0o755)

        os.remove(tmp_name)

    except Exception as e:
        return f"Installation failed:\n{e}"

    print("Restarting service...")

    subprocess.run(
        ["rc-service", "strongman", "restart"],
        check=False
    )

    return f"Update to {remote_version} installed successfully."
