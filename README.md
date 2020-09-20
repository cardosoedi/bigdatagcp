### Pré requisitos para execução dos scripts

1. Crie um login no google cloud plataform e adicione um projeto.
2. Crie um bucket para subir os arquivos do projeto.
3. Crie uma service account com permissões de owner do projeto
3. Com find/replace substitua em todos os arquivos os valores os itens abaixo:
    1. \<your-gcs-bucket-name\> para o nome do seu bucket no GCS.
    2. \<your-service-account\>@developer.gserviceaccount.com para sua service account.
    3. \<your-project-id\> para o nome do seu projeto no GCP.
4. Instale o sdk do google (gsutils) na sua máquina. Veja como nesse [link.](https://cloud.google.com/storage/docs/gsutil_install) 
5. Copie os diretórios compute_engine e dataproc para a raiz do seu bucket gerado no passo 2
6. Abra um terminal ou prompt de commando e execute os comandos abaixo

************************************************************************************************************************
### Subindo o serviço do Kafka e redis em um Compute Engine (vm instances)
```
gcloud beta compute --project=<your-project-id> instances create kafka \
--zone=us-east1-b \
--machine-type=e2-standard-4 \
--subnet=default \
--network-tier=PREMIUM \
--metadata startup-script-url=gs://<your-gcs-bucket-name>/compute_engine/kafka/kafka_init.sh \
--maintenance-policy=MIGRATE \
--image=ubuntu-2004-focal-v20200902 \
--image-project=ubuntu-os-cloud \
--boot-disk-size=30GB \
--boot-disk-type=pd-ssd \
--boot-disk-device-name=kafka_disk \
--reservation-affinity=any \
--service-account <your-service-account>@developer.gserviceaccount.com \
--scopes https://www.googleapis.com/auth/cloud-platform \
--tags https-server
```

************************************************************************************************************************
### Subindo banco mysql para armazenar o metastore do hive (Cloud SQL)
```
gcloud sql instances create hive-metastore \
--database-version="MYSQL_5_7" \
--activation-policy=ALWAYS \
--zone us-east1
```

************************************************************************************************************************
### Subindo hive para disponibilizar o metastore para o presto
```
gcloud beta dataproc clusters create hive-cluster \
--scopes sql-admin \
--bucket fia-tcc-dataproc-metainfo \
--region us-east1 \
--zone us-east1-b \
--single-node \
--master-machine-type e2-standard-2 \
--master-boot-disk-type pd-ssd \
--master-boot-disk-size 30GB \
--image-version 1.4-debian9 \
--project fia-tcc \
--initialization-actions 'gs://goog-dataproc-initialization-actions-us-east1/cloud-sql-proxy/cloud-sql-proxy.sh' \
--metadata "hive-metastore-instance=fia-tcc:us-east1:hive-metastore" \
--properties hive:hive.metastore.warehouse.dir=gs://fia-tcc-dataproc-metainfo/dataproc/datasets
```

************************************************************************************************************************
### Subindo o serviço do PrestoSQL e Metabase em um Compute Engine (vm instances)
```
gcloud beta compute --project=fia-tcc instances create prestosql \
--zone=us-east1-b \
--machine-type=e2-standard-4 \
--subnet=default \
--network-tier=PREMIUM \
--metadata startup-script-url=gs://fia-tcc-dataproc-metainfo/compute_engine/prestosql/prestosql_init.sh \
--maintenance-policy=MIGRATE \
--image=ubuntu-2004-focal-v20200902 \
--image-project=ubuntu-os-cloud \
--boot-disk-size=30GB \
--boot-disk-type=pd-ssd \
--boot-disk-device-name=prestosql_disk \
--reservation-affinity=any \
--service-account 46783465558-compute@developer.gserviceaccount.com \
--scopes https://www.googleapis.com/auth/cloud-platform \
--tags https-server
```
### Redirecione sua porta local para acesso a UI do presto
```gcloud compute ssh prestosql --project fia-tcc --zone us-east1-b -- -L 18080:localhost:18080```


************************************************************************************************************************
### Subindo o serviço do airflow em um Compute Engine (vm instances)
```
gcloud beta compute --project=<your-project-id> instances create airflow \
--zone=us-east1-b \
--machine-type=e2-standard-4 \
--subnet=default \
--network-tier=PREMIUM \
--metadata startup-script-url=gs://<your-gcs-bucket-name>/compute_engine/airflow/airflow_init.sh \
--maintenance-policy=MIGRATE \
--image=ubuntu-2004-focal-v20200902 \
--image-project=ubuntu-os-cloud \
--boot-disk-size=30GB \
--boot-disk-type=pd-ssd \
--boot-disk-device-name=airflow_disk \
--reservation-affinity=any \
--service-account <your-service-account>@developer.gserviceaccount.com \
--scopes https://www.googleapis.com/auth/cloud-platform \
--tags https-server
```

### Redirecione sua porta local para acesso a UI do airflow
```gcloud compute ssh airflow --project <your-project-id> --zone us-east1-b -- -L 8080:localhost:8080```

##### Configurações na UI do airflow

- Alterar a connection google_cloud_default:

    ```
  project_id = <your-project-id>
  scope = https://www.googleapis.com/auth/cloud-platform
  ```

 - Criar uma connection slack_conn com os valores:
    ```
    login: <your-slack-channel>
    password: <your-slackbot-token>
    ```
   
Após as configurações das conexões, ative as duas dags que aparecem na UI do airflow.  
Execute inicialmente a dag fundamentus-stocks-stream, para subir um cluster de sparkstream e ativar o job
Assim que a task do job estiver em running, ative e execute a dag do web scrapper send-stocks-to-kafka.  
  
Com o comando abaixo você poderá acessar os dados salvos no seu bucket via jupyter.
************************************************************************************************************************
### Criar um cluster com Jupyter Notebook para exploração dos dados
__no windows trocar ^ por ^^^^__
```
gcloud beta dataproc clusters create validation \
--enable-component-gateway \
--scopes sql-admin \
--bucket fia-tcc-dataproc-metainfo \
--region us-east1 \
--zone us-east1-b \
--single-node \
--master-machine-type e2-standard-2 \
--master-boot-disk-type pd-ssd \
--master-boot-disk-size 30GB \
--image-version 1.4-debian9 \
--optional-components ANACONDA,JUPYTER \
--project fia-tcc \
--initialization-actions 'gs://goog-dataproc-initialization-actions-us-east1/cloud-sql-proxy/cloud-sql-proxy.sh','gs://fia-tcc-dataproc-metainfo/dataproc/dataproc_init.sh' \
--metadata "hive-metastore-instance=fia-tcc:us-east1:hive-metastore" \
--properties=^#^spark:spark.driver.core=1\
#spark:spark.driver.memory=2g\
#spark:spark.driver.memoryOverhead=1g\
#spark:spark.executor.cores=1\
#spark:spark.executor.instances=1\
#spark:spark.executor.memory=4g\
#spark:spark.executor.memoryOverhead=1g\
#spark:spark.debug.maxToStringFields=300\
#spark:spark.jars.packages=org.apache.spark:spark-streaming-kafka-0-8-assembly_2.11:2.4.5,com.redislabs:spark-redis:2.4.0\
#spark:spark.redis.host=<your-kafka-ip>\
#spark:spark.redis.port=6379
```

Para conectar no jupyter, acesse a UI do seu projeto no google cloud platform  
 -> Depois entre em Google Dataproc no menu lateral  
 -> Acesse a configuração do seu cluster "validation"  
 -> Então no menu interfaces web, click no link Jupyter  
 
************************************************************************************************************************