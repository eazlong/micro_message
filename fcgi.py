#!/usr/bin/python
# encoding : utf-8
# from flup.server.fcgi import WSGIServer  
import web
import os
import time
import ms_interface
from xml.etree import ElementTree as ET
from token_manager import *
from db import *

urls = ('/micro_message.*', 'micro_message',
        '/request.*', 'request',
        '/show.*', 'show_info' )

app = web.application(urls, globals())  
token_mngr = token_manager()
mysql = db()
host = 'http://120.24.44.224'
source_dir=host+'/static'
show_dir=host+'/show?id='
invalid_request="Invalid Request"

class show_info:
    def __init__(self):
        self.render = web.template.render()

    def GET( self ):
        params = web.input()
        if not params.has_key( 'id' ):
            return invalid_request
        sid = int(params['id'])
        name, url, des = mysql.get_friends_info( sid )
        return self.render.show_friend_info( name, source_dir+url, des )


class request:
    def __init__(self):
        #templates_root = os.path.join(self.app_root, 'templates')
        self.render = web.template.render()

    def GET( self ):
        sid = 0
        dbparams = ()
        table = ""
        type = 0
        params = web.input()
        if params.has_key( 'type' ):
            if params['type'] == 'spread': #spread type
                if not params.has_key( 'name' ):
                    return "Invalid Request"
                sid = mysql.find_in_spread( params['name'] )
                if sid != 0:
                    ticket = mysql.get_ticket( sid );
                    print ticket
                    return self.render.gen_2dcode( "https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket="+ticket )
                sid = mysql.get_max_id_from( '2dcode' )+1
                dbparams = (sid, params['name'], 0)
                table = 'spread'
                type = 0
            elif params['type'] == 'friends':
                if params.has_key( 'id' ):
                    sid = str( params['id'] )
                    ticket = mysql.get_ticket( sid );
                    if  ticket != '':
                        return self.render.gen_2dcode( "https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket="+ticket )
                    else:
                        return invalid_request;
                sid = mysql.get_max_id_from( '2dcode' )+1
                dbparams = (sid, 'susan', '/friends/eg_tulip.jpg', 'this is a test picture', 0)
                table = 'friends'
                type = 1
            else:
                return "Invalid Request"
            print token_mngr
            r, code_info = ms_interface.gen_2d_code( token_mngr.get_token(), sid )
            if not r :
                return "Invalid Request"
            mysql.write_to( '2dcode', (sid, code_info['ticket'], code_info['url'], type ) )
            mysql.write_to( table, dbparams )
            return self.render.gen_2dcode( "https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket="+code_info['ticket'] );
        else:
            return "Invalid Request"


class micro_message: 
    def __init__(self):
        #templates_root = os.path.join(self.app_root, 'templates')
        self.render = web.template.render()
 
    def GET(self): 
        in_data = web.input()
        if in_data.has_key('signature'):
            if not ms_interface.check_signature( in_data ):
                return "Invalid Request"
            if ( in_data.has_key( 'echostr' ) ):
                return in_data.echostr
            # else:
            #     reply = """<xml>
            #         <ToUserName><![CDATA[%s]]></ToUserName>
            #         <FromUserName><![CDATA[%s]]></FromUserName>
            #                     <CreateTime>%s</CreateTime>
            #                     <MsgType><![CDATA[text]]></MsgType>
            #                     <Content><![CDATA[%s]]></Content>
            #                     <FuncFlag>0</FuncFlag>
            #             </xml>"""
            #        if request.raw_post_data:
            #            xml = ET.fromstring(request.raw_post_data)
            #            content = xml.find("Content").text
            #            fromUserName = xml.find("ToUserName").text
            #            toUserName = xml.find("FromUserName").text
            #            postTime = str(int(time.time()))
            #            if not content:
            #                return HttpResponse(reply % (toUserName, fromUserName, postTime, ""))
            #            if content == "Hello2BizUser":
            #                return HttpResponse(reply % (toUserName, fromUserName, postTime, ""))
            #            else:
            #                return HttpResponse(reply % (toUserName, fromUserName, postTime, ""))
            #        else:
            #            return HttpResponse("Invalid Request")
        else:
            return "Invalid Request"
            
    def POST( self ):
        in_data = web.input()
        print in_data
        if in_data.has_key('signature'):
            if not ms_interface.check_signature( in_data ):
                return "Invalid Request"
            data = web.data()
            print data
            try: 
                str_xml = web.data()
                xml = ET.fromstring(str_xml)
                content=xml.find("Ticket").text
                msgType=xml.find("MsgType").text
                fromUser=xml.find("FromUserName").text
                toUser=xml.find("ToUserName").text
                if msgType!='event':
                    return 'Invalid Request'
                event = xml.find("Event").text
                event_key = xml.find( "EventKey" ).text
                sid = 0
                if event=="subscribe":
                    sid = int( event_key[len('qrscene_'):])
                elif event=="SCAN":
                    sid = int( event_key )
                print sid
                type = mysql.get_type( sid )
                print type
                if type == 0 and event=="subscribe":
                    mysql.add_spread_count( sid );
                else:
                    name, url, des = mysql.get_friends_info( sid )
                    return self.render.reply_text_pic(fromUser,toUser,int(time.time()), name, des, source_dir+url, show_dir+str(sid) )
                return self.render.reply_text(fromUser,toUser,int(time.time()),"welcome")
            except Exception, e: 
                print e
        return 'Invalid Request'

# def myapp( environ, start_response ):
#     start_response( "200 ok", [('Content-Type', 'text/plain')] )
#     return ['hello']    

web.webapi.internalerror = web.debugerror
if __name__  == '__main__':
    token_mngr.start()
    web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi( func, addr )
    app.run()
    token_mngr.stop()
#flups.WSGIServer(myapp).run()   
#WSGIServer(myapp,bindAddress=('0.0.0.0',8008)).run()
