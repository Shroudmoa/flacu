from flask import Flask 
from flask import render_template_string
from flask import request
from flask import redirect
from flask import url_for
from flask import session
import subprocess

app = Flask(__name__)
app.secret_key = "supersecret123"  # session secret key 

USERNAME = "vm"
PASSWORD = "vm"

#main HTML template with background and styling
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
        button:hover {
            background-color: #330047;
        }
        pre {
            background-color: rgba(0, 0, 0, 1);
            padding: 15px;
            border-radius: 5px;
            text-align: left;
            max-width: 1200px;
            margin: 20px auto;
            overflow-x: auto;
        }
        input {padding: 10px; font-size: 16px; border-radius: 5px;}
                /* Watermark top-left */
        .watermark {
            position: fixed;
            top: 20px;
            left: 20px;
            width: 40px;
            height: 40px;
            opacity: 1;
            z-index: 9999;
        }
        

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

    </form>
    <pre>{{ output }}</pre>
{% endif %}
</body>
</html>
"""

ALLOWED_COMMANDS = {
    "ipconfig": ["ipconfig"],
    "stop_anydesk": ["powershell", "Stop-Service", "-Name", "AnyDesk"],
    "start_anydesk": ["powershell", "Start-Service", "-Name", "AnyDesk"],
    "get_services_anydesk": ["powershell", "Get-Service", "-Name", "AnyDesk"],
    "Route Print": ["powershell", "Route", "Print" ],
    "pwd": ["powershell", "Get-Location"]
}

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

    return render_template_string(HTML_TEMPLATE, output=output)

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
    app.run(debug=True,  host="0.0.0.0", port=5000)