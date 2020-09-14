import os
import glob
import yaml
from airflow.hooks.base_hook import BaseHook
from airflow.operators.slack_operator import SlackAPIPostOperator

SLACK_CONN_ID = 'slack_conn'


def task_fail_slack_alert(context):
    """
    Sends message to a slack channel.    If you want to send it to a "user" -> use "@user",
        if "public channel" -> use "#channel",
        if "private channel" -> use "channel"
    """
    slack_channel = context['dag'].default_args.get('slack_channel', BaseHook.get_connection(SLACK_CONN_ID).login)
    slack_token = BaseHook.get_connection(SLACK_CONN_ID).password
    failed_alert = SlackAPIPostOperator(
        task_id='slack_failed',
        channel=slack_channel,
        token=slack_token,
        text="""
            :red_circle: Task Failed. 
            *Task*: {task}  
            *Dag*: {dag} 
            *Execution Time*: {exec_date}  
            *Log Url*: {log_url} 
            """.format(
            task=context.get('task_instance').task_id,
            dag=context.get('task_instance').dag_id,
            exec_date=context.get('execution_date'),
            log_url=context.get('task_instance').log_url,
        )
    )
    return failed_alert.execute(context=context)


def load_dags_from_yaml(my_location, pipeline):
    work_dir = os.path.abspath(my_location)
    yaml_path = os.path.join(work_dir, f'yamls/{pipeline}/*.yaml')
    dags=[]
    for yaml_file in glob.glob(yaml_path):
        with open(yaml_file) as file:
            dag = yaml.load(file, Loader=yaml.FullLoader)
            dags.append(dag)
    yield dags


def normalize_dag_id(old_string):
    return old_string.replace('_', '-').replace(' ', '-')
