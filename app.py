import logging
logging.basicConfig(level= logging.INFO)
import helpers
import json
import controller
import init 

from kafka import KafkaConsumer, KafkaProducer
from json import loads

def multi():
    consumer = KafkaConsumer(
        init.mongodb_config["topic"],
        bootstrap_servers=init.mongodb_config["bootstrap_servers"],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='multinew-group',
        value_deserializer=lambda x: loads(x.decode('utf-8')))
    
    producer = KafkaProducer(bootstrap_servers=init.mongodb_config["bootstrap_servers"],
                         value_serializer=lambda x: json.dumps(x).encode('utf-8'))
    
    for message in consumer:
        message = message.value
        # database_name = message["database_name"]
        # collection_name = message["collection_name"]
        # full_doc = message["full_document"]
        # doc = loads(full_doc)
        
        id_mapAl_algoAI = "1"
        topic = init.find_algo_topic(id_mapAl_algoAI)
        producer.send(topic, message)
        
        
    # content = request.get_json()  
    # code = helpers.check_valid_input(content)
    # if code != 200:
    #     return {'result': {'cluster': [], 'topic': []}}
    # content = helpers.convert_b64_file_to_text(content)
    # # logging.info(content)
    # res = controller.summary(content)
    # logging.info("Response!!!!!!!!!!!!!!!!!!")
    # logging.info(res)
    # return json.dumps(res).encode('utf8')


if __name__ =="__main__":
    init.Initialize()
