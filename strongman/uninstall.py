import os

import subprocess





CONFIG_FILE = "/etc/swanctl/conf.d/ti-gw.conf"





def uninstall():

    try:

        result = subprocess.run(

            ["doas", "rm", "-f", CONFIG_FILE],

            capture_output=True,

            text=True,

            check=True,

        )

        return f"Deleted {CONFIG_FILE}"

    except subprocess.CalledProcessError as e:

        return f"Failed to delete {CONFIG_FILE}: {e.stderr or e}"
