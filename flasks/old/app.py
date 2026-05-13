from flask import Flask
#from flask import render
from flask import request
from flask import render_template_string
import subprocess

app = Flask(__name__)

# HTML-Template
HTML_TEMPLATE = """
<!doctype html>
<title>Server Command Executor</title>
<h1>Führe Befehl aus</h1>
<form method="post">
  <select name="command">
    <option value="ipconfig">ipconfig</option>
    <option value="stop_anydesk">Stop AnyDesk</option>
    <option value="start_anydesk">Start AnyDesk</option>
  </select>
  <input type="submit" value="Ausführen">
</form>
<pre>{{ output }}</pre>
"""

# Mapping der erlaubten Befehle
ALLOWED_COMMANDS = {
    "ipconfig": ["ipconfig"],
    "stop_anydesk": ["powershell", "Stop-Service", "-Name", "AnyDesk"],
    "start_anydesk": ["powershell", "Start-Service", "-Name", "AnyDesk"]
}

@app.route("/", methods=["GET", "POST"])
def index():
    output = ""
    if request.method == "POST":
        cmd_key = request.form.get("command")
        if cmd_key in ALLOWED_COMMANDS:
            try:
                result = subprocess.run(ALLOWED_COMMANDS[cmd_key], capture_output=True, text=True, check=True)
                output = result.stdout
            except subprocess.CalledProcessError as e:
                output = f"Fehler:\n{e.stderr}"
        else:
            output = "Ungültiger Befehl"
    return render_template_string(HTML_TEMPLATE, output=output)

if __name__ == "__main__":
    app.run(debug=True)