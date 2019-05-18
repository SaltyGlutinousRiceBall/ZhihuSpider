import pymysql


maintable = """CREATE TABLE IF NOT EXISTS zhihu(
               user1_id CHAR(33),
               user2_id CHAR(33),
               ACT_TYPE TINYINT,
               content_id CHAR(20),
               TIME DATETIME)"""

question_table = """CREATE TABLE IF NOT EXISTS questiontable(
                    question_id CHAR(20),
                    topic VARCHAR(20),
                    ans_num MEDIUMINT)"""

user_table = """CREATE TABLE IF NOT EXISTS usertable(
               user_id CHAR(33),
               name TINYTEXT)"""

answer_table = """CREATE TABLE IF NOT EXISTS anstable(
                 answer_id CHAR(20),
                 question_id CHAR(20),
                 comment_num MEDIUMINT,
                 vote_num MEDIUMINT,
                 content MEDIUMTEXT)"""

comment_table = """CREATE TABLE IF NOT EXISTS commenttable(
                  comment_id CHAR(20),
                  answer_id CHAR(20),
                  featured CHAR(5),
                  vote_num MEDIUMINT,
                  reply_num MEDIUMINT,
                  content MEDIUMTEXT)
                  """
reply_table = """CREATE TABLE IF NOT EXISTS replytable(
                reply_id CHAR(20),
                comment_id CHAR(20),
                vote_num MEDIUMINT,
                content MEDIUMTEXT)"""



def connect():
    host = 'localhost'  # 目标数据库的ip地址，如果是本机地址，可以写localhost
    port = 3306  # 数据库的端口，我这里使用的是3306
    user = 'root'  # 数据库的用户名
    passwd = '123456'  # 数据库密码
    db = 'zhihu'  # 连接的数据库的名字
    database = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db)
    return database


