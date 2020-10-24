### Pré requisitos para execução dos scripts

1. Crie um login no google cloud plataform e adicione um projeto chamado fia-tcc.
2. Crie um bucket chamado fia-tcc-configurations para subir os arquivos do projeto.
3. Crie uma service account chamada sa-fia-tcc com permissões de owner do projeto
4. Instale o sdk do google (gsutils) na sua máquina. Veja como nesse [link.](https://cloud.google.com/storage/docs/gsutil_install) 
5. Copie os diretórios compute_engine e dataproc para a raiz do seu bucket gerado no passo 2
6. Abra um terminal ou prompt de commando e execute os comandos abaixo


************************************************************************************************************************
### Subindo banco mysql para armazenar o metastore do hive (Cloud SQL)
```
gcloud sql instances create hive-metastore3 \
--database-version="MYSQL_5_7" \
--activation-policy=ALWAYS \
--zone us-east1-d
```

************************************************************************************************************************
### Subindo hive para disponibilizar o metastore para o presto
```
gcloud beta dataproc clusters create hive-cluster \
--scopes sql-admin \
--bucket fia-tcc-logs \
--region us-east1 \
--zone us-east1-b \
--single-node \
--master-machine-type e2-standard-2 \
--master-boot-disk-type pd-standard \
--master-boot-disk-size 30GB \
--image-version 1.4-debian9 \
--project fia-tcc \
--initialization-actions 'gs://goog-dataproc-initialization-actions-us-east1/cloud-sql-proxy/cloud-sql-proxy.sh' \
--metadata "hive-metastore-instance=fia-tcc:us-east1:hive-metastore3" \
--properties hive:hive.metastore.warehouse.dir=gs://fia-tcc-processed-zone/
```

Após executar o comando acima, acesse a UI do google cloud e recupere o IP da instância de compute engine chamada hive-cluster-m.
Com o IP em mãos acesse o arquivo abaixo e altere o parametro hive.metastore.uri

BigDataGcp/compute_engine/prestosql/etc/catalog/processed-zone.properties

************************************************************************************************************************
### Subindo o serviço do Kafka e redis em um Compute Engine (vm instances)
```
gcloud beta compute --project=fia-tcc instances create platform \
--zone=us-east1-b \
--machine-type=e2-standard-8 \
--metadata startup-script-url=gs://fia-tcc-configurations/compute_engine/init.sh \
--subnet=default \
--network-tier=PREMIUM \
--maintenance-policy=MIGRATE \
--image=ubuntu-2004-focal-v20200902 \
--image-project=ubuntu-os-cloud \
--boot-disk-size=100GB \
--boot-disk-type=pd-standard \
--boot-disk-device-name=kafka_disk \
--reservation-affinity=any \
--service-account sa-fia-tcc@fia-tcc.iam.gserviceaccount.com  \
--scopes https://www.googleapis.com/auth/cloud-platform \
--tags https-server
```

### Redirecione sua porta local para acesso a UI do presto
```gcloud compute ssh platform --project fia-tcc --zone us-east1-b -- -L 8080:localhost:8080```

### Redirecione sua porta local para acesso a UI do Airflow
```gcloud compute ssh platform --project fia-tcc --zone us-east1-b -- -L 8081:localhost:8081```

### Redirecione sua porta local para acesso a UI do Metabase
```gcloud compute ssh platform --project fia-tcc --zone us-east1-b -- -L 3000:localhost:3000```

### Redirecione sua porta local para acesso ao Mysql
```gcloud compute ssh platform --project fia-tcc --zone us-east1-b -- -L 3306:localhost:3306```

************************************************************************************************************************
##### Configurações na UI do airflow

- Alterar a connection google_cloud_default:

    ```
  project_id = fia-tcc
  Keyfile JSON = <Adicione o conteúdo do arquivo json gerado ao criar o usuário de serviço>
  scope = https://www.googleapis.com/auth/cloud-platform
  ```

 - Criar uma connection slack_conn com os valores:
    ```
    login: projeto-fia-tcc
    password: <Adicione o Bot User OAuth Access Token gerado ao criar o bot no slack>
    ```
   
Após as configurações das conexões, ative as três dags que aparecem na UI do airflow.
A dag fundamentus-stocks-stream iniciará automaticamente subindo um cluster e disparando um job spark streaming.
Aguarde até que o step chamado: inicia_spark_streaming; esteja no status running. Isso significa que o job já está consumindo o tópico do kafka.

Execute então a dag send-stocks-to-kafka, para que o web scrapper leia a página web e envie os dados para o tópico kafka.  
  
Com o comando abaixo você poderá acessar os dados salvos no bucket do GCS e no Redis via jupyter.
************************************************************************************************************************
### Criar um cluster com Jupyter Notebook para exploração dos dados
__no windows trocar ^ por ^^^^__
```
gcloud beta dataproc clusters create validation \
--enable-component-gateway \
--scopes sql-admin \
--bucket fia-tcc-logs \
--region us-east1 \
--zone us-east1-b \
--single-node \
--master-machine-type e2-standard-2 \
--master-boot-disk-type pd-standard \
--master-boot-disk-size 30GB \
--image-version 1.4-debian9 \
--optional-components ANACONDA,JUPYTER \
--project fia-tcc \
--initialization-actions 'gs://goog-dataproc-initialization-actions-us-east1/cloud-sql-proxy/cloud-sql-proxy.sh','gs://fia-tcc-configurations/dataproc/dataproc_init.sh' \
--metadata "hive-metastore-instance=fia-tcc:us-east1:hive-metastore3" \
--properties=^#^spark:spark.driver.core=1\
#spark:spark.driver.memory=2g\
#spark:spark.driver.memoryOverhead=1g\
#spark:spark.executor.cores=1\
#spark:spark.executor.instances=1\
#spark:spark.executor.memory=4g\
#spark:spark.executor.memoryOverhead=1g\
#spark:spark.debug.maxToStringFields=300\
#spark:spark.jars.packages=org.apache.spark:spark-streaming-kafka-0-8-assembly_2.11:2.4.5,com.redislabs:spark-redis:2.4.0\
#spark:spark.redis.host=10.142.0.56\
#spark:spark.redis.port=6379
```

Para conectar no jupyter, acesse a UI do seu projeto no google cloud platform  
 -> Depois, no menu principal lateral, entre em Google Dataproc  
 -> Acesse a configuração do seu cluster chamado "validation"  
 -> Então no menu interfaces web, click no link Jupyter  
 
************************************************************************************************************************