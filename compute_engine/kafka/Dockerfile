FROM centos:centos7

ENV KAFKA_HOME=/opt/kafka
ENV SCALA_VERSION=2.12
ENV KAFKA_VERSION=2.2.2
ENV JAVA_HOME=/usr/lib/jvm/zulu11

RUN groupadd kafka --gid 1000 && \
    useradd --uid 1000 --gid 1000 -ms /bin/bash -d ${KAFKA_HOME} kafka && \
    chown -R "kafka:kafka" ${KAFKA_HOME}

RUN yum -y -q install https://cdn.azul.com/zulu/bin/zulu-repo-1.0.0-1.noarch.rpm && \
    yum -y -q update && \
    yum install -y -q wget zulu11 less && \
    yum -q clean all && \
    rm -rf /var/cache/yum && \
    rm -rf /tmp/* /var/tmp/*

WORKDIR KAFKA_HOME
RUN wget https://downloads.apache.org/kafka/${KAFKA_VERSION}/kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz -O /tmp/kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz && \
    tar -xzf /tmp/kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz -C /tmp && \
    mv /tmp/kafka_${SCALA_VERSION}-${KAFKA_VERSION}/* ${KAFKA_HOME} && \
    rm -rf /tmp/kafka_${SCALA_VERSION}-${KAFKA_VERSION} && rm -rf /tmp/kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz

COPY server.properties ${KAFKA_HOME}/config/server.properties
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

EXPOSE 2181 9092
USER kafka:kafka
ENV LANG en_US.UTF-8
ENTRYPOINT ["/entrypoint.sh"]
