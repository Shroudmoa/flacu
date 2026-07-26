import subprocess
def reboot_machine():
    try:
        subprocess.Popen(
            ["reboot", "-f"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return "Reboot command executed"
    except Exception as e:
        return f"Reboot failed: {str(e)}"
