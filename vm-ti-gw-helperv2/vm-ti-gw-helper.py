#!/usr/bin/env python3
import subprocess
import os
import time
import socket
import concurrent.futures
import sys
import argparse


BASE_URL = "https://vm-tiaas.visionmaxx.net"
BASE_URL2 = "https://wl-ti-gateway-nutzerportal-pu.wlcle.org"
TOKEN_PATH = "./token"
PORTS = [4742, 443, 8500, 636, 53, 9500]
TEST_IP = "100.102.8.6"
TEST_PORT = 465


def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def check_reachability():
    print("wl-ti-gateway-nutzerportal-pu.wlcle.org erreicht...")
    code, _, _ = run_cmd(f"curl -Is {BASE_URL2} --max-time 5")
    return code == 0


def download_token(kundennummer):
    url = f"{BASE_URL}/ti-gw/tokens/{kundennummer}/token_{kundennummer}"
    print(f"Lade Token von {url}")
    code, _, err = run_cmd(f"curl -f -L {url} -o {TOKEN_PATH}")
    if code != 0:
        print(err)
    return code == 0


def check_single_port(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        result = s.connect_ex((host, port))
        return port, (result == 0)
    finally:
        s.close()


def check_ports_socket_parallel(host="127.0.0.1", show_only_problems=False):
    output_lines = []
    output_lines.append(f"Port Status ({host}):")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(lambda p: check_single_port(host, p), PORTS))

    for port, ok in results:
        if ok:
            if not show_only_problems:
                output_lines.append(f"OK     Port {port} erreichbar")
        else:
            output_lines.append(f"ERROR  Port {port} nicht erreichbar")

    return "\n".join(output_lines)


def install_gateway():
    print("Starte Installation...")
    cmd = """sudo ./ti-gw-installer-linux.run \
--serviceName ti-gw-secunet \
--prefix /home/vm/tigw \
--base64String $(cat ./55ytoken) \
--clientType device \
--installermode normal \
--enable-components clientService,gatewayMode \
--mode unattended \
--updateTimeslot 22,Europe/Berlin"""
    return run_cmd(cmd)


def getips():
    ips = []
    code, out, err = run_cmd("ip -4 addr show")

    if code != 0:
        print("Fehler beim Abrufen der IPs:", err)
        return ips

    for line in out.splitlines():
        line = line.strip()
        if line.startswith("inet "):
            ip = line.split()[1].split("/")[0]
            ips.append(ip)

    return ips


def get_ipv4_addresses():
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


def test_connection():
    try:
        sock = socket.create_connection((TEST_IP, TEST_PORT), timeout=5)
        sock.close()
        return f"OK     Verbindung zu {TEST_IP}:{TEST_PORT}"
    except Exception:
        return f"ERROR  Verbindung zu {TEST_IP}:{TEST_PORT}"


def monitor_single_iteration():
    output_lines = []
    
    ips = getips()

    output_lines.append("IPv4 Adressen:")
    for ip in ips:
        output_lines.append(f" - {ip}")

    output_lines.append("\nPort Checks:")

    for ip in ips:
        output_lines.append(f"\nChecking {ip}")
        port_output = check_ports_socket_parallel(ip, show_only_problems=True)
        output_lines.append(port_output)
    
    output_lines.append("\nfachdienstliche Verbindung:")
    conn_test = test_connection()
    output_lines.append(conn_test)

    return "\n".join(output_lines)


def show_logs():
    log_dir = "/home/vm/tigw/data/logs/"
    if not os.path.exists(log_dir):
        return f"Fehler: {log_dir} nicht gefunden"

    files = os.listdir(log_dir)
    output_lines = []
    output_lines.append("Verfügbare Log-Dateien:")
    
    for i, f in enumerate(files):
        output_lines.append(f"{i}: {f}")

    return "\n".join(output_lines)


def show_log_content(log_index):
    log_dir = "/home/vm/tigw/data/logs/"
    if not os.path.exists(log_dir):
        return f"Fehler: {log_dir} nicht gefunden"

    files = os.listdir(log_dir)
    
    try:
        file_index = int(log_index)
        if 0 <= file_index < len(files):
            file = files[file_index]
            file_path = os.path.join(log_dir, file)
            with open(file_path, 'r') as f:
                return f.read()
        else:
            return "Ungültige Log-Datei-Nummer"
    except ValueError:
        return "Ungültige Eingabe"
    except Exception as e:
        return f"Fehler beim Lesen der Datei: {str(e)}"


def setup_mode(kundennummer=None):
    output_lines = []
    
    if not check_reachability():
        output_lines.append("FEHLER: wl-ti-gateway-nutzerportal-pu.wlcle.org wurde nicht erreicht!")
        return "\n".join(output_lines)

    if not kundennummer:
        output_lines.append("FEHLER: Kundennummer erforderlich")
        return "\n".join(output_lines)

    output_lines.append(f"Kundennummer: {kundennummer}")

    if not download_token(kundennummer):
        output_lines.append("Token Download fehlgeschlagen")
        return "\n".join(output_lines)

    output_lines.append("Token erfolgreich heruntergeladen")

    code, out, err = install_gateway()
    output_lines.append(out if out else err)

    ip_info = get_ipv4_addresses()
    output_lines.append(ip_info)

    return "\n".join(output_lines)


def monitoring_mode(iterations=1):
    output_lines = []
    
    for i in range(int(iterations)):
        iteration_output = monitor_single_iteration()
        output_lines.append(iteration_output)
        
        if i < int(iterations) - 1:
            output_lines.append("\n" + "="*50 + "\n")
            time.sleep(10)

    return "\n".join(output_lines)


def logs_mode(log_index=None):
    if log_index is None:
        return show_logs()
    else:
        return show_log_content(log_index)


def main():
    parser = argparse.ArgumentParser(description='VM TI Gateway Helper')
    parser.add_argument('mode', 
                       choices=['setup', 'monitoring', 'logs', 'ipconfig', 'port-check', 'connection-test'],
                       help='Operation mode')
    parser.add_argument('--kundennummer', type=str, help='Kundennummer for setup mode')
    parser.add_argument('--iterations', type=int, default=1, help='Number of monitoring iterations')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host IP for port checks')
    parser.add_argument('--log-index', type=int, help='Log file index to display')

    args = parser.parse_args()

    if args.mode == 'setup':
        result = setup_mode(args.kundennummer)
        print(result)
    
    elif args.mode == 'monitoring':
        result = monitoring_mode(args.iterations)
        print(result)
    
    elif args.mode == 'logs':
        result = logs_mode(args.log_index)
        print(result)
    
    elif args.mode == 'ipconfig':
        result = get_ipv4_addresses()
        print(result)
    
    elif args.mode == 'port-check':
        result = check_ports_socket_parallel(args.host)
        print(result)
    
    elif args.mode == 'connection-test':
        result = test_connection()
        print(result)


if __name__ == "__main__":
    main()

