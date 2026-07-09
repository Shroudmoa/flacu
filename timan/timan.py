import subprocess



import os

from reboot import reboot_machine

import sys



from install import installTiManService, setup_mode



import signal

from installationStatus import check_installation_status

from uninstall import uninstall

from dirty_uninstall import dirty_uninstall

from shellCmd import run



from maschinemanagment import show_client_log, monitoring_mode, get_routing_table



from check import (



    ping_host,



    test_connection,



    get_ipv4_addresses,



    test_custom,



)



from serviceMan import service_status, start_service, stop_service



from flask import Flask, render_template_string, request, redirect, url_for, session



import shutil







SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))



STATIC_DIR = os.path.join(SCRIPT_DIR, "static")



os.makedirs(STATIC_DIR, exist_ok=True)



background_src = os.getcwd() + "strict/background.jpg"



background_src = os.getcwd() + "strict/background.jpg"



background_dst = os.path.join(STATIC_DIR, "background.jpg")



if os.path.exists(background_src):



    shutil.copy(background_src, background_dst)



logo_src = os.getcwd() + "strict/vm.jpg"



logo_dst = os.path.join(STATIC_DIR, "vm.jpg")



if os.path.exists(logo_src):



    shutil.copy(logo_src, logo_dst)



##########################################################################################



app = Flask(__name__)



app.secret_key = "lbBo85tuAguLZgMMAZisKp6q5Cohkjyy8ikYqtWb"



username = "vm"



password = "vm"



# we can change this later



##########################################################################################



HTML_TEMPLATE = """



<!doctype html>



<html>



<head>



    <title>VM TiMan</title>



    <link rel="icon" href="{{ url_for('static', filename='vm.jpg') }}" type="image/x-icon">



    <style>



        html {



            scroll-behavior: smooth;



        }



        body {



            font-family: Arial, sans-serif;



            background-color: #000000;



            color: white;



            text-align: center;



            padding-top: 50px;



            margin: 0;



            overflow-x: hidden;



        }



        .background-container {



            position: fixed;



            top: 0;



            left: 0;



            width: 100%;



            height: 100%;



            background-size: cover;



            background-position: center center;



            background-repeat: no-repeat;



            z-index: -1;



            opacity: 1;



            transition: opacity 1.5s ease-in-out;



        }



        .background-container::before {



            content: '';



            position: absolute;



            top: 0;



            left: 0;



            width: 100%;



            height: 100%;



            background: linear-gradient(135deg, rgba(0,0,0,0.3) 0%, rgba(29,0,41,0.5) 100%);



            z-index: 0;



        }



        .background-container.fade-out {



            opacity: 0;



        }



        button {



            padding: 15px 25px;



            margin: 10px;



            font-size: 16px;



            cursor: pointer;



            border-radius: 5px;



            border: none;



            background-color: #1d0029;



            color: white;



            transition: all 0.3s ease;



        }



        button:hover {



            background-color: #330047;



            box-shadow: 0 0 15px rgba(255,0,150,0.5);



            transform: translateY(-2px);



        }



        button:active {



            transform: translateY(0px);



        }



        pre {



            background-color: rgba(0, 0, 0, 1);



            padding: 15px;



            border-radius: 5px;



            text-align: left;



            max-width: 1200px;



            margin: 20px auto;



            overflow-x: auto;



            font-size: 12px;



            line-height: 1.4;



        }



        input { 



            padding: 10px; 



            font-size: 16px; 



            border-radius: 5px;



            margin: 5px;



            border: 1px solid #1d0029;



            background-color: rgba(255,255,255,0.1);



            color: white;



            transition: all 0.3s ease;



        }



        input::placeholder {



            color: rgba(255,255,255,0.5);



        }



        input:focus {



            outline: none;



            background-color: rgba(255,255,255,0.15);



            box-shadow: 0 0 10px rgba(255,0,150,0.3);



        }



        .watermark { 



            position: fixed; 



            top: 20px; 



            left: 20px; 



            width: 50px; 



            height: 50px; 



            opacity: 0.8; 



            z-index: 9999;



            animation: float 3s ease-in-out infinite;



        }



        @keyframes float {



            0%, 100% { transform: translateY(0px); }



            50% { transform: translateY(-10px); }



        }



        .dashboard { 



            display: flex; 



            flex-wrap: wrap; 



            justify-content: center; 



            gap: 20px; 



            margin-top: 30px;



        }



        .card { 



            background-color: rgba(0,0,0,0.6); 



            padding: 20px; 



            border-radius: 10px; 



            min-width: 250px; 



            max-width: 400px; 



            color: white;



            transition: all 0.3s ease;



            border-left: 3px solid transparent;



        }



        .card:hover {



            background-color: rgba(0,0,0,0.8);



            border-left-color: #ff0150;



            transform: translateY(-5px);



            box-shadow: 0 8px 20px rgba(255,0,150,0.3);



        }



        .up { 



            color: #00ff00; 



            font-weight: bold;



            text-shadow: 0 0 10px rgba(0,255,0,0.5);



        }



        .down { 



            color: #ff0000; 



            font-weight: bold;



            text-shadow: 0 0 10px rgba(255,0,0,0.5);



        }



        .status-dot {



            width: 12px;



            height: 12px;



            background-color: #00ff00;



            border-radius: 50%;



            display: inline-block;



            margin-right: 8px;



            animation: pulse 2s infinite;



        }



        @keyframes pulse {



            0%, 100% { opacity: 1; }



            50% { opacity: 0.5; }



        }



        .button-group {



            display: flex;



            flex-wrap: wrap;



            justify-content: center;



            gap: 10px;



            margin: 20px 0;



        }



        .input-group {



            margin: 20px 0;



            padding: 20px;



            background-color: rgba(0,0,0,0.3);



            border-radius: 10px;



            display: inline-block;



        }



        .input-group input {



            width: 300px;



            padding: 12px;



            font-size: 16px;



            border-radius: 5px;



            border: 1px solid #1d0029;



            background-color: rgba(255,255,255,0.1);



            color: white;



            margin: 10px 5px;



        }



        .input-group input::placeholder {



            color: rgba(255,255,255,0.5);



        }



        .input-group button {



            padding: 12px 20px;



            margin: 10px 5px;



        }







        .dropdown-wrapper {



            position: relative;



            width: 320px;



        }







        .dropdown-selected {



            background-color: rgba(255,255,255,0.1);



            color: white;



            border: 1px solid #1d0029;



            padding: 12px;



            border-radius: 5px;



            cursor: pointer;



            transition: all 0.3s ease;



            user-select: none;



        }







        .dropdown-selected:hover {



            background-color: rgba(255,255,255,0.15);



            box-shadow: 0 0 10px rgba(255,0,150,0.3);



        }







        .dropdown-menu {



            display: none;



            position: absolute;



            top: 105%;



            left: 0;



            width: 100%;



            background-color: rgba(0,0,0,0.95);



            border: 1px solid #1d0029;



            border-radius: 5px;



            overflow: hidden;



            z-index: 9999;



            box-shadow: 0 0 20px rgba(255,0,150,0.2);



        }



        .command-row {



            display: flex;



            align-items: center;



            justify-content: center;



            gap: 10px;



            flex-wrap: wrap;



        }







        .dropdown-item {



            padding: 12px;



            color: white;



            cursor: pointer;



            transition: all 0.2s ease;



        }







        .dropdown-item:hover {



            background-color: rgba(255,0,150,0.2);



        }



        



        h1 {



            margin-bottom: 30px;



            text-shadow: 0 0 20px rgba(255,0,150,0.3);



        }



        h2 {



            text-shadow: 0 0 15px rgba(255,0,150,0.2);



        }



        .section-title {



            margin-top: 40px;



            font-size: 18px;



            font-weight: bold;



            color: #e0e0e0;



            padding-bottom: 10px;



        }



        @media (max-width: 768px) {



            button {



                padding: 12px 18px;



                font-size: 14px;



            }



            .input-group input {



                width: 250px;



            }



            h1 {



                font-size: 24px;



            }



            .card {



                min-width: 220px;



                max-width: 350px;



            }



        }



    </style>



</head>



<body>



    <div class="background-container"></div>



    <img src="{{ url_for('static', filename='vm.jpg') }}" class="watermark" alt="Watermark">



{% if not session.get("logged_in") %}



    <h2>Login TiMan</h2>



    <form method="post" action="{{ url_for('login') }}">



        <div class="input-group">



            <input type="text" name="username" placeholder="Username" required>



            <input type="password" name="password" placeholder="Password" required>



            <button type="submit">Login</button>



        </div>



    </form>



{% else %}



<h1 style="color: white;"><span class="status-dot"></span>TiMan Visionmaxx GmbH</h1>



<div class="section-title">Service Management</div>



<div class="button-group">



    <form method="post" style="display: inline;">



        <button name="command" value="stop_service">Stop ti-gw-secunet</button>



    </form>



    <form method="post" style="display: inline;">



        <button name="command" value="start_service">Start ti-gw-secunet</button>



    </form>



    <form method="post" style="display: inline;">



        <button name="command" value="get_service_status">Status ti-gw-secunet</button>



    </form>



</div>







<div class="section-title">



    Command Center



</div>







<div class="input-group">







    <div class="command-row">







        <div class="dropdown-wrapper">







            <div class="dropdown-selected"



                 onclick="toggleDropdown()">







                Select Command â–¼







            </div>







            <div class="dropdown-menu"



                 id="dropdownMenu">







                <div class="dropdown-item"



                     onclick="selectCommand('connection-test', 'Test Mailserver')">







                    Test Mailserver







                </div>



                <div class="dropdown-item"



                    onclick="selectCommand('custom-connection-test', 'Custom Connection Test')">







                    Custom Connection Test







                </div>



                <div class="dropdown-item"



                     onclick="selectCommand('pwd', 'Current Directory')">







                    Current Directory







                </div>

                

                <div class="dropdown-item"



                    onclick="selectCommand('reboot', 'Reboot Machine')">







                   Reboot Machine







                </div>









                <div class="dropdown-item"



                     onclick="selectCommand('monitoring', 'Helper-Monitoring')">



                    Helper-Monitoring







                </div>







                <div class="dropdown-item"



                     onclick="selectCommand('show-logs', 'Client Log')">







                    Client Log







                </div>







                <div class="dropdown-item"



                     onclick="selectCommand('route-print', 'Routing Table')">







                    Routing Table







                </div>







            </div>







        </div>



        <div id="customTestFields"



            style="display:none; margin-top:15px;">







            <input type="text"



                name="custom_ip"



                form="commandForm"



                placeholder="IP Address">







            <input type="number"



                name="custom_port"



                form="commandForm"



                placeholder="Port">







        </div>











        <form method="post"



              id="commandForm"



              style="margin: 0;">







            <input type="hidden"



                   name="command"



                   id="commandInput">







            <button type="submit">



                Execute Command



            </button>







        </form>







    </div>







</div>







<div class="section-title">Setup & Configuration</div>



<div class="input-group">



    <div class="command-row">



        <div class="dropdown-wrapper">



            <div class="dropdown-selected"

                 id="setupSelected"

                 onclick="toggleSetupDropdown()">



                Select Setup Action ▼



            </div>





            <div class="dropdown-menu"

                 id="setupDropdownMenu">





                <div class="dropdown-item"

                     onclick="selectSetupCommand('install', 'Install')">



                    Install



                </div>





                <div class="dropdown-item"

                     onclick="selectSetupCommand('uninstall', 'Uninstall')">



                    Uninstall



                </div>





                <div class="dropdown-item"

                     onclick="selectSetupCommand('dirty-uninstall', 'Dirty Uninstall')">



                    Dirty Uninstall



                </div>





                <div class="dropdown-item"

                     onclick="selectSetupCommand('installation-status', 'Installation Status')">



                    Installation Status



                </div>





            </div>



        </div>







        <div id="setupFields"

             style="display:none; margin-top:15px;">





            <input type="text"

                   id="kundennummerField"

                   name="kundennummer"

                   form="setupForm"

                   placeholder="Kundennummer">





            <input type="password"

                   id="passwordField"

                   name="setup_password"

                   form="setupForm"

                   placeholder="Password">





        </div>







        <form method="post"

              id="setupForm"

              style="margin:0;">





            <input type="hidden"

                   name="command"

                   id="setupCommandInput">





            <button type="submit">



                Execute Setup



            </button>





        </form>





    </div>



</div>

{% if output %}



<div class="section-title">Output</div>



<pre>{{ output }}</pre>



{% endif %}



<div class="dashboard">



    <div class="card">



        <h3><span class="status-dot"></span>Machine IPs</h3>



        <pre>{{ machine_ips }}</pre>



    </div>



    <div class="card">



        <h3><span class="status-dot"></span>Ping 8.8.8.8</h3>



        <p>Status: <span class="{{ 'up' if ping_status=='Reachable' else 'down' }}">{{ ping_status }}</span></p>



    </div>



    <div class="card">



        <h3>ti-gw-secunet</h3>



        <p>Status: <span class="{{ 'up' if service_status_value=='Running' else 'down' }}">{{ service_status_value }}</span></p>



    </div>



</div>



<div class="section-title">Account</div>



<div class="button-group">



    <form method="post" style="display: inline;">



        <button name="command" value="logout" style="background-color: #a61d2a;">Logout</button>



    </form>



</div>



{% endif %}



<script>

function toggleSetupDropdown() {



    const menu = document.getElementById("setupDropdownMenu");



    menu.style.display =

        menu.style.display === "block"

        ? "none"

        : "block";



}







function selectSetupCommand(value, label) {





    document.getElementById("setupCommandInput").value = value;





    document.getElementById("setupSelected").innerText = label;





    document.getElementById("setupDropdownMenu").style.display = "none";





    const fields = document.getElementById("setupFields");



    const kdn = document.getElementById("kundennummerField");



    const password = document.getElementById("passwordField");







    if (value === "install") {



        fields.style.display = "block";



        kdn.style.display = "inline-block";



        password.style.display = "inline-block";





    } 

    else if (

        value === "uninstall" ||

        value === "dirty-uninstall"

    ) {



        fields.style.display = "block";



        kdn.style.display = "none";



        password.style.display = "inline-block";





    }

    else {



        fields.style.display = "none";



    }



}



function toggleDropdown() {



    const menu = document.getElementById("dropdownMenu");



    menu.style.display = menu.style.display === "block" ? "none" : "block";



}







function selectCommand(value, label) {







    document.getElementById("commandInput").value = value;







    document.querySelector(".dropdown-selected").innerText = label;







    document.getElementById("dropdownMenu").style.display = "none";







    const customFields = document.getElementById("customTestFields");







    if (value === "custom-connection-test") {



        customFields.style.display = "block";



    } else {



        customFields.style.display = "none";



    }



}











document.addEventListener("click", function(e) {



    if (!e.target.closest(".dropdown-wrapper")) {



        document.getElementById("dropdownMenu").style.display = "none";



    }



});







</script>







    <script>



        const bgContainer = document.querySelector('.background-container');



        async function updateBackground() {



            try {



                const response = await fetch('/get-background');



                const data = await response.json();



                const newBg = `{{ url_for('static', filename='') }}${data.background}`;



                // Fade out



                bgContainer.classList.add('fade-out');



                // Wait for fade out, then change image and fade in



                setTimeout(() => {



                    bgContainer.style.backgroundImage = `url('${newBg}')`;



                    bgContainer.classList.remove('fade-out');



                }, 1500); // Half of the transition time



            } catch (error) {



                console.error('Failed to update background:', error);



            }



        }



        // Update background every ... 



        setInterval(updateBackground, 20000); // 20 seconds 



        // Set initial background



        updateBackground();



        // Add visual feedback on form submission



        document.querySelectorAll('form').forEach(form => {



            form.addEventListener('submit', function() {



                const buttons = this.querySelectorAll('button[type="submit"]');



                buttons.forEach(btn => {



                    btn.style.opacity = '0.7';



                });



            });



        });



    </script>



</body>



</html>



"""











@app.route("/get-background")



def get_background():



    # return {"background": backgrounds[current_bg_index]}  # also kinda useless



    return {"background": "background.jpg"}











# didnt know that can be useful but it is..keep for Supporting phase so we can see if timan is running as a Service or not



def get_currbindir():



    try:



        result = subprocess.run(["pwd"], capture_output=True, text=True, timeout=5)



        return result.stdout if result.stdout else "Current directory not found"



    except Exception as e:



        return f"Error: {str(e)}"











# login is like only 20 lines and the it-guy cant play around or talk SH about the timan security



@app.route("/", methods=["GET", "POST"])



def index():



    if not session.get("logged_in"):



        return redirect(url_for("login"))



    # v2 type :



    output = ""



    if request.method == "POST":



        cmd_key = request.form.get("command")



        kundennummer = request.form.get("kundennummer", None)



        if cmd_key == "logout":



            session.pop("logged_in", None)



            return redirect(url_for("login"))

        elif cmd_key == "install":



            kundennummer = request.form.get("kundennummer")

            setup_password = request.form.get("setup_password")





            if setup_password != "supersecret":

                output = "Invalid setup password"



            elif not kundennummer:

                output = "Kundennummer required"



            else:

                output = setup_mode(kundennummer)







        elif cmd_key == "uninstall":



            setup_password = request.form.get("setup_password")



            if setup_password != "supersecret":

                output = "Invalid setup password"



            else:

                output = uninstall()







        elif cmd_key == "dirty-uninstall":



            setup_password = request.form.get("setup_password")



            if setup_password != "supersecret":

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



            )  #################flaw - wrong name chnage later pls. #ciel



        elif cmd_key == "connection-test":



            output = test_connection()



        elif cmd_key == "pwd":



            output = get_currbindir()



        elif cmd_key == "stop_service":



            output = stop_service()



        elif cmd_key == "start_service":



            output = start_service()



        elif cmd_key == "get_service_status":



            output = service_status()



        elif cmd_key == "route-print":



            output = get_routing_table()

        elif cmd_key == "reboot":



            output = reboot_machine()

        elif cmd_key == "custom-connection-test":



            ip = request.form.get("custom_ip")



            port = request.form.get("custom_port")







            output = test_custom(ip, port)







        else:



            output = "Invalid command"



    machine_ips = get_ipv4_addresses()  # get_machine_ips()



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



        username = request.form.get("username")



        password = request.form.get("password")



        if username == username and password == password:



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











# useless for now but might be useful later for graceful shutdown...



def signal_handler(sig, frame):



    print("\nShutting down Flask application...")



    sys.exit(0)











# port 5000 and 0.0.0.0 for LE and threaded for better performance - debug false for security reasons



if __name__ == "__main__":



    # v37



    try:



        if installTiManService():



            run("apk update")



            run("apk add curl iproute2 nano vim")



            run("rc-update add timan default")



            run("rc-service timan start")



            sys.exit(0)



    except Exception as e:



        print("Install failed:", e)







    signal.signal(signal.SIGINT, signal_handler)



    signal.signal(signal.SIGTERM, signal_handler)



    sys.stdout.flush()



    app.run(debug=False, host="0.0.0.0", port=5000, threaded=True)
