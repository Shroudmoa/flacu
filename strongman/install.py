import os
import stat
import json
import subprocess
import requests
from check import check_reachability, get_ipv4_addresses
def fix_iptables_order():
    path = "/etc/init.d/iptables"
    if os.path.exists(path):
        with open(path, "r") as f:
            data = f.read()
        if "need net" not in data:
            data = data.replace(
                "#!/sbin/openrc-run",
                "#!/sbin/openrc-run\n\ndepend() {\n    need net\n}\n"
            )
            with open(path, "w") as f:
                f.write(data)
def installTiManService() -> bool:
    service_file = "/etc/init.d/strongman"
    strongman_bin_path = "/usr/local/bin/strongman"
    downloadStrongman_url = "https://vm-tiaas.visionmaxx.net/ti-gw/timan/strongman.bin"
    if os.path.exists(service_file) and os.path.exists(strongman_bin_path):
        print("strongman is already installed")
        return False
    print("Installing strongman...")
    downloadResponse = requests.get(downloadStrongman_url)
    if downloadResponse.status_code == 200:
        with open(strongman_bin_path, "wb") as file:
            file.write(downloadResponse.content)
        os.chmod(strongman_bin_path, 0o755)
    else:
        print("download of strongman failed")
        return False
    service = """#!/sbin/openrc-run
name="Strongman VPN Manager"
description="Flask-based VPN Configuration Manager"
command="/usr/local/bin/strongman"
command_background="yes"
pidfile="/run/strongman.pid"
respawn_delay=5
respawn_max=0
output_log="/var/log/strongman.log"
error_log="/var/log/strongman.err"
"""
    with open(service_file, "w") as f:
        f.write(service)
    os.chmod(service_file, stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
    print("strongman installed successfully. - http://theip:5000")
    return True
def setup_vpn(vpn_json: str, local_net: str, target_ip: str, child: str) -> str:
    """Setup VPN from JSON config (s2sstrong)"""
    output_lines = []
    try:
        data = json.loads(vpn_json)
    except json.JSONDecodeError:
        return "FEHLER: Invalid JSON"
    output_lines.append(" Konfiguriere VPN...")
    params = {item['name']: item['value'] for item in data['parameters']}
    tunnel_ip = params.get('localTunnelIp', '10.0.0.1')
    p1_proposals = "aes256-sha512-x25519"
    p2_proposals = "aes256-sha512-x25519"
    local_id = params.get('localId')
    peer_id = params.get('peerId')
    swanctl_conf = f"""connections {{
    vpn_connection {{
        proposals = {p1_proposals}
        unique = no
        aggressive = no
        version = {params.get('ikeVersion', '2')}
        mobike = no
        remote_addrs = {params['remoteGatewayIp']}
        encap = yes
        dpd_delay = {params.get('dpdRetryInterval', '60')}
        dpd_timeout = {int(params.get('dpdRetryInterval', '60')) * int(params.get('dpdRetryCount', '3'))}
        send_certreq = no
        local-{local_id} {{
            round = 0
            auth = psk
            id = {local_id}
        }}
        remote-{peer_id} {{
            round = 0
            auth = psk
            id = {peer_id}
        }}
        children {{
            {child}_1 {{
                esp_proposals = {p2_proposals}
                sha256_96 = no
                start_action = start
                close_action = start
                dpd_action = start
                mode = tunnel
                policies = yes
                local_ts = {local_net}
                remote_ts = {params['hskVkonNet']}
                rekey_time = {params.get('p2KeyLifetime', '43200')}
            }}
            {child}_2 {{
                esp_proposals = {p2_proposals}
                sha256_96 = no
                start_action = start
                close_action = start
                dpd_action = start
                mode = tunnel
                policies = yes
                local_ts = {tunnel_ip}/32
                remote_ts = {params['openFdNet']}
                rekey_time = {params.get('p2KeyLifetime', '43200')}
            }}
        }}
    }}
}}
pools {{
}}
secrets {{
    ike-vpn {{
        id-0 = {local_id}
        id-1 = {peer_id}
        secret = {params['pskSec']}
    }}
}}
"""
    # Health check
    allsafe = f"""#!/bin/sh
TARGET="{target_ip}"
MAXDOWN=300
if ping -c 3 -W 2 $TARGET > /dev/null 2>&1; then
    rm -f /tmp/vpn_fail_time
    exit 0
fi
FAIL_TIME=$(cat /tmp/vpn_fail_time 2>/dev/null)
if [ -z "$FAIL_TIME" ]; then
    date +%s > /tmp/vpn_fail_time
    exit 0
fi
NOW=$(date +%s)
DIFF=$((NOW - FAIL_TIME))
if [ $DIFF -ge $MAXDOWN ]; then
    doas rc-service charon restart
    sleep 2
    rm -f /tmp/vpn_fail_time
fi
"""
    config_path = "/etc/swanctl/conf.d/ti-gw.conf"
    health_check_path = "/root/check_vpn.sh"
    # Write config
    with open("ti-gw.conf.tmp", "w") as f:
        f.write(swanctl_conf)
    subprocess.run(["doas", "cp", "ti-gw.conf.tmp", config_path], check=False)
    subprocess.run(["doas", "chown", "root:root", config_path], check=False)
    subprocess.run(["doas", "chmod", "644", config_path], check=False)
    os.remove("ti-gw.conf.tmp")
    output_lines.append(f"{config_path}")
    # Write health check
    with open(health_check_path, "w") as f:
        f.write(allsafe)
    subprocess.run(["chmod", "+x", health_check_path], check=False)
    output_lines.append(f"{health_check_path}")
    # Sysctl
    result = subprocess.run(["doas", "cat", "/etc/sysctl.conf"], capture_output=True, text=True)
    content = result.stdout if result.returncode == 0 else ""
    if "net.ipv4.ip_forward" in content:
        new_content = ""
        for line in content.split("\n"):
            if line.startswith("net.ipv4.ip_forward"):
                new_content += "net.ipv4.ip_forward = 1\n"
            else:
                new_content += line + "\n" if line else ""
    else:
        new_content = content + "net.ipv4.ip_forward = 1\n"
    with open("sysctl.conf.tmp", "w") as f:
        f.write(new_content)
    subprocess.run(["doas", "cp", "sysctl.conf.tmp", "/etc/sysctl.conf"], check=False)
    os.remove("sysctl.conf.tmp")
    subprocess.run(["doas", "sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    result = subprocess.run(["cat", "/proc/sys/net/ipv4/ip_forward"], capture_output=True, text=True)
    ip_forward_value = result.stdout.strip()
    output_lines.append(f"net.ipv4.ip_forward = {ip_forward_value}")
        # iptables
    subprocess.run(["doas", "iptables", "-t", "nat", "-A", "POSTROUTING", "-s", local_net, "-d", params['openFdNet'], "-j", "SNAT", "--to-source", tunnel_ip], check=False)
    rules = subprocess.check_output(["iptables-save"], text=True)
    subprocess.run(["doas", "mkdir", "-p", "/etc/iptables"], check=False)
    subprocess.run(["doas", "tee", "/etc/iptables/rules-save"], input=rules, text=True, stdout=subprocess.DEVNULL)
    fix_iptables_order()
    subprocess.run(["doas", "rc-update", "add", "iptables", "default"], check=False)
    # Cron
    result = subprocess.run(["doas", "crontab", "-l"], capture_output=True, text=True)
    existing_cron = result.stdout if result.returncode == 0 else ""
    if health_check_path not in existing_cron:
        new_cron = existing_cron + f"* * * * * {health_check_path}\n" if existing_cron else f"* * * * * {health_check_path}\n"
        with open("crontab.tmp", "w") as f:
            f.write(new_cron)
        subprocess.run(["doas", "crontab", "crontab.tmp"], check=False)
        os.remove("crontab.tmp")
        output_lines.append("Health check cron added")
    # Load config
    subprocess.run(["doas", "swanctl", "--load-all"], check=False)
    output_lines.append("swanctl config loaded")
    output_lines.append("\n" + "$"*70)
    output_lines.append("VPN Setup Complete")
    return "\n".join(output_lines)
def setup_mode(vpn_json: str, local_net: str, target_ip: str, child_name: str) -> str:
    output_lines = []
    if not vpn_json or not local_net or not target_ip or not child_name:
        return "FEHLER: All parameters required (JSON, LE, IP, Child)"
    output_lines.append(" Starting VPN setup...")
    output_lines.append(setup_vpn(vpn_json, local_net, target_ip, child_name))
    ip_info = get_ipv4_addresses()
    output_lines.append(ip_info)
    output_lines.append("Setup mode finished\n")
    return "\n".join(output_lines)
