import json
import argparse
from io import StringIO
from google.cloud import storage
from pyspark.sql import types as st
from pyspark.sql import SparkSession
from pyspark.sql.window import Window
from pyspark.sql.functions import rank

# import sys; sys.argv=['']; del sys
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--source', type=str, help="Source's name of your dataset")
parser.add_argument('-d', '--dataset', type=str, help='Dataset to be processed')
parser.add_argument('-k', '--key', type=str, help='Row key to identify rows as unique')

args = parser.parse_args()
SOURCE = args.source
DATASET = args.dataset
KEY = args.key

storage_client = storage.Client()
bucket = storage_client.get_bucket('fia-tcc-configurations')
blob = bucket.get_blob(f'dataproc/required_fields/{SOURCE}/{DATASET}.json')
json_file = blob.download_as_string()
json_file_decoded = json_file.decode('utf-8')
json_stringio = StringIO(json_file_decoded)
json_schema = json.load(json_stringio)
dataset_schema = st.StructType.fromJson(json_schema)

spark = SparkSession \
    .builder \
    .appName("Hive_TCC") \
    .enableHiveSupport() \
    .getOrCreate()

spark.sql(f"CREATE DATABASE IF NOT EXISTS {SOURCE}")

window = Window.partitionBy(KEY).orderBy("process_date")

df_raw = spark.read.format('parquet').schema(dataset_schema).load(f'gs://fia-tcc-raw-zone/{SOURCE}/{DATASET}')
ranked = df_raw.withColumn("rank", rank().over(window))
df_processed = ranked.where('rank == 1').drop('rank')
df_processed.write.mode('overwrite').saveAsTable(f"{SOURCE}.{DATASET}")
