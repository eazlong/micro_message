#!/usr/bin/python
# encoding=utf-8

import os
import hashlib
import httplib
import ssl
import socket
import json
import uuid
import requests 
from PIL import ImageFile
from image_processor import *

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
        di = image_processor()
        pics = []
        sizes = []
        x = 1
        y = 1
        i = 0;
        for d in data:
            size = di.str_to_image( d[0].encode('utf-8'), 300, '1.jpg')
            download_image( str(mysql.get_ticket(d[1])), '/root/code/2.jpg' )
            paths = ( '1.jpg', '2.jpg' )
            name_s = str( uuid.uuid1() )+'.jpg'
            size = di.image_stitching( paths, ( (1, 1, size[0], size[1]), (1, size[1]+2, size[0], 300)) , name_s, 1 )
            pics.append( name_s );
            if i%2==0:
                x = 1
            sizes.append( (x, y, size[0], size[1]) )
            x += size[0]+1;
            if i%2==1:
                y += size[1]+1
            i+=1
        name = str(uuid.uuid1())+'.jpg'
        di.image_stitching( pics, sizes, name, 1 )
        media_id = upload_image( t, name )
        for pic in pics:
        	os.remove( pic )
        os.remove( name )
        url = "http://www.joy8888.com/show?id="
        params = {
            "touser":to_user,
            "msgtype":"image",
            "image":{
                "media_id":media_id
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

def upload_image( t, image ):
    files = {"image": open(image, "rb")}
    response = requests.post("https://api.weixin.qq.com/cgi-bin/media/upload?access_token=" + t + "&type=image", files=files)
    print response.content
    data = eval(response.content)
    return data['media_id']

def download_image( ticket, file_name ):
    try:
        conn = httplib.HTTPSConnection("mp.weixin.qq.com")
        conn.request("GET", "/cgi-bin/showqrcode?ticket="+ticket )
        response = conn.getresponse()
        if response.status != 200:
            return False, ''
        data = response.read()
        p = ImageFile.Parser()
        p.feed( data )
        im = p.close();
        im.save( file_name )
    except Exception, e:
        print e
    finally:
        conn.close()


