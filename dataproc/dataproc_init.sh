apt update -y &&
apt upgrade -y &&
apt install python3-pip python3-dev -y

pip3 install quinn==0.8.0 &&
pip3 install kafka-python==2.0.1 &&
pip3 install google.cloud.storage==1.32.0