import subprocess


# raw output
def stop_service(service_name="charon") -> str:
    try:
        result = subprocess.run(
            ["rc-service", service_name, "stop"],
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


def start_service(service_name="charon") -> str:
    try:
        result = subprocess.run(
            ["rc-service", service_name, "start"],
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


def service_status(service_name="charon") -> str:
    try:
        result = subprocess.run(
            ["rc-service", service_name, "status"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error: {str(e)}"
