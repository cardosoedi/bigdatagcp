#!/usr/bin/env bash

: "${MYSQL_HOST:="mysql"}"
: "${MYSQL_PORT:="3306"}"

export AIRFLOW_HOME="/opt/airflow"
export AIRFLOW__CORE__SQL_ALCHEMY_CONN="mysql://airflow:airflow@$MYSQL_HOST:$MYSQL_PORT/airflow"

case "$1" in
  webserver)
    airflow initdb
    sleep 10
    airflow upgradedb
    sleep 10
    exec airflow webserver
    ;;
  worker|scheduler)
    sleep 10
    exec airflow "$@"
    ;;
  version)
    exec airflow version
    ;;
  *)
    exec "$@"
    ;;
esac