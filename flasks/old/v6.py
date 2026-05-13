#!/usr/bin/env python3
import subprocess
import os
import sys
import signal
import time
from flask import Flask, render_template_string, request, redirect, url_for, session
import threading


app = Flask(__name__)
app.secret_key = "supersecret123"

USERNAME = "vm"
PASSWORD = "vm"

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(SCRIPT_DIR, "static")

# Create static directory if it doesn't exist
os.makedirs(STATIC_DIR, exist_ok=True)

HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>VM Dashboard</title>
    <link rel="icon" href="{{ url_for('static', filename='vm.jpg') }}" type="image/x-icon">
    <style>
        body {
            font-family: Arial, sans-serif;
            background: url('{{ url_for('static', filename='background.jpg') }}') no-repeat center center fixed;
            background-size: cover;
            background-color: #000000;
            color: white;
            text-align: center;
            padding-top: 50px;
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
        }
        button:hover { background-color: #330047; }
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
        }
        .watermark { 
            position: fixed; 
            top: 20px; 
            left: 20px; 
            width: 40px; 
            height: 40px; 
            opacity: 1; 
            z-index: 9999; 
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
        }
        .up { 
            color: #28a745; 
            font-weight: bold; 
        }
        .down { 
            color: #dc3545; 
            font-weight: bold; 
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
        h1 {
            margin-bottom: 30px;
        }
        .section-title {
            margin-top: 40px;
            font-size: 18px;
            font-weight: bold;
            color: #28a745;
        }
    </style>
</head>
<body>
    <img src="{{ url_for('static', filename='vm.jpg') }}" class="watermark" alt="Watermark">
{% if not session.get("logged_in") %}
    <h2>Login Ti Manager</h2>
    <form method="post" action="{{ url_for('login') }}">
        <div class="input-group">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </div>
    </form>
{% else %}

<h1>TI Manager Visionmaxx GmbH</h1>

<div class="section-title">System Information</div>
<div class="button-group">
    <form method="post" style="display: inline;">
        <button name="command" value="ipconfig">Show IP Config</button>
    </form>
    <form method="post" style="display: inline;">
        <button name="command" value="port-check">Check Ports</button>
    </form>
    <form method="post" style="display: inline;">
        <button name="command" value="connection-test">Test Connection</button>
    </form>
    <form method="post" style="display: inline;">
        <button name="command" value="pwd">Show Current Directory</button>
    </form>
</div>

<div class="section-title">Service Management</div>
<div class="button-group">
    <form method="post" style="display: inline;">
        <button name="command" value="stop_anydesk">Stop AnyDesk</button>
    </form>
    <form method="post" style="display: inline;">
        <button name="command" value="start_anydesk">Start AnyDesk</button>
    </form>
    <form method="post" style="display: inline;">
        <button name="command" value="get_services_anydesk">Get AnyDesk Services</button>
    </form>
</div>

<div class="section-title">TI Gateway Operations</div>
<div class="button-group">
    <form method="post" style="display: inline;">
        <button name="command" value="monitoring">Run Monitoring</button>
    </form>
    <form method="post" style="display: inline;">
        <button name="command" value="show-logs">Show Logs</button>
    </form>
    <form method="post" style="display: inline;">
        <button name="command" value="route-print">Show Routing Table</button>
    </form>
</div>

<div class="section-title">Setup & Configuration</div>
<div class="input-group">
    <form method="post" style="display: block;">
        <input type="text" name="kundennummer" placeholder="Enter Kundennummer (customer number)" required>
        <button type="submit" name="command" value="setup">Start Setup</button>
    </form>
</div>

<div class="section-title">Account</div>
<div class="button-group">
    <form method="post" style="display: inline;">
        <button name="command" value="logout" style="background-color: #dc3545;">Logout</button>
    </form>
</div>

{% if output %}
<div class="section-title">Output</div>
<pre>{{ output }}</pre>
{% endif %}

<div class="dashboard">
    <div class="card">
        <h3>Machine IPs</h3>
        <pre>{{ machine_ips }}</pre>
    </div>
    <div class="card">
        <h3>Ping 8.8.8.8</h3>
        <p>Status: <span class="{{ 'up' if ping_status=='Reachable' else 'down' }}">{{ ping_status }}</span></p>
    </div>
    <div class="card">
        <h3>Service Status</h3>
        <p>Status: <span class="{{ 'up' if service_status_value=='Running' else 'down' }}">{{ service_status_value }}</span></p>
    </div>
</div>

{% endif %}
</body>
</html>
"""


ALLOWED_COMMANDS = {
    "ipconfig": ["vm-ti-gw-helper", "ipconfig"],
    "port-check": ["vm-ti-gw-helper", "port-check"],
    "connection-test": ["vm-ti-gw-helper", "connection-test"],
    "monitoring": ["vm-ti-gw-helper", "monitoring"],
    "show-logs": ["vm-ti-gw-helper", "logs"],
    "setup": ["vm-ti-gw-helper", "setup"],
    "stop_anydesk": ["sudo", "rc-service", "nginx", "stop"],
    "start_anydesk": ["sudo", "rc-service", "nginx", "start"],
    "get_services_anydesk": ["sudo", "rc-service", "nginx", "status"],
    "route-print": ["ip", "route"],
    "pwd": ["pwd"],
}


def get_machine_ips():
    try:
        result = subprocess.run(["ip", "addr"], capture_output=True, text=True, timeout=5)
        return result.stdout if result.stdout else "No IP information available"
    except Exception as e:
        return f"Error retrieving IPs: {str(e)}"


def ping_host(host="8.8.8.8"):
    try:
        result = subprocess.run(["ping", "-c", "1", host], capture_output=True, text=True, timeout=5)
        return "Reachable" if result.returncode == 0 else "Unreachable"
    except Exception:
        return "Ping failed"


def service_status(service_name="nginx"):
    try:
        result = subprocess.run(["sudo", "rc-service", service_name, "status"], capture_output=True, text=True, timeout=5)
        if "started" in result.stdout.lower() or result.returncode == 0:
            return "Running"
        else:
            return "Stopped"
    except Exception:
        return "Unknown"


def run_binary_command(cmd_list, kundennummer=None):
    """
    Execute a binary command with optional parameters
    """
    try:
        # Handle setup command with kundennummer
        if len(cmd_list) > 0 and cmd_list[0] == "vm-ti-gw-helper":
            if len(cmd_list) > 1 and cmd_list[1] == "setup":
                if not kundennummer or kundennummer.strip() == "":
                    return "Error: Kundennummer is required for setup"
                # Build command properly
                cmd_list = ["vm-ti-gw-helper", "setup", "--kundennummer", str(kundennummer).strip()]

        result = subprocess.run(
            cmd_list,
            capture_output=True,
            text=True,
            timeout=60,
            check=False
        )
        
        output = result.stdout if result.stdout else result.stderr
        return output if output else "Command executed successfully (no output)"
    
    except subprocess.TimeoutExpired:
        return "Error: Command timed out (took longer than 60 seconds)"
    except FileNotFoundError as e:
        return f"Error: Command not found - {str(e)}. Make sure vm-ti-gw-helper is in /usr/local/bin/"
    except PermissionError:
        return "Error: Permission denied. Setup may require sudo."
    except Exception as e:
        return f"Error: {str(e)}"


@app.route("/", methods=["GET", "POST"])
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    output = ""

    if request.method == "POST":
        cmd_key = request.form.get("command")
        kundennummer = request.form.get("kundennummer", "").strip()

        if cmd_key == "logout":
            session.pop("logged_in", None)
            return redirect(url_for("login"))

        # Special handling for setup command
        if cmd_key == "setup":
            if not kundennummer:
                output = "Error: Kundennummer is required for setup"
            else:
                cmd_list = ["vm-ti-gw-helper", "setup", "--kundennummer", kundennummer]
                output = run_binary_command(cmd_list)
        
        elif cmd_key in ALLOWED_COMMANDS:
            cmd_list = ALLOWED_COMMANDS[cmd_key]
            # Check if it's a binary command (starts with vm-ti-gw-helper)
            if cmd_list and cmd_list[0] == "vm-ti-gw-helper":
                output = run_binary_command(cmd_list.copy())
            else:
                # Regular system commands
                try:
                    result = subprocess.run(
                        cmd_list,
                        capture_output=True,
                        text=True,
                        timeout=10,
                        check=False
                    )
                    output = result.stdout if result.stdout else result.stderr
                except subprocess.TimeoutExpired:
                    output = "Error: Command timed out"
                except Exception as e:
                    output = f"Error: {str(e)}"
        else:
            output = "Invalid command"

    machine_ips = get_machine_ips()
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


def signal_handler(sig, frame):
    """Handle graceful shutdown"""
    print("\nShutting down Flask application...")
    sys.exit(0)


def run_flask():
    """Run Flask in a thread"""
    app.run(debug=False, host="0.0.0.0", port=5000, threaded=True)


if __name__ == "__main__":
    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("Starting TI Manager Dashboard...")
    print("Access at: http://0.0.0.0:5000")
    print("Username: vm")
    print("Password: vm")
    print("\nPress Ctrl+C to stop the application")
    
    # Run Flask
    run_flask()
