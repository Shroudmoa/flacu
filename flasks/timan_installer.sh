#!/bin/sh
set -e  
sudo apk update
sudo apk add iproute2 git nano vim
#FTP
sudo curl -L -o /usr/local/bin/timan https://vm-tiaas.visionmaxx.net/ti-gw/timan/v36.bin

sudo chmod +x /usr/local/bin/timan


sudo tee /etc/init.d/timan > /dev/null << 'EOF'
#!/sbin/openrc-run

name="TiMan Dashboard"
description="Flask-based VM TiMan Gateway Manager"

command="/usr/local/bin/timan"
command_background="yes"
pidfile="/run/timan.pid"

output_log="/var/log/timan.log"
error_log="/var/log/timan.err"
EOF
sudo sed -i '1{/^$/d}' /etc/init.d/timan
sudo sed -i 's/\r$//' /etc/init.d/timan
sudo sed -i '1s/^\xEF\xBB\xBF//' /etc/init.d/timan

sudo chmod +x /etc/init.d/timan

sudo rc-update add timan default
sudo rc-service timan start
clear
echo "TiMan setup complete."
echo "Access it at http://THE_IP:5000  --------   Use 'ip addr' to find the IP address of this machine if needed."
echo ""
echo " Questions? Ask rmi/moa" 
echo ""
