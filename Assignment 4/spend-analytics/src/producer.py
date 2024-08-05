from kafka import KafkaProducer
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    api_version=(3, 7, 1),
    metadata_max_age_ms=30000,
    request_timeout_ms=30000
)

def produce_data(data):
    future = producer.send('spend_data', data)
    result = future.get(timeout=10)
    logger.info(f"Message sent to topic {result.topic}, partition {result.partition}, offset {result.offset}")

# Example
data = {
    'Changed_On': '2023-01-01',
    'PO_Quantity': 100,
    'Net_Value': 5000,
    'Category': 'mechanical components'
}
produce_data(data)

# cd src
# cd kafka_2.12-3.7.1
# bin/zookeeper-server-start.sh config/zookeeper.properties
# bin/kafka-server-start.sh config/server.properties
# bin/kafka-topics.sh --create --topic spend_data --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
