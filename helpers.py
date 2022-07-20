import json
import requests
from multiprocessing import Process, Manager


def check_valid_input(dataInput):
    # check type
    try:
        if not isinstance(dataInput["raw_text"], list) or len(dataInput["raw_text"]) <=1:
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
    
    if cluster == False and len(topic.keys())==0:
        return 407
    return 200

def infer(manger,dataInput, url, key):
    res =  requests.post(url, json=dataInput)
    res = json.loads(res.content)

    manger[key] = {"result":res["result"], "code":res["code"]}
    
def test_mul_infer():
    manager = Manager()
    d = manager.dict()        
   
    dataInput ={
        "list_doc":[
            "Voters in 11 states will pick their governors tonight, and Republicans appear on track to increase their numbers by at least one, with the potential to extend their hold to more than two-thirds of the nation's top state offices.\nEight of the gubernatorial seats up for grabs are now held by Democrats; three are in Republican hands. Republicans currently hold 29 governorships, Democrats have 20, and Rhode Island's Gov. Lincoln Chafee is an Independent.\nPolls and race analysts suggest that only three of tonight's contests are considered competitive, all in states where incumbent Democratic governors aren't running again: Montana, New Hampshire and Washington.\nWhile those state races remain too close to call, Republicans are expected to wrest the North Carolina governorship from Democratic control, and to easily win GOP-held seats in Utah, North Dakota and Indiana.\nDemocrats are likely to hold on to their seats in West Virginia and Missouri, and are expected to notch safe wins in races for seats they hold in Vermont and Delaware.",
            "While the occupant of the governor's office is historically far less important than the party that controls the state legislature, top state officials in coming years are expected to wield significant influence in at least one major area.\nAnd that's health care, says political scientist Thad Kousser, co-author of The Power of American Governors.\n'No matter who wins the presidency, national politics is going to be stalemated on the Affordable Care Act,' says Kousser, of the University of California, San Diego.\nA recent U.S. Supreme Court decision giving states the ability to opt out of the law's expansion of Medicaid, the federal insurance program for poor, disabled and elderly Americans, confers 'incredible power' on the states and their governors, Kousser says.\nJust look at what happened when the Obama administration in 2010 offered federal stimulus money to states to begin building a high-speed rail network. Three Republican governors, including Rick Scott of Florida and Scott Walker of Wisconsin, rejected a share of the money citing debt and deficit concerns.\n'A [Mitt] Romney victory would dramatically empower Republican governors,' Kousser says."
        ],
        "percent_output":0.3
    }
    
    inputs = [dataInput, dataInput, dataInput, dataInput]
    
    url = "http://127.0.0.1:6688/extract"
    for idx, docs in enumerate(inputs):
        p = Process(target=infer, args=(d, inputs[idx],url, idx))
        p.start()
        p.join()

    print(d)

def check_contain(logic, text):
    assert(logic, list), "must be list logic to check valid"
    result = []
    for express_logic in logic:
        is_valid = True
        keywords = express_logic.split(',')
        for keyword in keywords:
            if not keyword.lower().rstrip() in text.lower():
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
    for idx, obj in enumerate(topics):
        logic = obj["logic"]
        elem_arr_valid = []
        for jdx, doc in enumerate(dataInput["raw_text"]):
            valid = check_valid_by_topic(logic, doc)
            if valid:
                elem_arr_valid.append(jdx)
        dataInput["topic"][idx].update({"elem_arr":elem_arr_valid})
    return dataInput
        
if __name__ == '__main__':
    data = {
        "raw_text":["abc a fg", "bdcd a b dfdanc", "a bc cd"],
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
    print(cluster_topics(data))
    