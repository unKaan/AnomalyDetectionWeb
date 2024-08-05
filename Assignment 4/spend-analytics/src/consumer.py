from kafka import KafkaConsumer
import json
import duckdb

import sys

sys.path.append('../../src')
from src import AnomalyDetect

consumer = KafkaConsumer('spend_data', bootstrap_servers='localhost:9092',api_version=(3,7,1), value_deserializer=lambda m: json.loads(m.decode('utf-8')),    metadata_max_age_ms=300000,
                         request_timeout_ms=300000)

duckdb.sql('''
CREATE TABLE IF NOT EXISTS spend_data (
    Key INT PRIMARY KEY,
    Changed_On DATE,
    PO_Quantity FLOAT,
    Net_Value FLOAT,
    Category VARCHAR,
    Net_Price FLOAT,
    risk_flag BOOLEAN
)
''')
duckdb.sql("CREATE SEQUENCE IF NOT EXISTS purchase START 1")

for message in consumer:
    data = message.value
    data['Net_Price'] = data['Net_Value'] / data['PO_Quantity']
    risk_flag = AnomalyDetect(data)
    data['risk_flag'] = risk_flag

    query = f"""
    INSERT INTO spend_data (Key, Changed_On, PO_Quantity, Net_Value, Category, Net_Price, risk_flag)
    VALUES (nextval('purchase'), '{data['Changed_On']}', {data['PO_Quantity']}, {data['Net_Value']}, '{data['Category']}', {data['Net_Price']}, {data['risk_flag']})
    """
    duckdb.sql(query)

    print(f"Data inserted with risk_flag={risk_flag}")
