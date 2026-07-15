import subprocess
# no output typeshit -we also have run_cmd() with output
def run(cmd):
    subprocess.run(cmd, shell=True, check=True)
# needed for setup and monitoring, also for some system info commands
def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()
