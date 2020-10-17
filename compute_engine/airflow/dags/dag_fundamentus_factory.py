import os
from datetime import timedelta, datetime
from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow_utils import task_fail_slack_alert, load_dags_from_yaml


def create_dag(dag_id,
               schedule,
               default_args,
               dag_param):
    kafka_param = dag_param.get('kafka_param')
    stocks = dag_param.get('stocks')
    stock_list = ','.join(stocks)

    with DAG(
        dag_id=dag_id,
        default_args=default_args,
        schedule_interval=schedule,
        catchup=False,
        max_active_runs=1,
        start_date=datetime(2020, 9, 10)
    ) as dag:

        inicio = DummyOperator(task_id='inicio')

        cmd_command = f"python3 /opt/airflow/dags/web_scraper/fundamentus.py --kafka {kafka_param.get('host')} --topic {kafka_param.get('topic')} --stocks {stock_list}"
        executa_web_scraper = BashOperator(
            task_id='executa_web_scraper',
            bash_command=cmd_command)

        fim = DummyOperator(task_id='fim')

        inicio >> executa_web_scraper >> fim
    return dag


for dag_list in load_dags_from_yaml(os.path.dirname(__file__), 'fundamentus'):
    for dag in dag_list:
        for dag_id in dag.keys():
            dag_param = dag.get(dag_id).get('dag_param')
            default_args = {'owner': dag_param.get('owner'),
                            'start_date': datetime(2020, 9, 1),
                            'depends_on_past': False,
                            'retries': 1,
                            'retry_delay': timedelta(seconds=10),
                            'on_failure_callback': task_fail_slack_alert,
                            'slack_channel': dag_param.get('slack_channel')}
            schedule = dag_param.get('schedule')
            globals()[dag_id] = create_dag(dag_id,
                                           schedule,
                                           default_args,
                                           dag.get(dag_id))
