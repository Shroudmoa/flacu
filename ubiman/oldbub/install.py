import os
import stat
import subprocess
import requests

from download import download_token, install_gateway
from check import check_reachability, get_ipv4_addresses


def installTiManService() -> bool:
    service_file = "/etc/systemd/system/timan.service"
    timan_bin_path = "/usr/local/bin/timan"
    downloadTiman_url = "https://vm-tiaas.visionmaxx.net/ti-gw/timan/timan.bin"

    if os.path.exists(service_file) and os.path.exists(timan_bin_path):
        print("TiMan is already installed")
        return False

    print("Installing TiMan...")

    # Create destination directory if it does not exist
    os.makedirs("/usr/local/bin", exist_ok=True)

    # Download binary
    downloadResponse = requests.get(downloadTiman_url)
    if downloadResponse.status_code == 200:
        with open(timan_bin_path, "wb") as file:
            file.write(downloadResponse.content)
        os.chmod(timan_bin_path, 0o755)
    else:
        print("Download of TiMan failed")
        return False

    # Create systemd service
    service = f"""[Unit]
Description=TiMan Dashboard
After=network.target

[Service]
Type=simple
ExecStart={timan_bin_path}
Restart=always
RestartSec=5
User=root
WorkingDirectory=/usr/local/bin

StandardOutput=append:/var/log/timan.log
StandardError=append:/var/log/timan.err

[Install]
WantedBy=multi-user.target
"""

    with open(service_file, "w") as f:
        f.write(service)

    os.chmod(service_file, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)

    # Reload systemd
    subprocess.run(["systemctl", "daemon-reload"], check=True)

    # Enable service at boot
    subprocess.run(["systemctl", "enable", "timan.service"], check=True)

    # Start service
    subprocess.run(["systemctl", "restart", "timan.service"], check=True)

    print("TiMan installed successfully.")
    print("Service started.")
    print("Open: http://<server-ip>:5000")

    return True


# main setup
def setup_mode(kundennummer) -> str:
    output_lines = ""

    if not check_reachability():
        return (
            "FEHLER: wl-ti-gateway-nutzerportal-pu.wlcle.org wurde nicht erreicht!\n"
        )

    if not kundennummer:
        return "FEHLER: Kundennummer erforderlich\n"

    output_lines += f"Kundennummer: {kundennummer}\n"

    if not download_token(kundennummer):
        output_lines += "Token Download fehlgeschlagen\n"
        return output_lines

    code, _, err = install_gateway(kundennummer)
    if code != 0 or err:
        output_lines += err
        return output_lines

    ip_info = get_ipv4_addresses()
    output_lines += ip_info
    output_lines += "Installation erfolgreich durchgeführt\n"

    return output_lines
