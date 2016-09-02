#!/usr/bin/python
# encoding : utf-8

import hashlib
import httplib
import ssl
import socket
import urllib
import json

token = "yujunxueyuan2016"
#token="VEPtMm7YGy7VAqLR4SI0pMpiqkKSDJ356LHPJFfUhOc"
def check_signature( param ):
    signature = param.signature
    timestamp = param.timestamp
    nonce = param.nonce
    temp_arr = [token, timestamp, nonce]
    temp_arr.sort()
    temp_str = "".join(temp_arr)
    temp_str = hashlib.sha1(temp_str).hexdigest()
    if temp_str == signature:
        return True;
    else:
        return False;

def gen_2d_code( t, id ):
    data = ""
    ret = False
    try:
        conn = httplib.HTTPSConnection("api.weixin.qq.com")
        headers = {"Content-type":"application/json"} 
        params = ({"action_name": "QR_LIMIT_SCENE",
            "action_info":
                 {
                    "scene": {"scene_id": id }
                 }
            })
        conn.request("POST", "/cgi-bin/qrcode/create?access_token="+t, json.JSONEncoder().encode(params), headers)
        response = conn.getresponse()
        data = response.read()
        print data
        if response.status == 200:
            ret = True
    except Exception, e:
        print e
    finally:
        conn.close()
    return ret, eval(data)
