import requests

API_URL = "https://pwpcourse.eu.pythonanywhere.com"


def room_info(body, south, north):
    #print(f"BODY:{body}")
    if body["content"] == None:
        if south == 0:
            try:
                #print(f"SOUTH: {body['@controls']['maze:south']["href"]}")
                return body['@controls']['maze:south']["href"], 0,0,0
            #elif body["@controls"]["maze:east"]:
            #    #print(f"SOUTH: {body['@controls']['maze:east']["href"]}")
            #    return body['@controls']['maze:east']
            #elif body["@controls"]["maze:north"]:
            #    #print(f"SOUTH: {body['@controls']['maze:north']["href"]}")
            #return body['@controls']['maze:north']
            except:
                print(f"FOUND {body['content']} FROM: {body['handle']} CTRLs:{body['@controls']}")
                return body['@controls']['maze:east']["href"], 1,0,0
        if north == 0:
            try:
                #print(f"SOUTH: {body['@controls']['maze:south']["href"]}")
                return body['@controls']['maze:north']["href"], 1,0,0
            except:
                print(f"FOUND {body['content']} FROM: {body['handle']} CTRLs:{body['@controls']}")
                return body['@controls']['maze:east']["href"], 0,0,0
    else:
        print(f"FOUND {body['content']} FROM: {body['handle']}")
        print(body)
        return None,1,1,1

def main():
    row_done_flag = 0
    with requests.Session() as s:
        s.headers.update({"Accept": "application/vnd.mason+json"})
        resp = s.get(API_URL + "/api/")
        if resp.status_code != 200:
            print("Unable to access API.")
        else:
            body = resp.json()
            room_href = body["@controls"]["maze:entrance"]["href"]
            resp = s.get(API_URL + room_href)
            body = resp.json()
            south = 0
            north = 0
            exit = 0
            while exit == 0:
                #while (south == 0) and (exit == 0):
                next_room_href,south, north, exit = room_info(body, south, north)
                resp = s.get(API_URL + next_room_href)
                body = resp.json()

main()