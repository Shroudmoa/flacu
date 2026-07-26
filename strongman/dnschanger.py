import os
import shutil
import os
RESOLV_FILE = "/etc/resolv.conf"
BACKUP_FILE = "/etc/resolv.conf.backup"
def set_dns(primary, secondary=None):
    if os.path.exists(RESOLV_FILE):
        shutil.copy(RESOLV_FILE, BACKUP_FILE)
    config = f"nameserver {primary}\n"
    if secondary:
        config += f"nameserver {secondary}\n"
    with open(RESOLV_FILE, "w") as f:
        f.write(config)
    return config
    ######################################################################################
RESOLV_FILE = "/etc/resolv.conf"
def get_dns():
    if not os.path.exists(RESOLV_FILE):
        return "resolv.conf not found"
    output = []
    with open(RESOLV_FILE) as f:
        for line in f:
            if line.startswith("nameserver"):
                output.append(line.strip())
    if not output:
        return "No nameserver configured."
    return "\n".join(output)
