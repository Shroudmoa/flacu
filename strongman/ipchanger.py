import os
import os
import shutil

INTERFACES_FILE = "/etc/network/interfaces"
BACKUP_FILE = "/etc/network/interfaces.backup"


def backup_interfaces():
    if os.path.exists(INTERFACES_FILE):
        shutil.copy(INTERFACES_FILE, BACKUP_FILE)


def set_static(ip, cidr, gateway):

    backup_interfaces()

    config = f"""auto lo
iface lo inet loopback

auto eth0
iface eth0 inet static
    address {ip}/{cidr}
    gateway {gateway}
"""

    with open(INTERFACES_FILE, "w") as f:
        f.write(config)

    return (
        "Static IP configured\n\n"
        f"IP: {ip}/{cidr}\n"
        f"Gateway: {gateway}\n\n"
        "Reboot to apply."
    )

def set_dhcp():

    backup_interfaces()

    config = """auto lo
iface lo inet loopback

auto eth0
iface eth0 inet dhcp
"""

    with open(INTERFACES_FILE, "w") as f:
        f.write(config)

    return "DHCP enabled. Reboot pls"
    subprocess.run(
        ["rc-service", "networking", "restart"],
        capture_output=True,
        text=True
    )

   ##############################################################################################
INTERFACES_FILE = "/etc/network/interfaces"


def get_eth0_config():
    if not os.path.exists(INTERFACES_FILE):
        return "Interface file not found."

    with open(INTERFACES_FILE, "r") as f:
        lines = f.readlines()

    eth0 = []
    inside = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("iface eth0"):
            inside = True

        elif inside and stripped.startswith("iface "):
            break

        if inside:
            eth0.append(line.rstrip())

    if not eth0:
        return "eth0 configuration not found."

    return "\n".join(eth0)


def is_dhcp():
    cfg = get_eth0_config()

    if "iface eth0 inet dhcp" in cfg:
        return True

    return False


def status():
    output = []

    output.append("::Current config::")
    output.append(get_eth0_config())
    output.append("")

    if is_dhcp():
        output.append("Mode : DHCP")
    else:
        output.append("Mode : STATIC")

    return "\n".join(output)
