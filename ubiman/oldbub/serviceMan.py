import subprocess


# raw output
def stop_service(service_name="ti-gw-secunet") -> str:
    try:
        result = subprocess.run(
            ["sudo", "systemctl", "stop", service_name],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "Error: Command timed out"
    except Exception as e:
        return f"Error: {str(e)}"


def start_service(service_name="ti-gw-secunet") -> str:
    try:
        result = subprocess.run(
            ["sudo", "systemctl", "start", service_name],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "Error: Command timed out"
    except Exception as e:
        return f"Error: {str(e)}"


def restart_service(service_name="ti-gw-secunet") -> str:
    try:
        result = subprocess.run(
            ["sudo", "systemctl", "restart", service_name],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "Error: Command timed out"
    except Exception as e:
        return f"Error: {str(e)}"


def service_status(service_name="ti-gw-secunet") -> str:
    try:
        result = subprocess.run(
            ["sudo", "systemctl", "status", service_name],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "Error: Command timed out"
    except Exception as e:
        return f"Error: {str(e)}"


def is_service_active(service_name="ti-gw-secunet") -> bool:
    try:
        result = subprocess.run(
            ["sudo", "systemctl", "is-active", "--quiet", service_name],
            timeout=5,
            check=False,
        )
        return result.returncode == 0
    except Exception:
        return False



