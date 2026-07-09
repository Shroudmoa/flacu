import os

import subprocess





TIGW_DIR = "/home/vm/tigw"

UNINSTALL_CLIENT = "/home/vm/tigw/uninstall_client"





def check_installation_status():



    output = []



    # Service check

    try:

        service = subprocess.run(

            ["rc-service", "ti-gw-secunet", "status"],

            capture_output=True,

            text=True

        )



        if "started" in service.stdout.lower() or service.returncode == 0:

            output.append("ti-gw-secunet Service is detected")

        else:

            output.append("ti-gw-secunet Service is NOT detected")



    except Exception:

        output.append("ti-gw-secunet Service check failed")





    # Directory check

    if os.path.exists(TIGW_DIR):

        output.append("/home/vm/tigw directory is detected")

    else:

        output.append("/home/vm/tigw directory is NOT detected")





    # Clean installation check

    if os.path.exists(UNINSTALL_CLIENT):

        output.append(

            "Clean installation detected cause /home/vm/tigw/uninstall_client is detected"

        )

    else:

        output.append(

            "Clean installation marker not detected"

        )





    # RAM

    try:

        mem = subprocess.check_output(

            ["grep", "MemTotal", "/proc/meminfo"],

            text=True

        )



        ram_mb = int(mem.split()[1]) // 1024

        ram_gb = round(ram_mb / 1024)



        output.append(f"Ram = {ram_gb} GB")



    except Exception:

        output.append("Ram detection failed")





    # CPU

    try:

        cores = os.cpu_count()

        output.append(f"Cpu core = {cores}")



    except Exception:

        output.append("Cpu detection failed")





    return "\n".join(output)
