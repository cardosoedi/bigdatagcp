# dags/subdags.py
from airflow.models import DAG
from airflow.models.variable import Variable
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator

child_dag_name = 'IngestaoFundamentus'

var_streaming_process = Variable.get("streaming_process", deserialize_json=True)
stock_list = Variable.get("stock_list")
stocks_vars = var_streaming_process['Stocks']
KAFKA_HOST = stocks_vars.get('kafka_host')
TOPIC_NAME = stocks_vars.get('topic_name')

cmd_command = f"python3 /root/airflow/dags/web_scraper/fundamentus.py --kafka {KAFKA_HOST} --topic {TOPIC_NAME} --stocks {stock_list}"


# Dag is returned by a factory method
def sub_dag(parent_dag_name, start_date, schedule_interval):
    dag = DAG('%s.%s' % (parent_dag_name, child_dag_name),
              schedule_interval=schedule_interval,
              start_date=start_date)

    inicio = DummyOperator(
        task_id='inicio',
        dag=dag)

    executa_web_scraper = BashOperator(
        task_id='executa_web_scraper',
        bash_command=cmd_command,
        dag=dag)

    fim = DummyOperator(
        task_id='fim',
        dag=dag)

    inicio >> executa_web_scraper >> fim
    return dag
