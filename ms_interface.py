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

def send_message( t, event_id, to_user, mysql ):
    params = None
    if event_id == "tuijian_tougao":
        params = {
	        "touser":to_user,
	        "msgtype":"mpnews",
	        "mpnews":
	        {
	             "media_id":'VOt33rJ0l05Euvzyj47IaECTUUZbcFYCfIETahIyk70'
	        }
	    }
    elif event_id== "tuijian_wangpo":
    	params = {
	        "touser":to_user,
	        "msgtype":"mpnews",
	        "mpnews":
	        {
	             "media_id":'VOt33rJ0l05Euvzyj47IaPzVzz_YyUcmwN270OQ5FC0'
	        }
	    }
    elif event_id == "tuijian_dati":
    	data = mysql.get_questions( "recognize", 1, 5 )
    	print data
    	params = {
		    "touser":to_user,
		    "msgtype":"news",
		    "news":{
		        "articles": [
		         {
		             "title":'扫码答题'.encode( 'utf-8' ),
		             "description":"打印下面的二维码，扫描后可以获得选项".encode( 'utf-8' ),
		         },
		         {
		             "title":data[0][0].encode( 'utf-8' ),
		             "description":data[0][0].encode( 'utf-8' ),
		             "url":"http://120.24.44.224/show?id="+str(data[0][1]),
		             "picurl":"https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket="+str(mysql.get_ticket(data[0][1]))
		         },
		         {
		             "title":data[1][0].encode( 'utf-8' ),
		             "description":data[1][0].encode( 'utf-8' ),
		             "url":"http://120.24.44.224/show?id="+str(data[1][1]),
		             "picurl":"https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket="+str(mysql.get_ticket(data[1][1]))
		         },
		         {
		             "title":data[2][0].encode( 'utf-8' ),
		             "description":data[2][0].encode( 'utf-8' ),
		             "url":"http://120.24.44.224/show?id="+str(data[2][1]),
		             "picurl":"https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket="+str(mysql.get_ticket(data[2][1]))
		         },
		         {
		             "title":data[3][0].encode( 'utf-8' ),
		             "description":data[3][0].encode( 'utf-8' ),
		             "url":"http://120.24.44.224/show?id="+str(data[3][1]),
		             "picurl":"https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket="+str(mysql.get_ticket(data[3][1]))
		         },
		         {
		             "title":data[4][0].encode( 'utf-8' ),
		             "description":data[4][0].encode( 'utf-8' ),
		             "url":"http://120.24.44.224/show?id="+str(data[4][1]),
		             "picurl":"https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket="+str(mysql.get_ticket(data[4][1]))
		         }
		         ]
		    }
		}
    else:
        return False
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
