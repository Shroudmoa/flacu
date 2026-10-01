import os
import subprocess

TIGW_DIR = "/home/vm/tigw"
UNINSTALL_CLIENT = "/home/vm/tigw/uninstall-client"
ROOT_CRONTAB = "/var/spool/cron/crontabs/root"


def check_installation_status():

    output = []

    # Service
    try:

        service = subprocess.run(
            ["rc-service", "ti-gw-secunet", "status"],
            capture_output=True,
            text=True
        )

        if "started" in service.stdout.lower() or service.returncode == 0:
            output.append("ti-gw-secunet service detected")
        else:
            output.append("ti-gw-secunet service not detected")

    except Exception:

        output.append("ti-gw-secunet service check failed")

    # Directory

    if os.path.exists(TIGW_DIR):
        output.append("/home/vm/tigw detected")
    else:
        output.append("/home/vm/tigw not detected")

    # Installation marker

    if os.path.exists(UNINSTALL_CLIENT):
        output.append("clean installation detected")
    else:
        output.append("clean installation marker NOT detected")

    # RAM

    try:

        mem = subprocess.check_output(
            ["grep", "MemTotal", "/proc/meminfo"],
            text=True
        )

        ram_mb = int(mem.split()[1]) // 1024
        ram_gb = round(ram_mb / 1024)

        output.append(f"RAM: {ram_gb} GB")

    except Exception:

        output.append("RAM detection failed")

    # CPU

    try:

        output.append(f"CPU cores: {os.cpu_count()}")

    except Exception:

        output.append("CPU detection failed")

    # ntpd

    try:

        ntp = subprocess.run(
            ["rc-service", "ntpd", "status"],
            capture_output=True,
            text=True
        )

        if ntp.returncode == 0:
            output.append("ntpd running")
        else:
            output.append("ntpd NOT RUNNING")

    except Exception:

        output.append("ntpd check failed error 303 -- contact the support-team pls")
    # MTU

    try:

        links = subprocess.run(
            ["ip", "-o", "link", "show"],
            capture_output=True,
            text=True
        )

        for line in links.stdout.splitlines():

            if ":" not in line:
                continue

            name = line.split(":")[1].strip()
            name = name.split("@")[0]

            parts = line.split()
            mtu = parts[parts.index("mtu") + 1] if "mtu" in parts else None

            output.append(f"{name}: mtu {mtu if mtu else 'not set'}")

    except Exception:

        output.append("MTU detection failed 303 => contact the support-team pls")

    # Uptime

    try:

        uptime = subprocess.run(
            ["uptime"],
            capture_output=True,
            text=True
        )

        output.append("")
        output.append("uptime")
        output.append(uptime.stdout.strip())

    except Exception:

        output.append("")
        output.append("uptime unavailable")

    # Root crontab

    output.append("")
    output.append("/var/spool/cron/crontabs/root")

    try:

        if os.path.exists(ROOT_CRONTAB):

            with open(ROOT_CRONTAB) as f:

                cron = f.read().strip()

            if cron:
                output.append(cron)
            else:
                output.append("empty")

        else:

            output.append("not found")

    except Exception as e:

        output.append(str(e))

    return "\n".join(output)
