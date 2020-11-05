import json
import argparse
from io import StringIO
from google.cloud import storage
from pyspark.sql import SparkSession
from pyspark.sql import types as st
from pyspark.sql import functions as sf

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--source', type=str, help="Source's name of your dataset")
parser.add_argument('--host', type=str, help='IP where your kafka server is running.')
parser.add_argument('-t', '--topic', type=str, help='A topic to be read from kafka server.')
parser.add_argument('-k', '--key', type=str,
                    help="Key name into your message that will be used to group data into the same dataset")

args = parser.parse_args()
SOURCE = args.source
KAFKA_HOST = args.host
KAFKA_TOPIC = args.topic
KEY_FIELD = args.key

print(f'KAFKA_HOST={KAFKA_HOST}')
print(f'KAFKA_TOPIC={KAFKA_TOPIC}')
print(f'KEY_FIELD={KEY_FIELD}')
# SOURCE = 'fundamentus'
# KAFKA_HOST = '10.142.15.222'
# KAFKA_TOPIC = 'stock'
# KEY_FIELD = 'papel'

class Error(Exception):
    pass


class DataFrameHasUnexpectedColumnError(Error):
    pass


class DataFrameRequiredColumnError(Error):
    pass


def validate_unexpected_columns(df, df_schema):
    all_col_names = df.columns
    unexpected_columns = [column for column in all_col_names if column not in df_schema.fieldNames()]
    if unexpected_columns:
        raise DataFrameHasUnexpectedColumnError(
            f"The {unexpected_columns} columns are not expected in this Dataframe, check your Dataframe Schema")


def validate_required_columns(df, df_schema):
    required_columns = [struct_type.name for struct_type in df_schema.fields if not struct_type.nullable]
    for column in required_columns:
        null_quant = df.filter(sf.col(column).isNull()).count()
        if null_quant > 0:
            raise DataFrameRequiredColumnError(f'Column {column} is required and cannot have null values.')


def get_required_fields():
    storage_client = storage.Client()
    bucket = storage_client.get_bucket('fia-tcc-configurations')
    blob = bucket.get_blob(f'dataproc/required_fields/{SOURCE}/{KAFKA_TOPIC}.json')
    json_file = blob.download_as_string()
    json_file_decoded = json_file.decode('utf-8')
    json_stringio = StringIO(json_file_decoded)
    json_schema = json.load(json_stringio)
    schema = st.StructType.fromJson(json_schema)
    return schema


REQUIRED_FIELDS = get_required_fields()

spark = SparkSession.builder.getOrCreate()

df_kafka = spark.readStream.format("kafka")\
    .option("subscribe", f"{KAFKA_TOPIC}")\
    .option("kafka.bootstrap.servers", f"{KAFKA_HOST}:9092")\
    .option("includeHeaders", "true")\
    .option("startingOffsets", "earliest")\
    .option("groupId", "datalakeConsumer")\
    .load()

df_kafka_json = df_kafka.selectExpr("CAST(value AS STRING)")


def validate_save_data(df, epoch_id):
    df_schema = spark.read.json(df.rdd.map(lambda row: row['value'])).schema
    df_raw = df.select(sf.from_json(sf.col("value"), df_schema).alias('data')).select("data.*")
    if df_raw.head(1):
        try:
            df_raw.show()
            validate_required_columns(df_raw, REQUIRED_FIELDS)
            validate_unexpected_columns(df_raw, REQUIRED_FIELDS)
            for column in df_raw.columns:
                df_raw = df_raw.withColumn(column, sf.col(column).cast(REQUIRED_FIELDS[column].dataType))

            # Write to redis
            df_raw.write.format("org.apache.spark.sql.redis")\
                .option("table", f"{SOURCE}.{KAFKA_TOPIC}")\
                .option("key.column", KEY_FIELD)\
                .save(mode='append')

            # Write to datalake bucket
            df_raw.write.format("parquet")\
                .save(path=f"gs://fia-tcc-raw-zone/{SOURCE}/{KAFKA_TOPIC}/",
                      partitionBy=f"{KEY_FIELD}",
                      mode="append")
        except DataFrameRequiredColumnError as err:
            # Write to kafka falback topic
            df.write.format("kafka")\
                .option("topic", f"{KAFKA_TOPIC}Fallback")\
                .option("kafka.bootstrap.servers",f"{KAFKA_HOST}:9092")\
                .save(mode="append")
        except DataFrameHasUnexpectedColumnError as err:
            # Write to kafka falback topic
            df.write.format("kafka")\
                .option("topic", f"{KAFKA_TOPIC}Fallback")\
                .option("kafka.bootstrap.servers", f"{KAFKA_HOST}:9092")\
                .save(mode="append")


query = df_kafka_json.writeStream.outputMode("append")\
    .option("checkpointLocation", f"gs://fia-tcc-raw-zone/checkpoint/{SOURCE}/{KAFKA_TOPIC}/")\
    .foreachBatch(validate_save_data)\
    .trigger(processingTime='2 seconds')

query.start().awaitTermination()
