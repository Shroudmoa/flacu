import requests
from shellCmd import run_cmd
import os
def download_token(kundennummer: str) -> bool:
    # ftp_url = "https://vm-tiaas.visionmaxx.net"
    tocken_path = "/home/vm/token"
    url = f"https://vm-tiaas.visionmaxx.net/ti-gw/tokens/{kundennummer}/token_{kundennummer}"
    try:
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            print("download vom Token nicht möglich")
            return False
        with open(tocken_path, "wb") as f:
            f.write(response.content)
        return True
    except requests.exceptions.RequestException as e:
        print(str(e))
        return False
# main setup command - rip vm-ti-gw-helper btw
def install_gateway(kundennummer: str) -> tuple[int, str, str]:
    if kundennummer == "":
        return (-1, "error", "kundernummer ist nicht angegeben worden")
    tigwDownloadUrl = (
        "https://wl-ti-gateway-nutzerportal-pu.wlcle.org/ccp/connectivity-repo/files/client-installer-linux/default/latest"
    )
    download_token(kundennummer)
    response = requests.get(tigwDownloadUrl)
    if response.status_code != 200:
        print("ti-gw installer download failed")
        return (-1, "error", "failed download")
    tig_installer_path = "/home/vm/ti-gw-installer-linux.run"
    with open(tig_installer_path, "wb") as f:
        f.write(response.content)
    os.chmod(tig_installer_path, 0o755)
    tocken_path = "/home/vm/token"
    cmd = f"""sudo /home/vm/ti-gw-installer-linux.run --serviceName ti-gw-secunet --prefix /home/vm/tigw --base64String "$(cat {tocken_path})" --clientType device --installermode normal --enable-components clientService,gatewayMode --mode unattended --updateTimeslot 22,Europe/Berlin"""
    return run_cmd(cmd)
