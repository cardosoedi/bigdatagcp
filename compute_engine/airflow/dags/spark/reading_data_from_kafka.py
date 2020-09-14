# coding: utf-8
import argparse
import json
from kafka import KafkaProducer
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark.sql import functions as sf
from pyspark.sql import Row
import quinn
from quinn.dataframe_validator import DataFrameMissingColumnError

parser = argparse.ArgumentParser()
parser.add_argument('--host', type=str, help='IP where your kafka server is running.')
parser.add_argument('-t', '--topic', type=str, help='A topic to be read from kafka server.')
parser.add_argument('-k', '--key', type=str,
                    help="Key name into your message that will be used to group data into the same dataset")

args = parser.parse_args()
KAFKA_HOST = args.host
KAFKA_TOPIC = args.topic
KEY_FIELD = args.key

print(f'KAFKA_HOST={KAFKA_HOST}')
print(f'KAFKA_TOPIC={KAFKA_TOPIC}')
print(f'KEY_FIELD={KEY_FIELD}')

# KAFKA_HOST = '10.142.0.14'
# KAFKA_TOPIC = 'Stocks'
# KEY_FIELD = 'papel'


sc = SparkContext(appName="Kafka_TCC").getOrCreate()
spark = SparkSession(sc)
sc.setLogLevel('WARN')
ssc = StreamingContext(sc, 2)

producer = KafkaProducer(bootstrap_servers=[f'{KAFKA_HOST}:9092'],
                         value_serializer=lambda x: json.dumps(x).encode('utf-8'))


def get_required_fields():
    df_required_fields = spark.read.option('header', 'true').csv(
        f'gs://<your-gcs-bucket-name>/dataproc/required_fields/{KAFKA_TOPIC}.csv')
    rows = df_required_fields.collect()
    required_fields = [row.column_name for row in rows]
    return required_fields


def get_spark_session_instance(spark_conf):
    if "sparkSessionSingletonInstance" not in globals():
        globals()["sparkSessionSingletonInstance"] = SparkSession.builder.config(conf=spark_conf).getOrCreate()
    return globals()["sparkSessionSingletonInstance"]


def send_kafka(message):
    records = message.collect()
    for record in records:
        producer.send(f'{KAFKA_TOPIC}Fallback', json.loads(record))
        producer.flush()


REQUIRED_FIELDS = get_required_fields()


def process(rdd):
    try:
        if not rdd.isEmpty():
            for row in rdd.collect():
                df_s3 = sc.parallelize([row]).toDF()
                try:
                    quinn.validate_presence_of_columns(df_s3, REQUIRED_FIELDS)
                    df_s3.write.format("org.apache.spark.sql.redis") \
                        .option("table", KAFKA_TOPIC) \
                        .option("key.column", KEY_FIELD) \
                        .save(mode='append')
                    df_s3.write.format('parquet') \
                        .save(f'gs://<your-gcs-bucket-name>/dataproc/datasets/{KAFKA_TOPIC}/',
                              mode='append',
                              partitionBy=KEY_FIELD)
                except DataFrameMissingColumnError as err:
                    df_kafka_fallback = df_s3.withColumn('error', sf.lit(err))
                    send_kafka(df_kafka_fallback.toJSON())
    except ValueError:
        pass


# kafkaStream = KafkaUtils.createStream(ssc, f'{KAFKA_HOST}:2181', groupId='parser', topics={KAFKA_TOPIC: 1})
kafkaStream = KafkaUtils.createDirectStream(ssc, [f"{KAFKA_TOPIC}"], {"metadata.broker.list": f"{KAFKA_HOST}:9092"})
kafkaStream.map(lambda kafka_message: json.loads(kafka_message[1])).map(lambda x: Row(**x)).foreachRDD(process)
ssc.start()
ssc.awaitTermination()
