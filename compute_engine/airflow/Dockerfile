FROM python:3.7-slim-buster

RUN apt-get -y -qq update && \
    apt-get install  -y -qq build-essential

RUN apt-get install -y -qq --no-install-recommends \
    freetds-bin \
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


ENV AIRFLOW_HOME=/opt/airflow
RUN useradd -ms /bin/bash -d ${AIRFLOW_HOME} airflow
RUN pip3 uninstall mysql-python
RUN pip3 install PyMySQL

WORKDIR ${AIRFLOW_HOME}
RUN pip3 install 'apache-airflow[gcp, google_auth, slack, mysql]'==1.10.12 --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-1.10.12/constraints-3.7.txt"

COPY --chown=airflow requirements.txt ${AIRFLOW_HOME}/requirements.txt
RUN pip3 install -r requirements.txt

COPY --chown=airflow dags ${AIRFLOW_HOME}/dags
COPY --chown=airflow airflow.cfg ${AIRFLOW_HOME}/airflow.cfg
COPY --chown=airflow entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh
RUN chown -R airflow:airflow ${AIRFLOW_HOME}

EXPOSE 8080 8793
USER airflow
WORKDIR ${AIRFLOW_HOME}

ENTRYPOINT ["/entrypoint.sh"]
CMD ["webserver"]