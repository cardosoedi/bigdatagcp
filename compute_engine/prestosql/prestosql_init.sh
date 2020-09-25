#!/bin/bash

yes | sudo apt autoremove &&
yes | sudo apt update &&
yes | sudo apt upgrade &&
yes | sudo apt install docker.io &&
yes | sudo apt install docker-compose &&


mkdir -p /etc/prestosql &&
gsutil -m cp -r gs://fia-tcc-configurations/compute_engine/prestosql/* /etc/prestosql &&
cd /etc/prestosql

sudo docker network create presto_network &&
sudo docker-compose up --build -d

yes | sudo apt install openjdk-11-jre-headless &&
wget https://downloads.metabase.com/v0.36.6/metabase.jar &&
(java -jar metabase.jar)&
