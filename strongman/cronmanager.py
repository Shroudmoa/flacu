import os
CRON_FILE = "/var/spool/cron/crontabs/root"
CRON_COMMAND = "/sbin/reboot -f"
def add_daily_reboot(hour):
    try:
        hour = int(hour)
        if hour < 0 or hour > 23:
            return "Hour must be between 0 and 23."
    except ValueError:
        return "Invalid hour."
    lines = []
    if os.path.exists(CRON_FILE):
        with open(CRON_FILE, "r") as f:
            lines = f.readlines()
    # Alte reboot -f Jobs entfernen
    lines = [
        line for line in lines
        if CRON_COMMAND not in line
    ]
    lines.append(f"0 {hour} * * * {CRON_COMMAND}\n")
    with open(CRON_FILE, "w") as f:
        f.writelines(lines)
    return f"Daily reboot scheduled at {hour:02d}:00."
