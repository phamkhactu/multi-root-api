
import json 
from pymongo import MongoClient
import urllib
import json


import urllib.parse
from pymongo import MongoClient
from sys import exit

my_conn, my_db =None, None



def Initialize():
    with open("configs.json", "r") as r:
        mongodb_config = json.load(r)
    global my_conn, my_db
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
        