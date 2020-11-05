#! /bin/bash

SCALA_VERSION=2.12
KAFKA_VERSION=2.2.2

yes| sudo apt update && yes| sudo apt upgrade
yes| sudo apt install default-jre

cd /opt
sudo wget https://www-us.apache.org/dist/kafka/${KAFKA_VERSION}/kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz
sudo tar -xzf kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz

sudo mv kafka_${SCALA_VERSION}-${KAFKA_VERSION} kafka
sudo rm -rf kafka_${SCALA_VERSION}-${KAFKA_VERSION}
sudo rm kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz

sudo gsutil cp gs://fia-tcc-configurations/compute_engine/kafka/kafka.service /etc/systemd/system/
sudo gsutil cp gs://fia-tcc-configurations/compute_engine/kafka/zookeeper.service /etc/systemd/system/
sudo gsutil cp gs://fia-tcc-configurations/compute_engine/kafka/server.properties /opt/kafka/config/

sudo chmod 755 /etc/systemd/system/zookeeper.service
sudo chmod 755 /etc/systemd/system/kafka.service

sudo systemctl enable zookeeper.service
sudo systemctl stop zookeeper.service
sudo systemctl start zookeeper.service

sudo systemctl enable kafka
sudo systemctl stop kafka
sudo systemctl start kafka

sleep 10

/opt/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic stock
/opt/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic stockFallback


sudo apt -y -qq install apt-transport-https ca-certificates curl software-properties-common &&
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - &&
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable" &&
sudo apt -y -qq install docker-ce docker-compose

gsutil -m cp -r dir gs://fia-tcc-configurations/compute_engine ~/

cd ~/compute_engine

sudo docker pull centos:centos7 &&
sudo docker pull redis:5.0.6 &&
sudo docker pull mysql:5.7 &&
sudo docker pull python:3.7-slim-buster &&
sudo docker pull metabase/metabase:latest

sudo docker-compose up -d
