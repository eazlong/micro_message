import MySQLdb as mysqldb

class db:
    def __init__( self ):
        self.conn=mysqldb.connect(host="localhost",user="root",passwd="1234",db="test",charset="utf8")    
        self.cursor = self.conn.cursor()   

    def write_to( self, table, params ):
        l = len( params )
        sql = "insert into " + table + " values("
        for i in range(l-1):
            sql += " %s,"
        sql += " %s );"
        print sql, params
        ret = self.cursor.execute(sql, params )
        self.conn.commit()
        return ret

    def get_max_id_from( self, table ):
        sql = "select max(id) from " + table + ";"
        self.cursor.execute( sql );
        ret = self.cursor.fetchall();
        print ret
        if ret[0][0]==None:
            return 0
        return int( ret[0][0] )

    def find_in_spread( self, name ):
        sql = "select id from spread where name='"+name + "'";
        self.cursor.execute( sql )
        ret = self.cursor.fetchall();
        print ret
        if not ret:
            return 0
        return int( ret[0][0] )

    def get_ticket( self, sid ):
        sql = "select 2did from 2dcode where id="+str(sid)
        self.cursor.execute( sql )
        ret = self.cursor.fetchall();
        if not ret:
            return ''
        return ret[0][0]

    def get_type( self, sid ):
        sql = "select type from 2dcode where id="+str(sid)
        self.cursor.execute( sql )
        ret = self.cursor.fetchall();
        if not ret:
            return -1
        return ret[0][0]

    def add_spread_count( self, sid ):
        sql = "update spread set count=count+1 where id="+str(sid)
        self.cursor.execute( sql )
        self.conn.commit();

    def get_friends_info( self, sid ):
        sql = "select name, picurl, description from friends where id="+str(sid)
        self.cursor.execute( sql )
        ret = self.cursor.fetchall();
        if not ret:
            return '', '', ''
        return ret[0][0], ret[0][1], ret[0][2]

    def get_questions( self, title, age, count ):
        sql = 'select question, id from questions where title=\''+title+'\' and age='+str(age)+' order by rand() limit '+ str(count)
        self.cursor.execute( sql )
        return self.cursor.fetchall();

    def get_answer_info( self, sid ):
        sql = "select question, answer1, answer2, answer3, answer4, right_anser from questions where id="+str(sid)
        self.cursor.execute( sql )
        ret = self.cursor.fetchall();
        if not ret:
            return '', '', ''
        return ret[0][0], ret[0][1], ret[0][2], ret[0][3], ret[0][4], ret[0][5]