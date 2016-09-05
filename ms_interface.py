#!/usr/bin/python
# encoding=utf-8

import hashlib
import httplib
import ssl
import socket
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

def create_menu( t, params ):
    data = ""
    ret = False
    try:
        conn = httplib.HTTPSConnection("api.weixin.qq.com")
        headers = {"Content-type":"application/json","encoding":"utf-8" }
        conn.request("POST", "/cgi-bin/menu/create?access_token="+t, json.JSONEncoder(ensure_ascii=False).encode(params), headers)
        response = conn.getresponse()
        data = response.read()
        print data
        if response.status == 200:
            ret = True
    except Exception, e:
        print e
    finally:
        conn.close()
    if ret:
        ret_json = eval(data)
        if ret_json['errcode'] == 0:
            return True
    return False

def get_material( t, type ):
    data = ""
    ret = False
    try:
        conn = httplib.HTTPSConnection("api.weixin.qq.com")
        headers = {"Content-type":"application/json","encoding":"utf-8" }
        params = {
            "type":type,
            "offset":0,
            "count":20
        }
        conn.request("POST", "/cgi-bin/material/batchget_material?access_token="+t, json.JSONEncoder(ensure_ascii=False).encode(params), headers)
        response = conn.getresponse()
        data = response.read()
        if response.status == 200:
            ret = True
        ret_json = eval(data)
        for s in ret_json['item']:
            print s['media_id'], s['update_time'], s['content']['news_item'][0]['title']
    except Exception, e:
        print e
    finally:
        conn.close()

def send_message( t, event_id, to_user ):
    print '怎么没反应啊'
    media_id = ""
    if event_id == "tuijian_tougao":
        media_id = 'VOt33rJ0l05Euvzyj47IaECTUUZbcFYCfIETahIyk70'
    elif event_id== "tuijian_wangpo":
        media_id = 'VOt33rJ0l05Euvzyj47IaPzVzz_YyUcmwN270OQ5FC0'
    else:
        return False
    params = {
        "touser":to_user,
        "msgtype":"mpnews",
        "mpnews":
        {
             "media_id":media_id
        }
    }
    data = ""
    ret = False
    try:
        conn = httplib.HTTPSConnection("api.weixin.qq.com")
        headers = {"Content-type":"application/json","encoding":"utf-8" }
        conn.request("POST", "/cgi-bin/message/custom/send?access_token="+t, json.JSONEncoder(ensure_ascii=False).encode(params), headers)
        response = conn.getresponse()
        data = response.read()
        print data
        if response.status == 200:
            ret = True
    except Exception, e:
        print e
    finally:
        conn.close()
    if ret:
        ret_json = eval(data)
        if ret_json['errcode'] == 0:
            return True
    return False

