#!/usr/bin/python
# encoding=utf-8
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
        type = mysql.get_type( sid )
        if type == 1:
            name, url, des = mysql.get_friends_info( sid )
            return self.render.show_friend_info( name, source_dir+url, des )
        elif type == 2:
            question, answer1, answer2, answer3, answer4, right_anser = mysql.get_answer_info( sid )
            return self.render.show_answer_info( question, answer1, answer2, answer3, answer4, right_anser )


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
            elif params['type'] == 'questions':
                sid = mysql.get_max_id_from( '2dcode' )+1
                dbparams = (sid, '你多大了', '1岁', '猴子那么大', '不大', '奔三了', 1, 1, 'recognize' )
                table = 'questions'
                type = 2
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
                fromUser=xml.find("FromUserName").text
                toUser=xml.find("ToUserName").text
                msgType=xml.find("MsgType").text
                if msgType == 'text':
                    msg = xml.find( "Content" ).text
                    if msg not in ( "1", "2" ):
                        ret_msg = '''您好，您输入的指令不支持，请输入如下指令:\n\t1.获取王婆邮箱\n\t2.获取投稿邮箱'''
                    if msg == '1':
                        ret_msg = "您好，您可以将邮件发送至1395017772@qq.com,我们会将通过筛选的邮件转发给对方"
                    elif msg == '2':
                        ret_msg = "您好，谢谢您的支持，您可以将稿件发送至1124465762@qq.com"
                    return self.render.reply_text(fromUser,toUser,int(time.time()), ret_msg.encode('utf-8') )
                elif msgType!='event':
                    return 'Invalid Request'
                event = xml.find("Event").text
                event_key = xml.find( "EventKey" ).text
                sid = 0
                if event=="subscribe":
                    if not event_key:
                        msg = '''欢迎你，这里是微信公众号『禹钧学苑 』。\n虽然来得晚了点，但是也不会错过太多风景，\n点击下面【往期回顾】可以查看所有文章。'''
                        return self.render.reply_text(fromUser,toUser,int(time.time()),msg.encode( 'utf-8' ) )
                    sid = int( event_key[len('qrscene_'):])
                elif event=="SCAN":
                    sid = int( event_key )
                elif event=="CLICK":
                    ms_interface.send_message( token_mngr.get_token(), event_key, fromUser, mysql )
                    return 'success'
                print sid
                type = mysql.get_type( sid )
                print type
                if type == 0 and event=="subscribe":
                    mysql.add_spread_count( sid );
                    msg = '''欢迎你，这里是微信公众号『禹钧学苑 』。\n虽然来得晚了点，但是也不会错过太多风景，\n点击下面【往期回顾】可以查看所有文章。'''
                    return self.render.reply_text(fromUser,toUser,int(time.time()),msg.encode( 'utf-8' ) )
                elif type == 1:
                    name, url, des = mysql.get_friends_info( sid )
                    return self.render.reply_text_pic(fromUser,toUser,int(time.time()), name, des, source_dir+url, show_dir+str(sid) )
                elif type == 2:
                    return self.render.reply_text_pic(fromUser,toUser,int(time.time()), "点击图片查看题目选项及答案".encode('utf-8'), "", source_dir+"/friends/eg_tulip.jpg", show_dir+str(sid) )                    
                else:
                    return 'Invalid Request'
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
    time.sleep(3)

    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')
    menu = {
        "button":[
        {
            "name":"最新文章".encode('utf-8'),
            "sub_button":[
            {    
               "type":"view",
               "name":"童声童趣".encode('utf-8'),
               "url":"http://mp.weixin.qq.com/s?__biz=MzIxNDM3MzEyMQ==&mid=100000048&idx=1&sn=7f051003ebc8720bcf5fd5c498d838a7&scene=18#wechat_redirect"
            },
            {
               "type":"view",
               "name":"原创作品".encode('utf-8'),
               "url":"http://mp.weixin.qq.com/s?__biz=MzIxNDM3MzEyMQ==&mid=100000068&idx=1&sn=d21452795371b2b1f2f34b7db7a7b342&scene=18#wechat_redirect"
            },
            {
               "type":"view",
               "name":"每日一更".encode('utf-8'),
               "url":"http://mp.weixin.qq.com/s?__biz=MzIxNDM3MzEyMQ==&mid=100000096&idx=1&sn=e48b64d0945d6f5f8354940d6c8e2d10&scene=18#wechat_redirect"
            }]
        },
        {
            "type":"view",
            "name":"往期回顾".encode('utf-8'),
            "url":"http://mp.weixin.qq.com/mp/getmasssendmsg?__biz=MzIxNDM3MzEyMQ==#wechat_webview_type=1&wechat_redirect"
        },
        {
            "name":"特别推荐".encode('utf-8'),
            "sub_button":[
            {    
               "type":"click",
               "name":"投稿专区".encode('utf-8'),
               "key":"tuijian_tougao"
            },
            {
               "type":"click",
               "name":"王婆专区".encode('utf-8'),
               "key":"tuijian_wangpo"
            },
            {
               "type":"click",
               "name":"扫码答题".encode('utf-8'),
               "key":"tuijian_dati"
            }]
        }]
    }
    if not ms_interface.create_menu( token_mngr.get_token(), menu ):
        print 'create menu error!'

    ms_interface.get_material( token_mngr.get_token(), 'news' )

    web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi( func, addr )
    app.run()
    token_mngr.stop()
#flups.WSGIServer(myapp).run()   
#WSGIServer(myapp,bindAddress=('0.0.0.0',8008)).run()
