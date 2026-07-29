import os
import stat
import subprocess
from download import download_token, install_gateway
import requests
from check import check_reachability, get_ipv4_addresses
import shutil



def installTiManService() -> bool:
    service_file = "/etc/init.d/timan"
    timan_bin_path = "/usr/local/bin/timan"
    downloadTiman_url = "https://vm-tiaas.visionmaxx.net/ti-gw/timan/timan.bin"
    backup = "/usr/local/bin/timan.backup"

    if (
        os.path.exists(service_file)
        and os.path.exists(timan_bin_path)
        and os.path.exists(backup)
    ):
        print("Timan is already installed")
        return False


    print("Installing TiMan...")
    # run("apk update")
    # run("apk add curl iproute2 nano vim")
    # run(f"curl -L -o {timan_bin_path} {downloadTiman_url}")
    downloadResponse = requests.get(downloadTiman_url)

    if downloadResponse.status_code == 200:
        with open(timan_bin_path, "wb") as file:
            file.write(downloadResponse.content)

        os.chmod(timan_bin_path, 0o755)

        if not os.path.exists(backup):
            shutil.copy2(
                timan_bin_path,
                backup
            )
            os.chmod(backup, 0o755)

    else:
        print("Download of timan failed")
        return False

    
    result = subprocess.run(
        ["crontab", "-l"],
        capture_output=True,
        text=True
    )

    existing = result.stdout if result.returncode == 0 else ""

    job = "0 3 1 * * /usr/local/bin/timan.backup --update >/var/log/timan-update.log 2>&1"

    if job not in existing:

        with open("/tmp/crontab.tmp", "w") as f:
            if existing:
                f.write(existing.rstrip() + "\n")
            f.write(job + "\n")

        subprocess.run(["crontab", "/tmp/crontab.tmp"])
        os.remove("/tmp/crontab.tmp")
    print("Cron job for monthly update added.")



    service = """#!/sbin/openrc-run

name="TiMan Dashboard"
description="Flask-based VM TiMan Gateway Manager"

command="/usr/local/bin/timan"
command_background="yes"
pidfile="/run/timan.pid"

respawn_delay=5
respawn_max=0

output_log="/var/log/timan.log"
error_log="/var/log/timan.err"
"""

    with open(service_file, "w") as f:
        f.write(service)
    os.chmod(service_file, stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
    print("TiMan installed successfully. - http://theip:5000")
    return True


# main setup
def setup_mode(kundennummer) -> str:
    output_lines: str = ""
    if not check_reachability():
        output_lines = (
            "FEHLER: wl-ti-gateway-nutzerportal-pu.wlcle.org wurde nicht erreicht!\n"
        )
        return output_lines
    if not kundennummer:
        output_lines += "FEHLER: Kundennummer erforderlich\n"
        return output_lines

    output_lines += f"Kundennummer: {kundennummer}\n"
    if not download_token(kundennummer):
        output_lines += "Token Download fehlgeschlagen\n"
        return output_lines
    # output_lines += "Token erfolgreich heruntergeladen\n"
    code, _, err = install_gateway(kundennummer)
    if code != 0 or err != "":
        output_lines += err
        return output_lines
    # change_password_output = change_vm_password(kundennummer)
    # output_lines.append(change_password_output)
    # output_lines.append(out if out else err)
    # while True:

    ip_info = get_ipv4_addresses()
    output_lines += ip_info
    output_lines += "Installation erfolgreich durchgeführt\n"
    return output_lines
