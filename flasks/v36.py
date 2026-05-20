#!/usr/bin/env python3
import subprocess
import os
import sys
import signal
import socket
from threading import Thread
import time
import concurrent.futures
from flask import Flask, render_template_string, request, redirect, url_for, session
import shutil
import requests

###############################################################################
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(SCRIPT_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)
background_src = resource_path("strict/background.jpg")
background_dst = os.path.join(STATIC_DIR, "background.jpg")
if os.path.exists(background_src):
    shutil.copy(background_src, background_dst)
logo_src = resource_path("strict/vm.jpg")
logo_dst = os.path.join(STATIC_DIR, "vm.jpg")
if os.path.exists(logo_src):
    shutil.copy(logo_src, logo_dst)
##########################################################################################
app = Flask(__name__)
app.secret_key = "supersecret123"
USERNAME = "vm"
PASSWORD = "vm"
# we can change this later
BASE_URL = "https://vm-tiaas.visionmaxx.net"
BASE_URL2 = "https://wl-ti-gateway-nutzerportal-pu.wlcle.org"
TOKEN_PATH = "/home/vm/token"
PORTS = [4742, 443, 8500, 636, 53, 9500, 8443]
TEST_TARGETS = [
    ("100.102.8.6", 465),
    ("100.102.8.13", 8443),
    ("100.102.30.4", 443),
]


LOG_FILE = "/home/vm/tigw/data/logs/client.log"
############ kinda not in use -- gotta check somthing before deleting
TEST_IPS = [
    "100.102.8.6",
    "100.102.8.13",
    "100.102.30.4",
]
TEST_PORT = 465
##########################################################################################


HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>VM TiMan</title>
    <link rel="icon" href="{{ url_for('static', filename='vm.jpg') }}" type="image/x-icon">
    <style>
        html {
            scroll-behavior: smooth;
        }
        body {
            font-family: Arial, sans-serif;
            background-color: #000000;
            color: white;
            text-align: center;
            padding-top: 50px;
            margin: 0;
            overflow-x: hidden;
        }
        .background-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-size: cover;
            background-position: center center;
            background-repeat: no-repeat;
            z-index: -1;
            opacity: 1;
            transition: opacity 1.5s ease-in-out;
        }
        .background-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, rgba(0,0,0,0.3) 0%, rgba(29,0,41,0.5) 100%);
            z-index: 0;
        }
        .background-container.fade-out {
            opacity: 0;
        }
        button {
            padding: 15px 25px;
            margin: 10px;
            font-size: 16px;
            cursor: pointer;
            border-radius: 5px;
            border: none;
            background-color: #1d0029;
            color: white;
            transition: all 0.3s ease;
        }
        button:hover {
            background-color: #330047;
            box-shadow: 0 0 15px rgba(255,0,150,0.5);
            transform: translateY(-2px);
        }
        button:active {
            transform: translateY(0px);
        }
        pre {
            background-color: rgba(0, 0, 0, 1);
            padding: 15px;
            border-radius: 5px;
            text-align: left;
            max-width: 1200px;
            margin: 20px auto;
            overflow-x: auto;
            font-size: 12px;
            line-height: 1.4;
        }
        input { 
            padding: 10px; 
            font-size: 16px; 
            border-radius: 5px;
            margin: 5px;
            border: 1px solid #1d0029;
            background-color: rgba(255,255,255,0.1);
            color: white;
            transition: all 0.3s ease;
        }
        input::placeholder {
            color: rgba(255,255,255,0.5);
        }
        input:focus {
            outline: none;
            background-color: rgba(255,255,255,0.15);
            box-shadow: 0 0 10px rgba(255,0,150,0.3);
        }
        .watermark { 
            position: fixed; 
            top: 20px; 
            left: 20px; 
            width: 50px; 
            height: 50px; 
            opacity: 0.8; 
            z-index: 9999;
            animation: float 3s ease-in-out infinite;
        }
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }
        .dashboard { 
            display: flex; 
            flex-wrap: wrap; 
            justify-content: center; 
            gap: 20px; 
            margin-top: 30px;
        }
        .card { 
            background-color: rgba(0,0,0,0.6); 
            padding: 20px; 
            border-radius: 10px; 
            min-width: 250px; 
            max-width: 400px; 
            color: white;
            transition: all 0.3s ease;
            border-left: 3px solid transparent;
        }
        .card:hover {
            background-color: rgba(0,0,0,0.8);
            border-left-color: #ff0150;
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(255,0,150,0.3);
        }
        .up { 
            color: #00ff00; 
            font-weight: bold;
            text-shadow: 0 0 10px rgba(0,255,0,0.5);
        }
        .down { 
            color: #ff0000; 
            font-weight: bold;
            text-shadow: 0 0 10px rgba(255,0,0,0.5);
        }
        .status-dot {
            width: 12px;
            height: 12px;
            background-color: #00ff00;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .button-group {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 10px;
            margin: 20px 0;
        }
        .input-group {
            margin: 20px 0;
            padding: 20px;
            background-color: rgba(0,0,0,0.3);
            border-radius: 10px;
            display: inline-block;
        }
        .input-group input {
            width: 300px;
            padding: 12px;
            font-size: 16px;
            border-radius: 5px;
            border: 1px solid #1d0029;
            background-color: rgba(255,255,255,0.1);
            color: white;
            margin: 10px 5px;
        }
        .input-group input::placeholder {
            color: rgba(255,255,255,0.5);
        }
        .input-group button {
            padding: 12px 20px;
            margin: 10px 5px;
        }

        .dropdown-wrapper {
            position: relative;
            width: 320px;
        }

        .dropdown-selected {
            background-color: rgba(255,255,255,0.1);
            color: white;
            border: 1px solid #1d0029;
            padding: 12px;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s ease;
            user-select: none;
        }

        .dropdown-selected:hover {
            background-color: rgba(255,255,255,0.15);
            box-shadow: 0 0 10px rgba(255,0,150,0.3);
        }

        .dropdown-menu {
            display: none;
            position: absolute;
            top: 105%;
            left: 0;
            width: 100%;
            background-color: rgba(0,0,0,0.95);
            border: 1px solid #1d0029;
            border-radius: 5px;
            overflow: hidden;
            z-index: 9999;
            box-shadow: 0 0 20px rgba(255,0,150,0.2);
        }
        .command-row {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            flex-wrap: wrap;
        }

        .dropdown-item {
            padding: 12px;
            color: white;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .dropdown-item:hover {
            background-color: rgba(255,0,150,0.2);
        }
        
        h1 {
            margin-bottom: 30px;
            text-shadow: 0 0 20px rgba(255,0,150,0.3);
        }
        h2 {
            text-shadow: 0 0 15px rgba(255,0,150,0.2);
        }
        .section-title {
            margin-top: 40px;
            font-size: 18px;
            font-weight: bold;
            color: #e0e0e0;
            padding-bottom: 10px;
        }
        @media (max-width: 768px) {
            button {
                padding: 12px 18px;
                font-size: 14px;
            }
            .input-group input {
                width: 250px;
            }
            h1 {
                font-size: 24px;
            }
            .card {
                min-width: 220px;
                max-width: 350px;
            }
        }
    </style>
</head>
<body>
    <div class="background-container"></div>
    <img src="{{ url_for('static', filename='vm.jpg') }}" class="watermark" alt="Watermark">
{% if not session.get("logged_in") %}
    <h2>Login TiMan</h2>
    <form method="post" action="{{ url_for('login') }}">
        <div class="input-group">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </div>
    </form>
{% else %}
<h1 style="color: white;"><span class="status-dot"></span>TiMan Visionmaxx GmbH</h1>
<div class="section-title">Service Management</div>
<div class="button-group">
    <form method="post" style="display: inline;">
        <button name="command" value="stop_service">Stop ti-gw-secunet</button>
    </form>
    <form method="post" style="display: inline;">
        <button name="command" value="start_service">Start ti-gw-secunet</button>
    </form>
    <form method="post" style="display: inline;">
        <button name="command" value="get_service_status">Status ti-gw-secunet</button>
    </form>
</div>

<div class="section-title">
    Command Center
</div>

<div class="input-group">

    <div class="command-row">

        <div class="dropdown-wrapper">

            <div class="dropdown-selected"
                 onclick="toggleDropdown()">

                Select Command ▼

            </div>

            <div class="dropdown-menu"
                 id="dropdownMenu">

                <div class="dropdown-item"
                     onclick="selectCommand('ipconfig', 'Download Installer.run')">

                    Download Installer.run

                </div>

                <div class="dropdown-item"
                     onclick="selectCommand('connection-test', 'Test Mailserver')">

                    Test Mailserver

                </div>
                <div class="dropdown-item"
                    onclick="selectCommand('custom-connection-test', 'Custom Connection Test')">

                    Custom Connection Test

                </div>


                <div class="dropdown-item"
                     onclick="selectCommand('pwd', 'Current Directory')">

                    Current Directory

                </div>


                <div class="dropdown-item"
                     onclick="selectCommand('monitoring', 'Helper-Monitoring')">

                    Helper-Monitoring

                </div>

                <div class="dropdown-item"
                     onclick="selectCommand('show-logs', 'Client Log')">

                    Client Log

                </div>

                <div class="dropdown-item"
                     onclick="selectCommand('route-print', 'Routing Table')">

                    Routing Table

                </div>

            </div>

        </div>
        <div id="customTestFields"
            style="display:none; margin-top:15px;">

            <input type="text"
                name="custom_ip"
                form="commandForm"
                placeholder="IP Address">

            <input type="number"
                name="custom_port"
                form="commandForm"
                placeholder="Port">

        </div>


        <form method="post"
              id="commandForm"
              style="margin: 0;">

            <input type="hidden"
                   name="command"
                   id="commandInput">

            <button type="submit">
                Execute Command
            </button>

        </form>

    </div>

</div>


<div class="section-title">Setup & Configuration</div>
<div class="input-group">
    <form method="post" action="{{ url_for('index') }}" style="display: block;">
        <input type="text" name="kundennummer" placeholder="Enter Kundennummer" required>
        <button type="submit" name="command" value="setup">Start Setup</button>
    </form>
</div>

{% if output %}
<div class="section-title">Output</div>
<pre>{{ output }}</pre>
{% endif %}
<div class="dashboard">
    <div class="card">
        <h3><span class="status-dot"></span>Machine IPs</h3>
        <pre>{{ machine_ips }}</pre>
    </div>
    <div class="card">
        <h3><span class="status-dot"></span>Ping 8.8.8.8</h3>
        <p>Status: <span class="{{ 'up' if ping_status=='Reachable' else 'down' }}">{{ ping_status }}</span></p>
    </div>
    <div class="card">
        <h3>ti-gw-secunet</h3>
        <p>Status: <span class="{{ 'up' if service_status_value=='Running' else 'down' }}">{{ service_status_value }}</span></p>
    </div>
</div>
<div class="section-title">Account</div>
<div class="button-group">
    <form method="post" style="display: inline;">
        <button name="command" value="logout" style="background-color: #a61d2a;">Logout</button>
    </form>
</div>
{% endif %}
<script>

function toggleDropdown() {
    const menu = document.getElementById("dropdownMenu");
    menu.style.display = menu.style.display === "block" ? "none" : "block";
}

function selectCommand(value, label) {

    document.getElementById("commandInput").value = value;

    document.querySelector(".dropdown-selected").innerText = label;

    document.getElementById("dropdownMenu").style.display = "none";

    const customFields = document.getElementById("customTestFields");

    if (value === "custom-connection-test") {
        customFields.style.display = "block";
    } else {
        customFields.style.display = "none";
    }
}


document.addEventListener("click", function(e) {
    if (!e.target.closest(".dropdown-wrapper")) {
        document.getElementById("dropdownMenu").style.display = "none";
    }
});

</script>

    <script>
        const bgContainer = document.querySelector('.background-container');
        async function updateBackground() {
            try {
                const response = await fetch('/get-background');
                const data = await response.json();
                const newBg = `{{ url_for('static', filename='') }}${data.background}`;
                // Fade out
                bgContainer.classList.add('fade-out');
                // Wait for fade out, then change image and fade in
                setTimeout(() => {
                    bgContainer.style.backgroundImage = `url('${newBg}')`;
                    bgContainer.classList.remove('fade-out');
                }, 1500); // Half of the transition time
            } catch (error) {
                console.error('Failed to update background:', error);
            }
        }
        // Update background every ... 
        setInterval(updateBackground, 20000); // 20 seconds 
        // Set initial background
        updateBackground();
        // Add visual feedback on form submission
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', function() {
                const buttons = this.querySelectorAll('button[type="submit"]');
                buttons.forEach(btn => {
                    btn.style.opacity = '0.7';
                });
            });
        });
    </script>
</body>
</html>
"""
##############testphase 2 - V21: ############################################################################
current_bg_index = 0
backgrounds = [
    'background.jpg',
    'background6.jpg',
    'v3.jpg',
    'v5.jpg',
    'v4.jpg',
    '20.jpg'
]
def rotate_background():
    global current_bg_index
    while True:
        time.sleep(19) #kinda useless if the other one is 15 seconds
        current_bg_index = (current_bg_index + 1) % len(backgrounds)
bg_thread = Thread(target=rotate_background, daemon=True)
bg_thread.start()
@app.route('/get-background')
def get_background():
    return {'background': backgrounds[current_bg_index]} #also kinda useless
################# v20 : ######################################################################################

#needed for setup and monitoring, also for some system info commands
def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()
def check_reachability():
    code, _, _ = run_cmd(f"curl -Is {BASE_URL2} --max-time 5")
    return code == 0
def download_token(kundennummer):
    url = f"{BASE_URL}/ti-gw/tokens/{kundennummer}/token_{kundennummer}"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(TOKEN_PATH, 'wb') as f:
            f.write(response.content)
        
        return True
    except requests.exceptions.RequestException as e:
        print(str(e))
        return False

#check later might delete 
def check_single_port(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        result = s.connect_ex((host, port))
        return port, (result == 0)
    finally:
        s.close()
#needed
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
#main setup command - rip vm-ti-gw-helper btw
def install_gateway(kundennummer):
    cmd = f"""sudo /home/vm/ti-gw-installer-linux.run --serviceName ti-gw-secunet --prefix /home/vm/tigw --base64String "$(cat {TOKEN_PATH})" --clientType device --installermode normal --enable-components clientService,gatewayMode --mode unattended --updateTimeslot 22,Europe/Berlin"""
    return run_cmd(cmd)
####test phase2#########################################
INSTALLER_PATH = "/home/vm/ti-gw-installer-linux.run"
INSTALLER_URL = "https://vm-tiaas.visionmaxx.net/ti-gw/installer/ti-gw-installer-linux.run"
'''
def download_gateway_installer():
    if os.path.exists(INSTALLER_PATH):
        return "Installer already exists"

    result = subprocess.run([
        "curl",
        "-L",
        "-s",
        INSTALLER_URL,
        "-o",
        INSTALLER_PATH,
    ])

    if result.returncode != 0:
        return "Download failed"

    os.chmod(INSTALLER_PATH, 0o755)

    return "Installer downloaded"   
'''
def download_gateway_installer():
    if os.path.exists(INSTALLER_PATH):
        return "Installer already exists"
    
    try:
        response = requests.get(INSTALLER_URL, timeout=30, stream=True)
        response.raise_for_status()
        
        with open(INSTALLER_PATH, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        os.chmod(INSTALLER_PATH, 0o755)
        return "Installer downloaded"
    
    except requests.exceptions.RequestException as e:
        return f"Download failed: {str(e)}"

########################################################
#keep 
def getips():
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
#keep, also used in monitoring mode
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
#keep, also used in monitoring mode     
def test_connection():
    results = []

    for ip, port in TEST_TARGETS:
        try:
            sock = socket.create_connection((ip, port), timeout=5)
            sock.close()
            results.append(f"OK     Verbindung zu {ip}:{port}")
        except Exception as e:
            results.append(f"ERROR  Verbindung zu {ip}:{port} -> {e}")

    return "\n".join(results)

#custom 
def test_custom(ip, port):
    try:
        sock = socket.create_connection((ip, int(port)), timeout=5)
        sock.close()
        return f"OK     Verbindung zu {ip}:{port}"
    except Exception as e:
        return f"ERROR  Verbindung zu {ip}:{port} -> {e}"
#main monitoring function, also used in monitoring mode, might split up later
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
#just client log is enough for now
def show_client_log():
    if not os.path.exists(LOG_FILE):
        return f"Fehler: {LOG_FILE} nicht gefunden"
    try:
        with open(LOG_FILE, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Fehler beim Lesen der Datei: {str(e)}"
#new test for changing password 
def change_vm_password(kundennummer):
    new_password = f"!tigw{kundennummer}"
    try:
        subprocess.run(
            ["sudo", "chpasswd"],
            input=f"vm:{new_password}".encode(),
            check=True
        )
        return f"Passwort für 'vm' erfolgreich geändert"
    except subprocess.CalledProcessError as e:
        return f"FEHLER beim Ändern des Passworts: {e}"
    
#main setup

def setup_mode(kundennummer):
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
    code, out, err = install_gateway(kundennummer)
    change_password_output = change_vm_password(kundennummer)
    output_lines.append(change_password_output)
    output_lines.append(out if out else err)
    time.sleep(5)  #kurze Pause damit der Dienst Zeit hat zu starten
    ip_info = get_ipv4_addresses()
    output_lines.append(ip_info)
    return "\n".join(output_lines)

#main moni
def monitoring_mode(iterations=1):
    output_lines = []
    for i in range(int(iterations)):
        iteration_output = monitor_single_iteration()
        output_lines.append(iteration_output)
        if i < int(iterations) - 1:
            output_lines.append("\n" + "="*50 + "\n")
            time.sleep(10)
    return "\n".join(output_lines)

#kinda messy - might use get ip insteed
def get_machine_ips():
    try:
        result = subprocess.run(["ip", "addr"], capture_output=True, text=True, timeout=5)
        return result.stdout if result.stdout else "No IP information available"
    except Exception as e:
        return f"Error retrieving IPs: {str(e)}"
#keep - might use it for s2s Moni
def ping_host(host="8.8.8.8"):
    try:
        result = subprocess.run(["ping", "-c", "1", host], capture_output=True, text=True, timeout=5)
        return "Reachable" if result.returncode == 0 else "Unreachable"
    except Exception:
        return "Ping failed"
#raw output 
def stop_service(service_name="ti-gw-secunet"):
    try:
        result = subprocess.run(
            ["sudo", "rc-service", service_name, "stop"], 
            capture_output=True, 
            text=True, 
            timeout=10,
            check=False
        )
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "Error: Command timed out"
    except Exception as e:
        return f"Error: {str(e)}"
def start_service(service_name="ti-gw-secunet"):
    try:
        result = subprocess.run(
            ["sudo", "rc-service", service_name, "start"], 
            capture_output=True, 
            text=True, 
            timeout=10,
            check=False
        )
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "Error: Command timed out"
    except Exception as e:
        return f"Error: {str(e)}"
def service_status(service_name="ti-gw-secunet"):
    try:
        result = subprocess.run(
            ["sudo", "rc-service", service_name, "status"], 
            capture_output=True, 
            text=True, 
            timeout=5,
            check=False
        )
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error: {str(e)}"
def get_routing_table():
    try:
        result = subprocess.run(["ip", "route"], capture_output=True, text=True, timeout=5)
        return result.stdout if result.stdout else "No routing information available"
    except Exception as e:
        return f"Error: {str(e)}"
#didnt know that can be useful but it is..keep for Supporting phase so we can see if timan is running as a Service or not
def get_pwd():
    try:
        result = subprocess.run(["pwd"], capture_output=True, text=True, timeout=5)
        return result.stdout if result.stdout else "Current directory not found"
    except Exception as e:
        return f"Error: {str(e)}"
    






#login is like only 20 lines and the it-guy cant play around or talk SH about the timan security  
@app.route("/", methods=["GET", "POST"])
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    #v2 type :
    output = ""
    if request.method == "POST":
        cmd_key = request.form.get("command")
        kundennummer = request.form.get("kundennummer", None)
        if cmd_key == "logout":
            session.pop("logged_in", None)
            return redirect(url_for("login"))
        elif cmd_key == "setup":
            if not kundennummer:
                output = "Error: Kundennummer is required for setup"
            else:
                output = setup_mode(kundennummer)
        elif cmd_key == "monitoring":
            output = monitoring_mode(iterations=1)
        elif cmd_key == "show-logs":
            output = show_client_log()
        elif cmd_key == "ipconfig":
            output = download_gateway_installer()  #################flaw - wrong name chnage later pls. #ciel
        elif cmd_key == "connection-test":
            output = test_connection()
        elif cmd_key == "pwd":
            output = get_pwd()
        elif cmd_key == "stop_service":
            output = stop_service()
        elif cmd_key == "start_service":
            output = start_service()
        elif cmd_key == "get_service_status":
            output = service_status()
        elif cmd_key == "route-print":
            output = get_routing_table()
        elif cmd_key == "custom-connection-test":

            ip = request.form.get("custom_ip")
            port = request.form.get("custom_port")

            output = test_custom(ip, port)

        else:
            output = "Invalid command"
    machine_ips = get_ipv4_addresses()  #get_machine_ips()
    ping_status_value = ping_host()
    service_status_value = service_status()
    return render_template_string(
        HTML_TEMPLATE,
        output=output,
        machine_ips=machine_ips,
        ping_status=ping_status_value,
        service_status_value=service_status_value
    )



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")        
        if username == USERNAME and password == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("index"))
        else:
            return render_template_string(
                HTML_TEMPLATE, 
                output="Invalid credentials. Please try again.",
                machine_ips="",
                ping_status="",
                service_status_value=""
            )
    return render_template_string(
        HTML_TEMPLATE,
        output="",
        machine_ips="",
        ping_status="",
        service_status_value=""
    )



#useless for now but might be useful later for graceful shutdown...
def signal_handler(sig, frame):
    print("\nShutting down Flask application...")
    sys.exit(0)


#port 5000 and 0.0.0.0 for LE and threaded for better performance - debug false for security reasons 
if __name__ == "__main__":
    sys.stdout.flush()    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    sys.stdout.flush()
    app.run(debug=False, host="0.0.0.0", port=5000, threaded=True)
