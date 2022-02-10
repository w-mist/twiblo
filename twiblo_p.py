import base64
import datetime
import sys
import time
import datetime
import requests
import tweepy
import random

DEBUG=0
#DEBUG=1

API_KEY=""
API_SECRET=""
ACC_TOKEN=""
ACC_TOKEN_SECRET=""
BLOCK_FILEPATH=""
PASS_FILEPATH=""
CYCLE_NUM=175
SLEEP_TIME=600
API_OAUTH_URL="https://api.twitter.com/oauth2/token"
API_BASE_URL="https://api.twitter.com/2"
API_LIMIT_URL="https://api.twitter.com/1.1/application/rate_limit_status.json"
LIST_FOLLOWER=[]
LIST_FOLLOWEE=[]

def MakeAuthRequest():
    # encode by base64
    s = API_KEY + ":" + API_SECRET
    b = base64.b64encode(s.encode())
    a = b.decode()
    if DEBUG:
        print(a)
    # make header & body
    global header
    header = { \
        "Authorization" : "Basic" + " " + a, \
        "Content-Type" : "application/x-www-form-urlencoded;charset=UTF-8"
    }
    global body
    body = "grant_type=client_credentials"

def GetBearerToken():
    global body
    global header
    resp = requests.post(API_OAUTH_URL, data=body, headers=header)
    c = resp.status_code
    if c != 200:
        n = sys._getframe().f_code.co_name
        print("![ERR] HTTP {} at {}".format(str(c), str(n)))
        print(resp.text)
        sys.exit
    print("HTTP " + str(c))
    jd = resp.json()
    if DEBUG:
        print(jd)
    bt = jd["access_token"]
    print("AUTH success")
    return bt

# return list
def GetTargetList():
    lis = []
    # read from file
    for i in open(BLOCK_FILEPATH, 'r'):
        li = i[:-1].split(',')
        lis = [str(uid) for uid in li]
    print("target ids=" + str(len(lis)) + " accounts")
    return lis

# return dict
def GetUsersInfo(token, id, i):
    header = { \
        "Authorization" : "Bearer" + " " + token
    }
    url = API_BASE_URL + "/users/" + str(id) + "?user.fields=verified"
    resp = requests.get(url, headers=header)
    c = resp.status_code
    if c != 200:
        n = sys._getframe().f_code.co_name
        print("![ERR] HTTP {} at {}".format(str(c), str(n)))
        print(resp.text)
        sys.exit
    lim = resp.headers["x-rate-limit-limit"]
    rem = resp.headers["x-rate-limit-remaining"]
    res = int(resp.headers["x-rate-limit-reset"]) - time.mktime(datetime.datetime.now().timetuple())
    jd = resp.json()
    if DEBUG:
        print("rate-limit at {}:{}/{}({}sec)".format(sys._getframe().f_code.co_name, rem, lim, res))
    return jd

# return: boolean
# - true: account is in my follower
def IsMyFollower(id):
    bl = id in LIST_FOLLOWER
    if DEBUG:
        print("id:" + str(id) + " is not FolloweR")
    return bl

# return: boolean
# - true: account is in my folowee
def IsMyFollowee(id):
    bl = id in LIST_FOLLOWEE
    if DEBUG:
        print("id:" + str(id) + " is not FoloweE")
    return bl

# return tweepy api
def DoOAuthV1():
    auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACC_TOKEN, ACC_TOKEN_SECRET)
    api = tweepy.API(auth)
    return api

def DoBlock(api, dict):
    if len(dict) == 0:
        print("![ERR] dict is empty")
        sys.exit
    id = dict.get("data").get("id") #str
    name = dict.get("data").get("name") #str
    username = dict.get("data").get("username") #str
    verified = dict.get("data").get("verified") #boolean
    wr = False
    if not IsMyFollower(id):
        if not IsMyFollowee(id):
            if not verified:
                if DEBUG:
                    print("id:" + str(id) + " is not verified user")
                api.create_block(user_id=id, include_entities=False, skip_status=True)
                print("id:" + str(id) + " is blocked")
                wr = False
            else:
                print("**id:" + str(id) + " is verified user. pass")
                wr = True
        else:
            print("**id:" + str(id) + " is my foloweE. pass")
            wr = True
    else:
        print("**id:" + str(id) + " is my FolloweR. pass")
        wr = True
    if wr:
        f = open(PASS_FILEPATH, 'a')
        f.write(str(id) + ",")
        f.close()

def main():
    if DEBUG:
        print("#----- DEBUG print enable -----#")
    MakeAuthRequest()
    token = GetBearerToken()
    target_uid_list = GetTargetList()
    i = 0
    api = DoOAuthV1()
    l = list(target_uid_list)
    for id in target_uid_list:
        r_l = len(target_uid_list)
        i += 1
        print("#" + str(i) + "--------")
        uid = id
        dict = GetUsersInfo(token, id, i)
        if not "errors" in dict:
            DoBlock(api, dict)
        else:
            print("![ERR] id:" + str(id) + " reason:" + dict.get("errors")[0].get("title"))

        # output to file
        l.remove(id)
        f = open(BLOCK_FILEPATH, 'w')
        t = ",".join(l)
        f.write(t)
        f.close()

        # check rate_limit
        d = api.rate_limit_status(resources='blocks')   # dict
        rem = d.get('resources').get('blocks').get('/blocks/ids').get('remaining')
        if DEBUG:
            print("rate-limit remaining:" + str(rem))
        if rem % CYCLE_NUM == 0:
            print("@reached the rate-limit. need " + \
                datetime.datetime.fromtimestamp(rem).isoformat(' ', 'seconds') + "seconds to reset")
            print("@wait for " + str(SLEEP_TIME) + "seconds")
            time.sleep(SLEEP_TIME)
            # OAuth again
            api = DoOAuthV1()
        time.sleep(2+random.random())

if __name__ == '__main__':
    main()
