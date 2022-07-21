import helpers
import init
import logging
import requests
import json
logging.basicConfig(level=logging.INFO)

def summary(dataInput):
    cluster = dataInput["cluster"]
    id_mapAlgTypeAI = dataInput["id_mapAlgTypeAI"]
    try:
        id_mapAlgTypeAI = int(id_mapAlgTypeAI[0])
    except:
        logging.info("id_mapAlgTypeAI must int")
        return {"result":None}, 500

    url_algo = init.find_algo_url(id_mapAlgTypeAI)
    # url_algo = "http://192.168.6.18:8899/extract"
    if url_algo is None:
        logging.info("Can not find url algorithm")
        return {"result":None}, 500
    
    try:
        percent_output = float(dataInput["percent_output"])
    except:
        dataInput.update({"percent_output":0.3})
        
    if cluster:
        url_cluster = init.configs["url_cluster"]
        res = requests.post(url_cluster, json={"list_doc":dataInput["raw_text"]})
        code = res.status_code
        list_cluster = json.loads(res.content)["clusters"]
        # list_cluster, code =[[0,1],[1,2]],200
        if code!=200:
            logging.info("err call api cluster")
            return {"result":None}, 500
        inputs = helpers.pre_data_cluster(dataInput, list_cluster)
        dic_res = helpers.mul_infer(inputs,url_algo)
        result = {
            "result":
                {
                "cluster": [],
                "topic": []
                }
            }
        keys = dic_res.keys()
        for k in keys:
            result["result"]["cluster"].append(
                 {
                    "text": dic_res[k]["result"],
                    "displayName": f"Cụm {k}",
                    "elem_arr": list_cluster[k]
                    },
            )
        return result, 200
    inputs = helpers.pre_data_topic(dataInput)
    dic_res = helpers.mul_infer(inputs,url_algo)
    result={"result":
                {
                    "cluster": [],
                    "topic": []
                }
            }
    
    keys = dic_res.keys()
    for k in keys:
        result["result"]["topic"].append(
                {
                    "text": dic_res[k]["result"],
                    "displayName": dataInput["topic"][k]["displayName"],
                    "elem_arr": dataInput["topic"][k]["elem_arr"]
                },
        )
    return result, 200

if __name__ == '__main__':
    dataInput={
        "raw_text":[
            "Voters in 11 states will pick their governors tonight, and Republicans appear on track to increase their numbers by at least one, with the potential to extend their hold to more than two-thirds of the nation's top state offices.\nEight of the gubernatorial seats up for grabs are now held by Democrats; three are in Republican hands. Republicans currently hold 29 governorships, Democrats have 20, and Rhode Island's Gov. Lincoln Chafee is an Independent.\nPolls and race analysts suggest that only three of tonight's contests are considered competitive, all in states where incumbent Democratic governors aren't running again: Montana, New Hampshire and Washington.\nWhile those state races remain too close to call, Republicans are expected to wrest the North Carolina governorship from Democratic control, and to easily win GOP-held seats in Utah, North Dakota and Indiana.\nDemocrats are likely to hold on to their seats in West Virginia and Missouri, and are expected to notch safe wins in races for seats they hold in Vermont and Delaware.",
            "While the occupant of the governor's office is historically far less important than the party that controls the state legislature, top state officials in coming years are expected to wield significant influence in at least one major area.\nAnd that's health care, says political scientist Thad Kousser, co-author of The Power of American Governors.\n'No matter who wins the presidency, national politics is going to be stalemated on the Affordable Care Act,' says Kousser, of the University of California, San Diego.\nA recent U.S. Supreme Court decision giving states the ability to opt out of the law's expansion of Medicaid, the federal insurance program for poor, disabled and elderly Americans, confers 'incredible power' on the states and their governors, Kousser says.\nJust look at what happened when the Obama administration in 2010 offered federal stimulus money to states to begin building a high-speed rail network. Three Republican governors, including Rick Scott of Florida and Scott Walker of Wisconsin, rejected a share of the money citing debt and deficit concerns.\n'A [Mitt] Romney victory would dramatically empower Republican governors,' Kousser says.",
            "The law requires the Maryland Public Secondary Schools Athletic Association, governing bodies of public institutions of higher education, county education boards and community college trustee boards to allow student athletes to modify athletic, or team uniforms, to conform to their religious or cultural requirements, or preferences for modesty."
        ],
        "topic": [
            {
            "logic":[["Voters","requires"],[]],
            "displayName":"tên topic 1"
            },
            {
                "logic":[["A","B","C"],["D"]],
                "displayName":"tên topic 2"
            }
        ],
        "id_mapAlgTypeAI" :[1],
        "percent_output": 0.3,
        "cluster": False
    }
    # init.Initialize()
    print(summary(dataInput))
    