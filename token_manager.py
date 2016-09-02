#!/usr/bin/python
# encoding : utf-8

import threading
import time
import httplib
import json
#import commands

def singleton(cls, *args, **kw):  
    instances = {}  
    def _singleton():  
        if cls not in instances:  
            instances[cls] = cls(*args, **kw)  
        return instances[cls]  
    return _singleton  

# APPID="wx8d318dd436013ad3"
# APPSecret="ef662f9aa7c6d8f0c6691cbce646763d"
APPID="wxca5bf8e49f97500c"
APPSecret="b670b01eea29272625c62e81ad9d98fe"
@singleton
class token_manager( threading.Thread ):
    def __init__( self ):
        threading.Thread.__init__( self )
        self.to_stop = False
        self.access_token=""
        self.expires_time = 0

    def run( self ):
        while not self.to_stop:
            # (status, output) = commands.getstatusoutput('curl -s "https://api.weixin.qq.com/cgi-bin/token?secret='+APPSecret+'&grant_type=client_credential&appid='+APPID+'"')
            # if status != 0:
            #     print 'get token error %d' %status
            #     continue
            # json_data = json.loads( output )
            # if json_data.has_key( "errcode" ):
            #     print json_data['errmsg']
            # else:
            #     self.access_token = json_data['access_token']
            #     print self.access_token
            #     time.sleep( int(json_data['expires_in']-10) )
            if self.expires_time < 20:
                conn = httplib.HTTPSConnection( 'api.weixin.qq.com' )
                #data = urllib.urlencode( { 'secret':APPSecret, 'grant_type':'client_credential', 'appid':APPID } )
                conn.request( 'GET', '/cgi-bin/token?grant_type=client_credential&appid='+APPID+'&secret='+APPSecret )
                res = conn.getresponse()
                if res.status != 200:
                    print "get response error"
                    conn.close()
                    continue
                body = res.read()
                conn.close()
                json_data = json.loads( body )
                print json_data['access_token']
                if json_data.has_key( "errcode" ):
                    print json_data['errmsg']
                else:
                    self.access_token = json_data['access_token']
                    self.expires_time = int(json_data['expires_in'])
            time.sleep( 10 )
            self.expires_time -= 10

    def stop( self ):
        self.to_stop = True

    def get_token( self ):
        return self.access_token
