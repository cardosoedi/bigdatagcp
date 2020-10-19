#!/usr/bin/env bash

apt-get -y -qq install docker docker-compose

docker pull centos:centos7
docker pull redis:5.0.6
docker pull mysql:5.7
docker pull python:3.7-slim-buster
docker pull metabase/metabase:latest

docker-compose up -d

docker-compose exec kafka /opt/kafka/bin/kafka-topics.sh --create --zookeeper zookeeper.lake_network:2181 --replication-factor 1 --partitions 1 --topic stock
docker-compose exec kafka /opt/kafka/bin/kafka-topics.sh --create --zookeeper zookeeper.lake_network:2181 --replication-factor 1 --partitions 1 --topic stockFallback
