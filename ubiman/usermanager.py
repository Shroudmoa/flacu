import subprocess
def user_exists(username):
    result = subprocess.run(
        ["id", username],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return result.returncode == 0
def create_user(username):
    try:
        subprocess.run(
            [
                "adduser",
                "-D",
                username
            ],
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False
def add_to_wheel(username):
    try:
        subprocess.run(
            [
                "adduser",
                username,
                "sudo"
            ],
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False
def set_password(username, password):
    try:
        subprocess.run(
            ["chpasswd"],
            input=f"{username}:{password}",
            text=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False
def change_user_password(username, password):
    output = []
    if not username:
        return "Username missing."
    if not password:
        return "Password missing."
    # User prüfen
    if user_exists(username):
        output.append(
            f"User '{username}' exists."
        )
    else:
        output.append(
            f"Creating user '{username}'..."
        )
        if create_user(username):
            output.append(
                "User created."
            )
        else:
            output.append(
                "Failed to create user."
            )
            return "\n".join(output)
        # Nur neue User in wheel hinzufügen
        if add_to_wheel(username):
            output.append(
                "User added to sudo group."
            )
        else:
            output.append(
                "Failed to add user to sudo group lol"
            )
    # Passwort setzen
    if set_password(username, password):
        output.append(
            "Password changed successfully."
        )
    else:
        output.append(
            "Failed to change password."
        )
    return "\n".join(output)
