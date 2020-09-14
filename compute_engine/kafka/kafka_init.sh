#! /bin/bash
pwd &&
sudo apt-get -y -qq update &&
sudo apt-get -y -qq upgrade &&
sudo apt install -y -qq default-jre &&
sudo apt -y -qq autoremove

# adduser kafka
# usermod -aG sudo kafka

# su - kafka

cd /opt &&
sudo wget https://www-us.apache.org/dist/kafka/2.2.2/kafka_2.12-2.2.2.tgz &&
sudo tar -xzf kafka_2.12-2.2.2.tgz &&

sudo mv kafka_2.12-2.2.2 kafka &&
sudo rm -rf kafka_2.12-2.2.2 &&
sudo rm kafka_2.12-2.2.2.tgz &&

sudo gsutil cp gs://<your-gcs-bucket-name>/compute_engine/kafka/kafka.service /etc/systemd/system/ &&
sudo gsutil cp gs://<your-gcs-bucket-name>/compute_engine/kafka/zookeeper.service /etc/systemd/system/ &&
sudo gsutil cp gs://<your-gcs-bucket-name>/compute_engine/kafka/server.properties /opt/kafka/config/ &&

sudo chmod 755 /etc/systemd/system/zookeeper.service &&
sudo chmod 755 /etc/systemd/system/kafka.service &&

sudo systemctl enable zookeeper.service &&
sudo systemctl stop zookeeper.service &&
sudo systemctl start zookeeper.service &&

sudo systemctl enable kafka &&
sudo systemctl stop kafka &&
sudo systemctl start kafka &&

sleep 10

/opt/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic Stocks &&
/opt/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic StocksFallback

# ===========================
# Subir docker com redis
# ===========================
sudo apt -y -qq update &&
sudo apt -y -qq upgrade &&
sudo apt -y -qq install docker &&
sudo apt -y -qq install docker-compose &&
sudo apt -y -qq install redis-tools &&
sudo apt -y -qq autoremove
sudo docker pull redis:5.0.6 &&
sudo docker run -d -p 6379:6379 -i -t redis:5.0.6
