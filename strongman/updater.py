import hashlib
import os
import shutil
import subprocess
import tempfile
import time

import requests


UPDATE_URL = "https://vm-tiaas.visionmaxx.net/ti-gw/timan/strong_update.json"

BINARY_PATH = "/usr/local/bin/strongman"
BACKUP_PATH = "/usr/local/bin/strongman.backup"

UPDATE_SCRIPT = "/tmp/strongman_update.sh"

REQUEST_TIMEOUT = 30


def sha256sum(filename):
    sha = hashlib.sha256()

    with open(filename, "rb") as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            sha.update(data)

    return sha.hexdigest()


def check_update():

    print("Checking for updates...")

    try:
        r = requests.get(
            UPDATE_URL,
            timeout=REQUEST_TIMEOUT
        )
        r.raise_for_status()
        update = r.json()

    except Exception as e:
        return f"Update check failed: {e}"


    if not update.get("update", False):
        return "No update available"


    version = update.get("version")
    url = update.get("download")
    expected_hash = update.get("checksum", "").lower()


    print(f"Downloading version {version}...")


    try:
        tmp = tempfile.NamedTemporaryFile(
            delete=False
        )

        tmp_path = tmp.name

        with requests.get(
            url,
            stream=True,
            timeout=REQUEST_TIMEOUT
        ) as response:

            response.raise_for_status()

            for chunk in response.iter_content(8192):
                if chunk:
                    tmp.write(chunk)

        tmp.close()

    except Exception as e:
        return f"Download failed: {e}"


    print("Verifying checksum...")

    calculated = sha256sum(tmp_path)


    if calculated.lower() != expected_hash:

        os.remove(tmp_path)

        return (
            "Checksum failed\n"
            f"Expected: {expected_hash}\n"
            f"Got:      {calculated}"
        )


    print("Stopping service...")

    subprocess.run(
        [
            "rc-service",
            "strongman",
            "stop"
        ],
        check=False
    )


    create_update_script(tmp_path)


    subprocess.Popen(
        [
            UPDATE_SCRIPT
        ],
        start_new_session=True
    )


    return (
        f"Update to {version} prepared.\n"
        "Updater will replace binary and restart service."
    )


def create_update_script(new_binary):

    script = f"""#!/bin/sh

sleep 3

echo "Installing new strongman binary"

if [ -f "{BINARY_PATH}" ]; then
    cp "{BINARY_PATH}" "{BACKUP_PATH}"
fi

cp "{new_binary}" "{BINARY_PATH}"

chmod 755 "{BINARY_PATH}"

rm -f "{new_binary}"

echo "Starting service"

rc-service strongman start

rm -f "$0"

"""


    with open(
        UPDATE_SCRIPT,
        "w"
    ) as f:
        f.write(script)


    os.chmod(
        UPDATE_SCRIPT,
        0o755
    )