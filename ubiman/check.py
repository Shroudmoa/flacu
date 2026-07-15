import socket
import subprocess
import requests
from shellCmd import run_cmd
import concurrent.futures
# custom
def test_custom(ip, port) -> str:
    try:
        sock = socket.create_connection((ip, int(port)), timeout=5)
        sock.close()
        return f"OK     Verbindung zu {ip}:{port}"
    except Exception as e:
        return f"ERROR  Verbindung zu {ip}:{port} -> {e}"
# keep
def getips() -> list[str]:
    ips = []
    code, out, err = run_cmd("ip -4 addr show")
    if code != 0:
        return ips
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("inet "):
            ip = line.split()[1].split("/")[0]
            ips.append(ip)
    return ips
# keep, also used in monitoring mode
def get_ipv4_addresses() -> str:
    output_lines = []
    output_lines.append("IPv4 Adressen:")
    code, out, err = run_cmd("ip -4 addr show")
    if code != 0:
        output_lines.append(f"Fehler beim Abrufen der IPs: {err}")
        return "\n".join(output_lines)
    found = False
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("inet "):
            ip = line.split()[1].split("/")[0]
            output_lines.append(f" - {ip}")
            found = True
    if not found:
        output_lines.append("Keine IPv4 Adresse gefunden")
    return "\n".join(output_lines)
# keep, also used in monitoring mode
def test_connection() -> str:
    results = []
    tigw_sockets = [
        ("100.102.8.6", 465),
        ("100.102.8.13", 8443),
        ("100.102.30.4", 443),
    ]
    for ip, port in tigw_sockets:
        try:
            sock = socket.create_connection((ip, port), timeout=5)
            sock.close()
            results.append(f"OK     Verbindung zu {ip}:{port}")
        except Exception as e:
            results.append(f"ERROR  Verbindung zu {ip}:{port} -> {e}")
    return "\n".join(results)
def check_reachability() -> bool:
    tigw_url = "https://wl-ti-gateway-nutzerportal-pu.wlcle.org"
    tigwResponse = requests.get(tigw_url)
    # code, _, _ = run_cmd(f"curl -Is {tigw_url} --max-time 5")
    return tigwResponse.status_code == 200
# check later might delete
def check_single_port(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        result = s.connect_ex((host, port))
        return port, (result == 0)
    finally:
        s.close()
# needed
def check_ports_socket_parallel(host="127.0.0.1", show_only_problems=False):
    output_lines: str = f"Port Status ({host}):\n"
    PORTS = [4742, 443, 8500, 636, 53, 9500, 8443]
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(lambda p: check_single_port(host, p), PORTS))
    for port, ok in results:
        if ok:
            if not show_only_problems:
                output_lines += f"OK     Port {port} erreichbar\n"
        else:
            output_lines += f"ERROR  Port {port} nicht erreichbar\n"
    return output_lines
# keep - might use it for s2s Moni
def ping_host(host="8.8.8.8"):
    try:
        result = subprocess.run(
            ["ping", "-c", "1", host], capture_output=True, text=True, timeout=5
        )
        return "Reachable" if result.returncode == 0 else "Unreachable"
    except Exception:
        return "Ping failed"
