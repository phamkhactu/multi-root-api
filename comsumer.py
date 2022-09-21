from kafka import KafkaConsumer, KafkaProducer
from json import loads
import init
import json

consumer = KafkaConsumer(
    'test_meeymap',
    bootstrap_servers=["b-1.meeyland-test.ketxgx.c3.kafka.ap-southeast-1.amazonaws.com:9092",
                        "b-2.meeyland-test.ketxgx.c3.kafka.ap-southeast-1.amazonaws.com:9092",
                        "b-3.meeyland-test.ketxgx.c3.kafka.ap-southeast-1.amazonaws.com:9092"],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='multinew-group',
    value_deserializer=lambda x: loads(x.decode('utf-8')))

producer = KafkaProducer(bootstrap_servers=init.mongodb_config["bootstrap_servers"],
                        value_serializer=lambda x: json.dumps(x).encode('utf-8'))


for message in consumer:
    message = message.value
    database_name = message["database_name"]
    collection_name = message["collection_name"]
    full_doc = message["full_document"]
    doc = loads(full_doc)