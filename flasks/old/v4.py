from flask import Flask, render_template_string, request, redirect, url_for, session
import subprocess
import os


app = Flask(__name__)
app.secret_key = "supersecret123"  # session secret key 

USERNAME = "vm"
PASSWORD = "vm"


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
        }
        input { padding: 10px; font-size: 16px; border-radius: 5px; }
        .watermark { position: fixed; top: 20px; left: 20px; width: 40px; height: 40px; opacity: 1; z-index: 9999; }
        .dashboard { display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; }
        .card { background-color: rgba(0,0,0,0.6); padding: 20px; border-radius: 10px; min-width: 250px; max-width: 400px; color: white; }
        .up { color: #28a745; font-weight: bold; }
        .down { color: #dc3545; font-weight: bold; }
    </style>
</head>
<body>
    <img src="{{ url_for('static', filename='vm.jpg') }}" class="watermark" alt="Watermark">
{% if not session.get("logged_in") %}
    <h2>Login Ti Manager</h2>
    <form method="post" action="{{ url_for('login') }}">
        <input type="text" name="username" placeholder="Username" required>
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit">Login</button>
    </form>
{% else %}


<h1>TI Manager Visionmaxx GmbH</h1>
<form method="post">
    <button name="command" value="ipconfig">Show IP</button>
    <button name="command" value="stop_anydesk">Stop AnyDesk</button>
    <button name="command" value="start_anydesk">Start AnyDesk</button>
    <button name="command" value="Route Print">Show Routing Table</button>
    <button name="command" value="pwd">Show Current Directory</button>
    <button name="command" value="get_services_anydesk">Get AnyDesk Services</button>
    <button name="command" value="logout">Logout</button>
    <button name="command" value="vm-ti-gw-helper">Run Helper Script</button>
</form>
<pre>{{ output }}</pre>
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
    "ipconfig": ["ipconfig"] if os.name == "nt" else ["ip", "addr"], ##keep the way so we can make a doas/sudo combination for linux
    "stop_anydesk":  ["sudo", "rc-service", "nginx", "stop"],
    "start_anydesk":  ["sudo", "rc-service", "nginx", "start"],
    "get_services_anydesk":  ["sudo", "rc-service", "nginx", "status"],
    "Route Print": ["ip", "route"],
    "pwd": ["pwd"],
    "vm-ti-gw-helper": ["vm-ti-gw-helper"]
}


def get_machine_ips():
        result = subprocess.run(["ip", "addr"], capture_output=True, text=True)
        return result.stdout

def ping_host(host="8.8.8.8"): # can be the connector
    try:
        result = subprocess.run(["ping", "-c", "1", host], capture_output=True, text=True)
        return "Reachable" if result.returncode == 0 else "Unreachable"
    except Exception:
        return "Ping failed"

def service_status(service_name="nginx"):  #

        result = subprocess.run(["sudo", "rc-service", service_name, "status"], capture_output=True, text=True)
        if "started" in result.stdout:
            return "Running"
        else:
            return "Stopped"

@app.route("/", methods=["GET", "POST"])
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    output = ""

    if request.method == "POST":
        cmd_key = request.form.get("command")
        if cmd_key == "logout":
            session.pop("logged_in", None)
            return redirect(url_for("login"))

        if cmd_key in ALLOWED_COMMANDS:
            try:
                result = subprocess.run(ALLOWED_COMMANDS[cmd_key], capture_output=True, text=True, check=True)
                output = result.stdout
            except subprocess.CalledProcessError as e:
                output = f"Error:\n{e.stderr}"
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
            return render_template_string(HTML_TEMPLATE, output="Invalid credentials")
    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
