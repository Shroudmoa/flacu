import os
import subprocess
CONFIG_FILE = "/etc/swanctl/conf.d/ti-gw.conf"
def uninstall():
    try:
        subprocess.run(
            [ "rm", "-f", CONFIG_FILE],
            capture_output=True,
            text=True,
            check=True,
        )
        subprocess.run(
            [ "iptables", "-t", "nat", "-F"],
            capture_output=True,
            text=True,
            check=True,
        )
        return f"Deleted {CONFIG_FILE}\nFlushed iptables NAT table"
    except subprocess.CalledProcessError as e:
        return f"Failed: {e.stderr or e}"
