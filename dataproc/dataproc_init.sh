apt update -y &&
apt upgrade -y &&
apt install python3-pip python3-dev -y &&
pip3 install quinn &&
pip3 install kafka-python