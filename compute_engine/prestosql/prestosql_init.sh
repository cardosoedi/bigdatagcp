#!/bin/bash

yes | sudo apt autoremove &&
yes | sudo apt update &&
yes | sudo apt upgrade &&
yes | sudo apt install docker.io &&
sudo docker pull prestosql/presto
sudo docker run -d -p 127.0.0.1:18080:8080 --name presto prestosql/presto:latest

yes | sudo apt install openjdk-11-jre-headless &&
wget https://downloads.metabase.com/v0.36.6/metabase.jar &&
(java -jar metabase.jar)&
