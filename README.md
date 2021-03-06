### Pré requisitos para execução dos scripts

1. Crie um login no [google cloud plataform](https://cloud.google.com/) 
    1. Adicione um projeto chamado *fia-tcc*. [Veja como!](https://cloud.google.com/resource-manager/docs/creating-managing-projects#creating_a_project)
    2. Habilite a cobrança em um cartão de crédito, caso contrário não será possível utilizar máquinas com mais de 1 processador.
2. Crie 4 buckets necessários para o projeto: *fia-tcc-configurations*, *fia-tcc-logs*, *fia-tcc-processed-zone*, *fia-tcc-raw-zone*. [Veja como!](https://cloud.google.com/storage/docs/creating-buckets)
3. Acesse a página de [service account](https://console.cloud.google.com/iam-admin/serviceaccounts), escolha o projeto criado no primeiro passo e crie uma nova SA  
chamada *sa-fia-tcc* com permissão de **Project Editor**.
   1. Após a criação da SA, ainda na página, vá em *actions* e escolha *create key* com a opção de chave **Json**.  
   2. Salve o arquivo json para uso futuro na criação de conexão no airflow.
4. Instale e configure o sdk do google (gsutils) na sua máquina, para acessar a suca conta. [Veja como!](https://cloud.google.com/storage/docs/gsutil_install) 
5. Copie os diretórios *compute_engine* e *dataproc* para a raiz do bucket *fia-tcc-configurations*.
    ```
    > gsutil -m cp -r ./compute_engine gs://fia-tcc-configurations/
    > gsutil -m cp -r ./dataproc gs://fia-tcc-configurations/
    ```
7. Abra um terminal ou prompt de commando e execute os comandos abaixo.


************************************************************************************************************************
### Subindo banco mysql para armazenar o metastore do hive (Cloud SQL)
```
    > gcloud sql instances create hive-metastore \
    --database-version="MYSQL_5_7" \
    --activation-policy=ALWAYS \
    --zone us-east1-d 
```
Obs: Aguarde a finalização, antes de executar o próximo script.
************************************************************************************************************************
### Subindo hive para disponibilizar o metastore para o presto
```
    > gcloud beta dataproc clusters create hive-cluster \
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
    --metadata "hive-metastore-instance=fia-tcc:us-east1:hive-metastore" \
    --properties hive:hive.metastore.warehouse.dir=gs://fia-tcc-processed-zone/
```

************************************************************************************************************************
### Subindo os serviços de Airflow, Kafka, Redis, prestoSql e Metabase
O webscraper está incluído no airflow como uma dag.
```
    > gcloud beta compute --project=fia-tcc instances create platform \
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
    --boot-disk-device-name=platform_disk \
    --reservation-affinity=any \
    --service-account sa-fia-tcc@fia-tcc.iam.gserviceaccount.com  \
    --scopes https://www.googleapis.com/auth/cloud-platform \
    --tags https-server
```

Para acompanhar o término do script de inicialização, você pode acessar a máquina via ssh e acompanhar o log:

```
    > gcloud compute ssh platform --project fia-tcc --zone us-east1-b
    > tail -f /var/log/syslog
```

************************************************************************************************************************
Após subir todos os serviços necessário para nossa ingestão, processamento streaming e apresentação dos dados,  
precisamos fazer apenas algumas configurações de conexões:

1. Conexão PrestoSQL -> Hive Metastore:
   * Primeiro vamos recuperar o IP interno do nosso hive metastore através desse [link](https://console.cloud.google.com/compute/instancesDetail/zones/us-east1-b/instances/hive-cluster-m) para conectar o prestoSQL.
   *  Acesse a máquina via ssh com o comando abaixo (ou utilize o terminal de abertura dos túneis)

      ```> gcloud compute ssh platform --project fia-tcc --zone us-east1-b ```
   * Acesse o usuário root com o comando: `sudo su -`  
   * Altere o parametro hive.metastore.uri no arquivo de configuração de catálogo do presto  
   adicionando o IP interno do hive metastore recuperado no primeiro passo:
      
      ```> vim ~/compute_engine/prestosql/etc/catalog/processed-zone.properties ```
   * Pronto vamos para o próximo passo

2. Conexão PrestoSQL -> Kafka:
   * Assim como para o hive metastore, iremos recuperar o IP interno da máquina, na qual o kafka está instalado,  
   através desse [link](https://console.cloud.google.com/compute/instancesDetail/zones/us-east1-b/instances/platform).
   * Altere o parametro kafka.nodes no arquivo de configuração de catálogo do presto  
   adicionando o IP interno recuperado no passo anterior e a porta default do kafka (9092):
      
      ```> vim ~/compute_engine/prestosql/etc/catalog/kafka.properties ```
 
3. Acesse o diretório compute engine e reinicie os serviços que estão rodando com docker-compose:
      ``` 
        > cd ~/compute_engine/ 
        > docker-compose down
        > docker-compose up --force-recreate --build -d
        > exit
        > exit
      ```

Para executar os comandos abaixo, abra novos terminais ou prompt de comando e execute um em cada janela.
************************************************************************************************************************
##### Redirecione sua porta local para acesso a UI do presto
```
    > gcloud compute ssh platform --project fia-tcc --zone us-east1-b -- -L 8080:localhost:8080
```

##### Redirecione sua porta local para acesso a UI do Airflow
```
    > gcloud compute ssh platform --project fia-tcc --zone us-east1-b -- -L 8081:localhost:8081
```

##### Redirecione sua porta local para acesso a UI do Metabase
```
    > gcloud compute ssh platform --project fia-tcc --zone us-east1-b -- -L 3000:localhost:3000
```

##### Redirecione sua porta local para acesso ao Mysql (passo opcional)
```
    > gcloud compute ssh platform --project fia-tcc --zone us-east1-b -- -L 3306:localhost:3306
```

Com os tuneis abertos, você já deve conseguir acessar as UIs disponíveis, sendo elas:

| Ferramenta | UI |
| :--- | :---: |
| Airflow | http://localhost:8081 |
| Metabase | http://localhost:3000 |
| PrestoSQL | http://localhost:8080 |


## Configurações na UI do airflow

- Crie uma connection chamada **google_cloud_default** com os valores abaixo:

    | Campo             | Valor |
    | :---             | :--- |
    | Conn Type         | Google Cloud Platform|
    | Project Id        | fia-tcc |
    | Keyfile JSON      | Adicione o conteúdo do arquivo json gerado ao criar o usuário de serviço|
    | Scopes            | https://www.googleapis.com/auth/cloud-platform |

- Crie uma connection chamada **kafka** com os valores abaixo:

    | Campo  | Valor |
    | :---:  | :---: |
    | Host   | IP interno recuperado no passo "Conexão PrestoSQL -> Kafka"|

 - Criar uma connection **slack_conn** com os valores abaixo:
 
    | Campo     | Valor |
    | :---     | :---: |
    | Login     | Adicione um canal default para receber seus alertas |
    | Password  | Adicione o Bot User OAuth Access Token gerado ao criar o bot no slack |  

************************************************************************************************************************  
- Após as configurações das conexões, ative as três dags que apareceram na UI do airflow.  
- A dag *fundamentus-stock-stream* iniciará automaticamente, subindo um cluster e disparando um job spark streaming.  
- Aguarde até que o step *inicia_spark_streaming*, dessa mesma dag, esteja no status running. Isso significa  
que o spark já está consumindo o tópico do kafka definido no yaml.
- Execute então a dag send-stocks-to-kafka, para que o web scrapper leia a página web e envie os dados  para o  
tópico kafka definido no yaml.
  
Com o comando abaixo você poderá acessar os dados salvos no bucket do GCS e no Redis via jupyter.
************************************************************************************************************************

## Configurações na UI do Metabase
Ao acessar a UI do metabase, você precisará fazer um *set up* para acessar as funcionalidades do mesmo.  
Você pode fazer o set up seguindo os passos desse [link](https://www.metabase.com/docs/latest/setting-up-metabase.html) da documentação oficial.

No segundo passo você pode configurar a conexão com o database, que será sua fonte para análises.  
Vamos então conecta-lo ao nosso serviço de presto, preenchendo os campos com os valores abaixo:

|  |  |
| :--- | :--- |
| Type: | Presto |
| Name: | Identificador da origem de sua preferência |
| Host: | prestosql.lake_network |
| Port: | 8080 |
| Database Name: | kafka |
| Database User Name: | usr_metabase |
| Database Password: | Não é necessário |


************************************************************************************************************************

### Criar um cluster com Jupyter Notebook para exploração dos dados
__no windows trocar ^ por ^^^^__
```
    > gcloud beta dataproc clusters create validation \
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
    --metadata "hive-metastore-instance=fia-tcc:us-east1:hive-metastore" \
    --properties=^#^spark:spark.driver.core=1\
    #spark:spark.driver.memory=2g\
    #spark:spark.driver.memoryOverhead=1g\
    #spark:spark.executor.cores=1\
    #spark:spark.executor.instances=1\
    #spark:spark.executor.memory=4g\
    #spark:spark.executor.memoryOverhead=1g\
    #spark:spark.debug.maxToStringFields=300\
    #spark:spark.jars.packages=org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.5,com.redislabs:spark-redis:2.4.0\
    #spark:spark.redis.host=<IP Interno da instância platform>\
    #spark:spark.redis.port=6379
```
************************************************************************************************************************
#### Acessando o Jupyter Notebook:

- Acesse seu cluster criado acima através desse [link](https://console.cloud.google.com/dataproc/clusters/validation) 
- Acessa a aba *Interfaces Web* e então click no link *Jupyter*.  
    Aparecerá uma janela com link de redirecionamento, click nele e o jupyter notebook está pronto para uso.
- Já na UI do jupyter, aparecerá a opção de acessar os notebook do bucket como um diretório chamado *GCS*.  
    Clicando nele veremos o notebook que carregamos no passo iniciais (passo 6).
************************************************************************************************************************