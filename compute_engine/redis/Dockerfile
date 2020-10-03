#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
FROM centos:centos7
LABEL maintainer="Presto community <https://prestosql.io/community.html>"

ENV PRESTO_VERSION 341
ENV PRESTO_HOME /usr/lib/presto
ENV JAVA_HOME /usr/lib/jvm/zulu11

ENV PRESTO_LOCATION=https://repo1.maven.org/maven2/io/prestosql/presto-server/${PRESTO_VERSION}/presto-server-${PRESTO_VERSION}.tar.gz
ENV CLIENT_LOCATION=https://repo1.maven.org/maven2/io/prestosql/presto-cli/${PRESTO_VERSION}/presto-cli-${PRESTO_VERSION}-executable.jar


RUN \
    set -xeu && \
    yum -y -q install curl && \
    yum -y -q install https://cdn.azul.com/zulu/bin/zulu-repo-1.0.0-1.noarch.rpm && \
    yum -y -q update && \
    yum -y -q install zulu11 less && \
    yum -q clean all && \
    rm -rf /var/cache/yum && \
    rm -rf /tmp/* /var/tmp/* && \
    groupadd presto --gid 1000 && \
    useradd presto --uid 1000 --gid 1000 && \
    mkdir -p ${PRESTO_HOME} /data/presto && \
    chown -R "presto:presto" ${PRESTO_HOME} /data/presto

workdir ${PRESTO_HOME}

RUN \
    curl -o ${PRESTO_HOME}/presto-cli-${PRESTO_VERSION}-executable.jar ${CLIENT_LOCATION} && \
    curl -o ${PRESTO_HOME}/presto-server-${PRESTO_VERSION}.tar.gz ${PRESTO_LOCATION} && \
    tar -C ${PRESTO_HOME} -xzf ${PRESTO_HOME}/presto-server-${PRESTO_VERSION}.tar.gz && \
    rm ${PRESTO_HOME}/presto-server-${PRESTO_VERSION}.tar.gz && \
    cp -r ${PRESTO_HOME}/presto-server-${PRESTO_VERSION}/* . && \
    mkdir -p {PRESTO_HOME}/etc/catalog && \
    chmod +x ${PRESTO_HOME}

EXPOSE 8080
USER presto:presto
ENV LANG en_US.UTF-8

CMD ./bin/launcher --config=${PRESTO_HOME}/etc/config.properties --log-levels-file=${PRESTO_HOME}/etc/log.properties --node-config=${PRESTO_HOME}/etc/node.properties run
