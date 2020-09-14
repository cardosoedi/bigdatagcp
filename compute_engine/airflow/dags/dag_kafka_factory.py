import os
from datetime import timedelta, datetime
from airflow import DAG
from airflow.contrib.operators.dataproc_operator import DataprocClusterCreateOperator, DataProcPySparkOperator, DataprocClusterDeleteOperator
from airflow_utils import task_fail_slack_alert, load_dags_from_yaml, normalize_dag_id


def create_dag(dag_id,
               schedule,
               default_args,
               dag_param):
    kafka_param = dag_param.get('kafka_param')
    spark_streaming = dag_param.get('spark_streaming')

    with DAG(
            dag_id=dag_id,
            default_args=default_args,
            schedule_interval=schedule,
            catchup=False,
            max_active_runs=1,
            start_date=datetime(2020, 9, 10)
        ) as dag:

        dataproc_clustername = f'{normalize_dag_id(dag_id)}-cluster'

        cria_cluster_streaming = DataprocClusterCreateOperator(
            task_id='cria_cluster_streaming',
            project_id=<your-project-id>,
            cluster_name=dataproc_clustername,
            zone='us-east1-b',
            storage_bucket='<your-gcs-bucket-name>',
            init_actions_uris=['gs://<your-gcs-bucket-name>/dataproc/dataproc_init.sh'],
            init_action_timeout='10m',
            image_version='1.4-debian9',
            properties={
                'spark:spark.driver.core': '1',
                'spark:spark.driver.memory': '18g',
                'spark:spark.driver.memoryOverhead': '2g',
                'spark:spark.executor.cores': '3',
                'spark:spark.executor.instances': '1',
                'spark:spark.executor.memory': '18g',
                'spark:spark.executor.memoryOverhead': '2g',
                'spark:spark.default.parallelism': '12',
                'spark:spark.debug.maxToStringFields': '300',
                'spark:spark.jars.packages': 'org.apache.spark:spark-streaming-kafka-0-8-assembly_2.11:2.4.3,com.redislabs:spark-redis:2.4.0',
                'spark:spark.redis.host': kafka_param.get('host'),
                'spark:spark.redis.port': '6379'
            },
            num_masters=1,
            master_machine_type='e2-highmem-4',
            master_disk_type='pd-standard',
            master_disk_size=1024,
            num_workers=0,
            worker_machine_type='e2-highmem-4',
            worker_disk_type='pd-standard',
            worker_disk_size=1024,
            region='us-east1',
            idle_delete_ttl=1800,
            auto_delete_ttl=3600,
            service_account='<your-service-account>@developer.gserviceaccount.com',
            service_account_scopes=['https://www.googleapis.com/auth/cloud-platform'])

        inicia_spark_streaming = DataProcPySparkOperator(
            task_id='inicia_spark_streaming',
            main='gs://<your-gcs-bucket-name>/compute_engine/airflow/dags/spark/reading_data_from_kafka.py',
            arguments=[f"--host={kafka_param.get('host')}", f"--topic={kafka_param.get('topic')}", f"--key={spark_streaming.get('partitionBy', '')}"],
            cluster_name=dataproc_clustername,
            region='us-east1',
            trigger_rule='all_success'
        )

        deleta_cluster_streaming = DataprocClusterDeleteOperator(
            task_id='deleta_cluster_streaming',
            cluster_name=dataproc_clustername,
            project_id=<your-project-id>,
            region='us-east1',
            trigger_rule='all_done'
        )
        cria_cluster_streaming >> inicia_spark_streaming >> deleta_cluster_streaming
    return dag


for dag_list in load_dags_from_yaml(os.path.dirname(__file__), 'kafka'):
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
