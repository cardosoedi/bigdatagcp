#!/usr/bin/env bash

: "${ZOOKEEPER_HOST:="zookeeper.lake_network"}"
: "${ZOOKEEPER_PORT:="2181"}"

export KAFKA_HOME="/opt/kafka"
${KAFKA_HOME}/bin/zookeeper-server-start.sh ${KAFKA_HOME}/config/zookeeper.properties &
sleep 10
${KAFKA_HOME}/bin/kafka-server-start.sh ${KAFKA_HOME}/config/server.properties > ${KAFKA_HOME}/kafka.log 2>&1