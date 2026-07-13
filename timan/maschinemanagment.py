import os

import subprocess

from check import test_connection, check_ports_socket_parallel, getips

import time





# main moni

def monitoring_mode(iterations=1):

    output_lines = []

    for i in range(int(iterations)):

        iteration_output = monitor_single_iteration()

        output_lines.append(iteration_output)

        if i < int(iterations) - 1:

            output_lines.append("\n" + "=" * 50 + "\n")

            time.sleep(10)

    return "\n".join(output_lines)





# kinda messy - might use get ip insteed

def get_machine_ips():

    try:

        result = subprocess.run(

            ["ip", "-ca"], capture_output=True, text=True, timeout=5

        )

        return result.stdout if result.stdout else "No IP information available"

    except Exception as e:

        return f"Error retrieving IPs: {str(e)}"





def get_routing_table() -> str:

    try:

        result = subprocess.run(

            ["ip", "route"], capture_output=True, text=True, timeout=5

        )

        return result.stdout if result.stdout else "No routing information available"

    except Exception as e:

        return f"Error: {str(e)}"





# main monitoring function, also used in monitoring mode, might split up later

# main monitoring function, also used in monitoring mode, might split up later

def monitor_single_iteration() -> str:

    output_lines = []



    ips = getips()

    output_lines.append("IPv4 Adressen:")

    for ip in ips:

        output_lines.append(f" - {ip}")



    output_lines.append("\nRouting Table:")

    output_lines.append(get_routing_table())



    output_lines.append("\nPort Checks:")

    for ip in ips:

        output_lines.append(f"\nChecking {ip}")

        port_output = check_ports_socket_parallel(ip, show_only_problems=True)

        output_lines.append(port_output)



    output_lines.append("\nfachdienstliche Verbindung:")

    conn_test = test_connection()

    output_lines.append(conn_test)



    return "\n".join(output_lines)





# just client log is enough for now

def show_client_log() -> str:

    log_file = "/home/vm/tigw/data/logs/client.log"

    if not os.path.exists(log_file):

        return f"Fehler: {log_file} nicht gefunden"

    try:

        with open(log_file, "r") as f:

            return f.read()

    except Exception as e:

        return f"Fehler beim Lesen der Datei: {str(e)}"





# new test for changing password

def change_vm_password(kundennummer) -> str:

    new_password = f"!tigw{kundennummer}"

    try:

        subprocess.run(

            ["sudo", "chpasswd"], input=f"vm:{new_password}".encode(), check=True

        )

        return "Passwort für 'vm' erfolgreich geändert"

    except subprocess.CalledProcessError as e:

        return f"FEHLER beim Ändern des Passworts: {e}"


