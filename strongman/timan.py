import subprocess
import os
import sys
import signal
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, url_for, session
from reboot import reboot_machine
from usermanager import change_user_password
from install import installTiManService, setup_mode
from ipchanger import status as ip_status, set_static, set_dhcp
from dnschanger import get_dns, set_dns
from installationStatus import check_installation_status
from uninstall import uninstall
from dirty_uninstall import dirty_uninstall
from shellCmd import run
from cronmanager import add_daily_reboot
from sslmanager import ensure_ssl
from maschinemanagment import show_client_log, monitoring_mode
from datetime import datetime
from check import (
    ping_host,
    test_connection,
    get_ipv4_addresses,
    test_custom,
)
from serviceMan import service_status, start_service, stop_service
from updater import check_update
###############################################
app = Flask(__name__)
app.secret_key = "lbBo85tuAguLZgMMAZisKp6q5Cohkjyy8ikYqtWb"
USER = "vm"
PASS = "vm"
ADMIN_PASSWORD = datetime.now().strftime("%m/%d")
cert, key = ensure_ssl()
########################################
# Load HTML template (new one)
if getattr(sys, "frozen", False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))
index_path = os.path.join(base_path, "index.html")
with open(index_path, "r", encoding="utf-8") as f:
    HTML_TEMPLATE = f.read()
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
        elif cmd_key == "install":
            vpn_json = request.form.get("vpn_json")
            local_net = request.form.get("local_net")
            target_ip = request.form.get("target_ip")
            child_name = request.form.get("child_name")
            setup_password = request.form.get("setup_password")
            try:
                if setup_password != ADMIN_PASSWORD:
                    output = "Invalid setup password"
                elif not all([vpn_json, local_net, target_ip, child_name]):
                    output = "All VPN parameters required"
                else:
                    output = setup_mode(
                        vpn_json,
                        local_net,
                        target_ip,
                        child_name
                    )
            except Exception as e:
                import traceback
                traceback.print_exc()
                output = str(e)
        elif cmd_key == "uninstall":
            setup_password = request.form.get("setup_password")
            if setup_password != ADMIN_PASSWORD:
                output = "Invalid setup password"
            else:
                output = uninstall()
        elif cmd_key == "dirty-uninstall":
            setup_password = request.form.get("setup_password")
            if setup_password != ADMIN_PASSWORD:
                output = "Invalid setup password"
            else:
                output = dirty_uninstall()
        elif cmd_key == "installation-status":
            output = check_installation_status()
        elif cmd_key == "monitoring":
            output = monitoring_mode(iterations=1)
        elif cmd_key == "show-logs":
            output = show_client_log()
        elif cmd_key == "ipconfig":
            output = (
                get_ipv4_addresses()
            )
        elif cmd_key == "connection-test":
            output = test_connection()
        elif cmd_key == "stop_service":
            output = stop_service()
        elif cmd_key == "start_service":
            output = start_service()
        elif cmd_key == "ip-config":
            admin_password = request.form.get("admin_password")
            if admin_password != ADMIN_PASSWORD:
                output = "Invalid admin password"
            else:
                ip = request.form.get("ip_address")
                cidr = request.form.get("subnet")
                gateway = request.form.get("gateway")
                if ip and cidr and gateway:
                    output = set_static(ip, cidr, gateway)
                else:
                    output = ip_status()
        elif cmd_key == "dns-config":
            admin_password = request.form.get("admin_password")
            if admin_password != ADMIN_PASSWORD:
                output = "Invalid admin password"
            else:
                dns1 = request.form.get("dns1")
                dns2 = request.form.get("dns2")
                if dns1:
                    output = set_dns(dns1, dns2)
                else:
                    output = get_dns()
        elif cmd_key == "ip-dhcp":
            output = set_dhcp()
        elif cmd_key == "user-manager":
            setup_password = request.form.get("setup_password")
            if setup_password != ADMIN_PASSWORD:
                output = "Invalid setup password"
            else:
                username = request.form.get("username")
                new_password = request.form.get("user_password")
                if not username or not new_password:
                    output = "Username and password required"
                else:
                    output = change_user_password(
                        username,
                        new_password
                            )
        elif cmd_key == "daily-reboot":
            hour = request.form.get("reboot_hour")
            output = add_daily_reboot(hour)
        elif cmd_key == "reboot":
            admin_password = request.form.get("admin_password")
            if admin_password != ADMIN_PASSWORD:
                output = "Invalid admin password"
            else:
                output = reboot_machine()
        elif cmd_key == "custom-connection-test":
            ip = request.form.get("custom_ip")
            port = request.form.get("custom_port")
            output = test_custom(ip, port)
        else:
            output = "Invalid command"
    machine_ips = get_ipv4_addresses()
    ping_status_value = ping_host()
    service_status_value = service_status()
    return render_template_string(
        HTML_TEMPLATE,
        output=output,
        machine_ips=machine_ips,
        ping_status=ping_status_value,
        service_status_value=service_status_value,
    )
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("username")
        pwd = request.form.get("password")
        if user == USER and pwd == PASS:
            session["logged_in"] = True
            return redirect(url_for("index"))
        else:
            return render_template_string(
                HTML_TEMPLATE,
                output="Invalid credentials. Please try again.",
                machine_ips="",
                ping_status="",
                service_status_value="",
            )
    return render_template_string(
        HTML_TEMPLATE,
        output="",
        machine_ips="",
        ping_status="",
        service_status_value="",
    )
def signal_handler(sig, frame):
    print("\nShutting down Flask application...")
    sys.exit(0)
##################################################################################################
def alpine_setup():
    if os.geteuid() != 0:
        return "Please run as root."
    def run(cmd):
        subprocess.run(cmd, shell=True, check=True)
    # Install doas
    run("apk update")
    run("apk add doas")
    # Configure repositories
    with open("/etc/apk/repositories", "w") as f:
        f.write(
            "http://dl-cdn.alpinelinux.org/alpine/edge/main\n"
            "http://dl-cdn.alpinelinux.org/alpine/edge/community\n"
        )
    run("apk update")
    # Install packages
    run("apk add vim nano iptables strongswan")
    run("apk update")
    run("apk add curl iproute2")
    run("apk add git fish strongswan iptables")
    run("rc-update add charon default")
    run("rc-update add crond default")
    run("rc-service crond start")
    # Configure doas
    with open("/etc/doas.conf", "w") as f:
        f.write("permit persist :wheel\n")
    # Create users
    for user in ("vm", "ti-gw"):
        subprocess.run(f"id -u {user}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if subprocess.run(f"id -u {user}", shell=True).returncode != 0:
            run(f"adduser -D {user}")
        run(f"adduser {user} wheel")
    return "Alpine init completed successfully."


if __name__ == "__main__":
    if "--update" in sys.argv: 
        print(check_update())
        sys.exit(0)
    try:
        if installTiManService():
            alpine_setup()
            run("rc-service strongman start")
            run("rc-update add strongman default")
            
            sys.exit(0)
    except Exception as e:
        print("Install failed:", e)
    alpine_setup()
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    sys.stdout.flush()
    app.run(debug=False, host="0.0.0.0", port=5000, threaded=True, ssl_context=(cert, key))
