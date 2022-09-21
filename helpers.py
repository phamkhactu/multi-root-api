from cmath import log
import json
import requests
from multiprocessing import Process, Manager
import logging
logging.basicConfig(level=logging.INFO)
import base_64 

def check_valid_input(dataInput):
    # check type
    try:
        if not isinstance(dataInput["raw_text"], list) or len(dataInput["raw_text"]) <1:
            return 404
    except:
        return 404
    
    try:
        if not isinstance(dataInput["topic"], list):
            return 401
    except:
        return 401

    try:
        if not isinstance(dataInput["id_mapAlgTypeAI"], list) or len(dataInput["id_mapAlgTypeAI"]) !=1 :
            return 402
    except:
        return 402
    
    try:
        percent_output = float(dataInput["percent_output"])
        if  not 0 < percent_output <=1:
            return 403
    except:
        return 403
    
    try:
        if not isinstance(dataInput["cluster"], bool) :
            return 405
    except:
        return 405
    
    try:
        if not isinstance(dataInput["file_type"], list) or len(dataInput["file_type"]) != len(dataInput["raw_text"]):
            return 408
        for _type in dataInput["file_type"]:
            try:
                int(_type)
            except:
                return 408
    except:
        return 408
    
    
    # only cluster or topic to summary doc 
    cluster = dataInput["cluster"]
    topic = dataInput["topic"]
    
    
    if cluster:
        if len(topic)>0:
            # also cluster and also topic
            return 406
    else:
        if len(topic)==0:
            return 401
        try:
            for obj in topic:
                topic_keys = obj.keys()
                if len(topic_keys) ==0:
                    return 401
                else:
                    if len(obj["logic"]) !=2:
                        return 401
        except:
            return 401
    
    if cluster == False and len(topic)==0:
        return 407
    return 200

def infer(manger,dataInput, url, key):
    # check if empty input after cluster or topic
    if len(dataInput["list_doc"])==0:
        manger[key] = {"result":None}
    else:
        res=  requests.post(url, json=dataInput)
        code = res.status_code
        if code !=200:
            logging.error(f"{code} status code in {url}")
            manger[key] = {"result":None}
        else:
            res = json.loads(res.content)
            manger[key] = {"result":res["result"]}
    
def mul_infer(inputs, url):
    manager = Manager()
    d = manager.dict()        
    
    for idx, docs in enumerate(inputs):
        p = Process(target=infer, args=(d, inputs[idx],url, idx))
        p.start()
        p.join()
        
    return d

def check_contain(logic, text):
    # assert(logic, list), "must be list logic to check valid"
    result = []
    for express_logic in logic:
        is_valid = True
        keywords = express_logic.split(',')
        for keyword in keywords:
            if not keyword.lower().strip() in text.lower():
                is_valid= False
                break
        result.append(is_valid)
    return any(result)

def check_valid_by_topic(logic_topic,text):
    topic_choose = logic_topic[0]
    topic_not = logic_topic[1]
    
    #check if contain True logic not in text =>False not valid
    if check_contain(topic_not, text):
        return False
    
    # check if contain True in logic And or => True valid
    if check_contain(topic_choose, text):
        return True
    # else False
    return False

def cluster_topics(dataInput):
    topics = dataInput["topic"]
    # logging.info(f"topics logics {topics}")
    for idx, obj in enumerate(topics):
        logic = obj["logic"]
        logging.info(f"topic : {logic}")
        elem_arr_valid = []
        for jdx, doc in enumerate(dataInput["raw_text"]):
            valid = check_valid_by_topic(logic, doc)
            if valid:
                elem_arr_valid.append(jdx)
        dataInput["topic"][idx].update({"elem_arr":elem_arr_valid})
    return dataInput
    
def pre_data_cluster(dataInput, list_cluster):
    percent_output = dataInput["percent_output"]
    raw_data = dataInput["raw_text"]
    inputs =[]
    for cluster in list_cluster:
        list_text_raw = []
        for idx in cluster:
            list_text_raw.append(raw_data[idx])
        inputs.append(
            {
            "list_doc":list_text_raw,
            "percent_output":percent_output
        })
        
    return inputs

def get_pharagraph_topic(doc, logic_topic):
    topic_choose = logic_topic[0]
    pharagraphs = doc.split("\n")
    text = ""
    for phara in pharagraphs:
        for logic in topic_choose:
            if logic.lower() in phara.lower():
                text += phara +"\n"
                break
    return text

def pre_data_topic(dataInput):
    dataInput = cluster_topics(dataInput)
    inputs = []
    topics = dataInput["topic"]
    for top in topics:
        elem_arr = top["elem_arr"]
        list_text_raw = []
        for elem in elem_arr:
            list_text_raw.append(get_pharagraph_topic(dataInput["raw_text"][elem], top["logic"]))
        inputs.append(
            {
            "list_doc":list_text_raw,
            "percent_output":dataInput["percent_output"]
        })
        
    return inputs

def convert_b64_file_to_text(dataInput):
    raw_data_files = dataInput["raw_text"]
    # for idx, raw_data in enumerate(raw_data_files):
    #     with open(f"dx{idx}.txt", "w") as w:
    #         w.write(raw_data)
    file_types = dataInput["file_type"]
    for idx, data_file in enumerate(raw_data_files):
        r_text = base_64.get_raw_text(data_file,int(file_types[idx]),0,99999)
        dataInput["raw_text"][idx] = r_text
    
    return dataInput
    
    
if __name__ == '__main__':
    data = {
        "raw_text":["abc\n a\n fg\n", "bdcd\n a\n b\n dfdanc\n", "a\n bc\n cd\n"],
        "topic": [
        {
            "logic":[["A","B"],["C"]],
            "displayName":"tên topic"
        },
        {
            "logic":[["A","B","C"],["D"]],
            "displayName":"tên topic"
        }
        ],
        "id_mapAlgTypeAI" :[1],
        "percent_output": 0.3,
        "cluster": False
        }
    # data = cluster_topics(data)
    # print(data)
    print(pre_data_topic(data))
    # raw="While the occupant of the governor's office is historically far less important than the party that controls the state legislature, top state officials in coming years are expected to wield significant influence in at least one major area.\nAnd that's health care, says political scientist Thad Kousser, co-author of The Power of American Governors.\n'No matter who wins the presidency, national politics is going to be stalemated on the Affordable Care Act,' says Kousser, of the University of California, San Diego.\nA recent U.S. Supreme Court decision giving states the ability to opt out of the law's expansion of Medicaid, the federal insurance program for poor, disabled and elderly Americans, confers 'incredible power' on the states and their governors, Kousser says.\nJust look at what happened when the Obama administration in 2010 offered federal stimulus money to states to begin building a high-speed rail network. Three Republican governors, including Rick Scott of Florida and Scott Walker of Wisconsin, rejected a share of the money citing debt and deficit concerns.\n'A [Mitt] Romney victory would dramatically empower Republican governors"
    
    # raw_data = [raw, raw, raw, raw, raw, raw,raw]
    # list_cluster = [[0,1,2],[3,4,2]]
    
    # inputs = pre_data(raw_data, topics[""])
    # d = mul_infer(inputs, url="http://192.168.6.18:8899/extract")
    # print(d)