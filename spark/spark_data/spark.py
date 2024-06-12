from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from pyspark.sql.functions import col, sum as spark_sum, date_format, to_date

spark = SparkSession.builder.appName('Join Parquet and CSV').getOrCreate()

csv_schema = StructType([
    StructField("id", StringType(), True),
    StructField("student_name", StringType(), True)
])

csv_file_path = 'hdfs://namenode:9000/raw_zone/fact/danh_sach_sv_de.csv'
csv_df = spark.read.csv(csv_file_path, header=False, schema=csv_schema)

parquet_file_path = 'hdfs://namenode:9000/raw_zone/fact/activity/'
parquet_df = spark.read.parquet(parquet_file_path)
print("CSV Schema:")
csv_df.printSchema()
print("Parquet Schema:")
parquet_df.printSchema()

joined_df = parquet_df.join(csv_df, parquet_df['student_code'] == csv_df['id'], 'full')
formatted_df = joined_df.withColumn('date', date_format(to_date(col('timestamp'), 'M/dd/yyyy'), 'yyyyMMdd'))

num =formatted_df.count()
print("num record: ",num)

aggregated_df = formatted_df.groupBy(
    col('date'),
    col('student_code'),
    col('student_name'),
    col('activity')
).agg(
    spark_sum(col('numberOfFile')).alias('totalFile')
)

aggregated_df.write.option("header",True).option("delimiter",",").mode("overwrite").csv("output")
spark.stop()