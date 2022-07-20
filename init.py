
import json
from bson import ObjectId 
from pymongo import MongoClient
import urllib
import json


import urllib.parse
from pymongo import MongoClient
from sys import exit

my_conn, my_db, mongodb_config =None, None, None



def Initialize():
    global my_conn, my_db, mongodb_config
    with open(".env", "r") as r:
        mongodb_config = json.load(r)
    
    username_rh = urllib.parse.quote_plus(mongodb_config['username'].strip())
    password_rh = urllib.parse.quote_plus(mongodb_config['password'].strip())
    if username_rh!="" and password_rh!="":
        connection_string='mongodb://%s:%s@%s:%s/%s?authSource=admin' % (username_rh, password_rh,
                mongodb_config['host'],mongodb_config['port'],
                mongodb_config['auth_database'])
    else:
            connection_string='mongodb://%s:%s/%s' % (mongodb_config['host'],
                            mongodb_config['port'], mongodb_config['auth_database'])
    try:
        my_conn=MongoClient(connection_string, maxPoolSize=5000)
        my_db=my_conn[mongodb_config['database']]
        my_conn.admin.command('ismaster')
    except:
        print("Mongo Connection Error")
        exit(1)

def find_algo_url(id_mapAl_algoAI):
    url = None
    # try:
    mapAl_algo_ai = my_db[mongodb_config["mapAlgTypeAI_collection"]].find({"id":id_mapAl_algoAI})
    id_algorithm = list(mapAl_algo_ai)[0]["algorId"]
    url = list(my_db[mongodb_config["algorithm_collection"]].find({"algorId":id_algorithm}))[0]["urlAPI"]
    # except:
    #     pass
    return url

if __name__ =="__main__":
    Initialize()
    print(find_algo_url(17))