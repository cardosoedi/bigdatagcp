FROM python:3.7-slim-buster

RUN apt-get -y -qq update && \
    apt-get -y -qq upgrade

RUN apt-get install -y -qq --no-install-recommends \
    libsasl2-2 \
    libsasl2-modules \
    libssl1.1 \
    locales  \
    lsb-release \
    sasl2-bin \
    sqlite3 \
    unixodbc \
    default-libmysqlclient-dev \
    gcc
RUN apt-get install -y -qq python3-pip python3-dev
RUN apt-get -y -qq autoremove

ENV AIRFLOW_HOME=/opt/airflow
RUN useradd -ms /bin/bash -d ${AIRFLOW_HOME} airflow

WORKDIR ${AIRFLOW_HOME}
RUN pip3 install 'apache-airflow[gcp, google_auth, slack, redis, mysql]==1.10.12'

COPY requirements.txt ${AIRFLOW_HOME}/requirements.txt
RUN pip3 install -r requirements.txt

COPY dags ${AIRFLOW_HOME}/dags
COPY airflow.cfg ${AIRFLOW_HOME}/airflow.cfg
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh
RUN chown -R airflow: ${AIRFLOW_HOME}

EXPOSE 8080
USER airflow
WORKDIR ${AIRFLOW_HOME}

ENTRYPOINT ["/entrypoint.sh"]
CMD ["webserver"]