import argparse
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

spark = SparkSession \
    .builder \
    .appName("Hive_TCC") \
    .enableHiveSupport() \
    .getOrCreate()

window = Window.partitionBy(KEY).orderBy("process_date")

df_teste = spark.read.parquet(f'gs://fia-tcc-raw/{SOURCE}/{DATASET}')
ranked = df_teste.withColumn("rank", rank().over(window))
df_final = ranked.where('rank == 1').drop('rank')
df_final.write.mode('overwrite').saveAsTable(f"{SOURCE}_{DATASET}")
