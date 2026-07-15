import os
import subprocess
UNINSTALL_SCRIPT = "/home/vm/tigw/uninstall-client"
def uninstall():
    output = []
    if not os.path.exists(UNINSTALL_SCRIPT):
        return "uninstall_client not found"
    try:
        subprocess.run(
            ["chmod", "+x", UNINSTALL_SCRIPT],
            check=True
        )
        output.append(
            "chmod +x /home/vm/tigw/uninstall-client completed"
        )
        result = subprocess.run(
            [UNINSTALL_SCRIPT],
            capture_output=True,
            text=True
        )
        output.append("Uninstall script executed")
        if result.stdout:
            output.append(result.stdout)
        if result.stderr:
            output.append(result.stderr)
    except Exception as e:
        output.append(f"Uninstall failed: {str(e)}")
    return "\n".join(output)
