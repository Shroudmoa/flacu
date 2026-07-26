import os
import subprocess
from shellCmd import run_cmd
TIGW_DIR = "/etc/swanctl/conf.d/ti-gw.conf"
UNINSTALL_CLIENT = "/etc/swanctl/conf.d/ti-gw.conf" # change later
ROOT_CRONTAB = "/var/spool/cron/crontabs/root"
def check_installation_status():
    output = []
    # Service
    try:
        service = subprocess.run(
            ["rc-service", "charon", "status"],
            capture_output=True,
            text=True
        )
        if "started" in service.stdout.lower() or service.returncode == 0:
            output.append("charon service detected")
        else:
            output.append("charon service not detected")
    except Exception:
        output.append("charon service check failed")
    # Directory
    if os.path.exists(TIGW_DIR):
        output.append("/etc/swanctl/conf.d/ti-gw.conf detected")
    else:
        output.append("/etc/swanctl/conf.d/ti-gw.conf not detected")
    # Installation marker
    if os.path.exists(UNINSTALL_CLIENT):
        output.append("clean installation detected")
    else:
        output.append("clean installation marker not detected")
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
    # ti-gw.conf content
    output.append("")
    output.append("/etc/swanctl/conf.d/ti-gw.conf")
    try:
        if os.path.exists(TIGW_DIR):
            with open(TIGW_DIR) as f:
                config = f.read().strip()
            if config:
                output.append(config)
            else:
                output.append("empty")
        else:
            output.append("not found")
    except Exception as e:
        output.append(str(e))
    output.append("")
    _, stdout, stderr = run_cmd("iptables -t nat -L -n --line-numbers")
    output.append(stdout or stderr)
    return "\n".join(output)
