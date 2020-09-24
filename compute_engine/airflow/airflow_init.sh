#! /bin/bash
pwd &&
sudo apt-get -y -qq update &&
sudo apt-get -y -qq upgrade &&
sudo apt-get install -y -qq --no-install-recommends \
        libsasl2-2 \
        libsasl2-modules \
        libssl1.1 \
        locales  \
        lsb-release \
        sasl2-bin \
        sqlite3 \
        unixodbc \
        libmysqlclient-dev \
        gcc &&

sudo apt-get install -y -qq python3-pip python3-dev &&
sudo apt -y -qq autoremove &&

sudo apt install -y -qq mysql-server &&
echo '[mysqld]' >> /etc/mysql/my.cnf && echo 'explicit_defaults_for_timestamp = true' >> /etc/mysql/my.cnf &&
sudo service mysql restart &&

mysql -e "create database airflow" &&
mysql -e "CREATE USER 'airflow'@'localhost' IDENTIFIED BY 'airflow'" &&
mysql -e "GRANT ALL PRIVILEGES ON *.* TO 'airflow'@'localhost'" &&
mysql -e "flush privileges" &&

sudo pip3 -q install 'apache-airflow[gcp, google_auth, slack, redis, mysql]==1.10.12' &&
sudo pip3 -q install requests==2.24.0 &&
sudo pip3 -q install quinn &&
sudo pip3 -q install bs4==0.0.1 &&
sudo pip3 -q install kafka-python==2.0.1 &&

mkdir -p /root/airflow/dags &&
echo 'export AIRFLOW_HOME=/root/airflow' >> /root/.bashrc &&
source /root/.bashrc &&
gsutil -m cp gs://fia-tcc-configurations/compute_engine/airflow/airflow.cfg /root/airflow/ &&
gsutil -m cp -r gs://fia-tcc-configurations/compute_engine/airflow/dags/* /root/airflow/dags/ &&

airflow initdb &&
(airflow webserver --port=8080&) &&
(airflow scheduler&)
