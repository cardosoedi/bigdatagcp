import os
from datetime import timedelta, datetime
from airflow import DAG
from airflow.contrib.operators.dataproc_operator import DataprocClusterCreateOperator, DataProcPySparkOperator, DataprocClusterDeleteOperator
from airflow_utils import task_fail_slack_alert, load_dags_from_yaml, normalize_dag_id
from airflow.hooks.base_hook import BaseHook

gcp_project_id = BaseHook.get_connection('google_cloud_default').extra_dejson['extra__google_cloud_platform__project']


def create_dag(dag_id,
               schedule,
               default_args,
               dag_param):
    kafka_param = dag_param.get('kafka_param')
    spark_param = dag_param.get('spark_param')

    dag_id = dag_id+'-raw-to-process'
    with DAG(
            dag_id=dag_id,
            default_args=default_args,
            schedule_interval=schedule,
            catchup=False,
            max_active_runs=1,
            start_date=datetime(2020, 9, 10)
    ) as dag:

        dataproc_clustername = f'{normalize_dag_id(dag_id)}-cluster'

        create_spark_cluster = DataprocClusterCreateOperator(
            task_id='create_spark_cluster',
            project_id=gcp_project_id,
            cluster_name=dataproc_clustername,
            zone='us-east1-b',
            storage_bucket='fia-tcc-logs',
            init_actions_uris=['gs://fia-tcc-configurations/dataproc/dataproc_init.sh',
                               'gs://goog-dataproc-initialization-actions-us-east1/cloud-sql-proxy/cloud-sql-proxy.sh'],
            init_action_timeout='10m',
            image_version='1.4-debian9',
            metadata={'hive-metastore-instance': 'fia-tcc:us-east1:hive-metastore'},
            properties={
                'spark:spark.driver.core': '1',
                'spark:spark.driver.memory': '3584M',
                'spark:spark.driver.memoryOverhead': '512M',
                'spark:spark.executor.cores': '1',
                'spark:spark.executor.instances': '1',
                'spark:spark.executor.memory': '3584M',
                'spark:spark.executor.memoryOverhead': '512M',
                'spark:spark.default.parallelism': '1',
                'spark:spark.debug.maxToStringFields': '300'
            },
            num_masters=1,
            master_machine_type='e2-standard-2',
            master_disk_type='pd-standard',
            master_disk_size=1024,
            num_workers=0,
            worker_machine_type='e2-standard-2',
            worker_disk_type='pd-standard',
            worker_disk_size=1024,
            region='us-east1',
            idle_delete_ttl=1800,
            auto_delete_ttl=3600,
            service_account='sa-fia-tcc@fia-tcc.iam.gserviceaccount.com',
            service_account_scopes=[
                'https://www.googleapis.com/auth/cloud-platform',
                'https://www.googleapis.com/auth/sqlservice.admin'])

        if spark_param.get('script'):
            spark_raw_to_process = DataProcPySparkOperator(
                task_id='spark_raw_to_process',
                main=spark_param.get('script'),
                arguments=spark_param.get('script_arguments'),
                cluster_name=dataproc_clustername,
                region='us-east1',
                trigger_rule='all_success')
        else:
            spark_raw_to_process = DataProcPySparkOperator(
                task_id='spark_raw_to_process',
                main='gs://fia-tcc-configurations/compute_engine/airflow/dags/spark/raw_to_processed.py',
                arguments=[f"--source={spark_param.get('source')}",
                           f"--dataset={kafka_param.get('topic')}",
                           f"--key={spark_param.get('key')}"],
                cluster_name=dataproc_clustername,
                region='us-east1',
                trigger_rule='all_success')

        delete_spark_cluster = DataprocClusterDeleteOperator(
            task_id='delete_spark_cluster',
            cluster_name=dataproc_clustername,
            project_id=gcp_project_id,
            region='us-east1',
            trigger_rule='all_done')
        create_spark_cluster >> spark_raw_to_process >> delete_spark_cluster
    return dag


for dag_list in load_dags_from_yaml(os.path.dirname(__file__), 'kafka'):
    for dag in dag_list:
        for dag_id in dag.keys():
            dag_param = dag.get(dag_id).get('dag_param').get('raw_to_process_dag')
            if dag_param:
                default_args = {'owner': dag.get(dag_id).get('dag_param').get('owner'),
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
            else:
                pass
