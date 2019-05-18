#-*-coding:utf-8-*-
import requests
import json
from lxml import html
import SpiderConfig
import datetime
import pymysql
import ZhihuSQL

def hastopic(search):

    param = {'type': 'content',
             'q': search}
    response = requests.get(SpiderConfig.url + r'/search', params=param, headers=SpiderConfig.headers)
    tree = html.fromstring(response.text)
    intro = tree.xpath(r'//*[@id="SearchMain"]/div/div/div/div/div/div/div/div[1]/a/@href')
    intro_2 = tree.xpath(r'//*[@id="SearchMain"]/div/div/div/div/div/div/div/div/div[2]/h2/div/a/@href')
    topic_name_2 = tree.xpath(r'//*[@id="Popover10-toggle"]/span/em/text()')
    topic_name = tree.xpath(r'//*[@id="SearchMain"]/div/div/div/div/div/div/div/div[1]/div/div[1]/h2/a/text()')
    if intro:
        flag = True
        return flag, intro[0], topic_name
    else:
        if intro_2:
            flag = True
            return flag, intro_2[0][15:], topic_name_2

        flag = False
        topic_name = '无'
        return flag, intro, topic_name


def childComentSpider(comment_id):
    url = SpiderConfig.url + SpiderConfig.url_api + r'/comments/' + str(comment_id) + r'/child_comments'
    response = requests.get(url, params=SpiderConfig.ChildCommentSpiderParam, headers=SpiderConfig.headers)
    ans_json = json.loads(response.text)
    db = ZhihuSQL.connect()
    cursor = db.cursor()
    while True:
        for data in ans_json['data']:
            author_id = data['author']['member']['id']  # 撰写回复的用户的id
            author_name = data['author']['member']['name']  # 撰写回复的用户的名称
            content = data['content']  # 回复的内容
            created_time = data['created_time']  # 回复时间
            created_time_array = datetime.datetime.utcfromtimestamp(created_time)  # 将时间戳转化为数组
            created_time_real = created_time_array.strftime("%Y-%m-%d %H:%M:%S")  # 将时间数组转化为字符串的形式
            childcomment_id = data['id']  # 该条回复的id
            vote_count = data['vote_count']  # 点赞数量
            reply_to_author_id = data['reply_to_author']['member']['id']  # 回复目标的id
            reply_to_author_name = data['reply_to_author']['member']['name']  # 回复目标的名字
            author_name = pymysql.escape_string(author_name)
            content = pymysql.escape_string(content)
            author_id = pymysql.escape_string(author_id)

            sql_main = """INSERT INTO zhihu(user1_id, user2_id, ACT_TYPE, content_id, TIME)
                                      values('%s','%s',5, '%s', str_to_date(\'%s\','%%Y-%%m-%%d %%H:%%i:%%s'))"""\
                       % (author_id, reply_to_author_id, 'reply'+str(comment_id), created_time_real)
            sql_user = """INSERT INTO usertable(user_id,name) select '%s','%s' from dual where not
                                                          exists(select 1 from usertable where user_id ='%s')""" \
                       % (author_id, author_name, author_id)
            sql_reply = """INSERT INTO replytable(reply_id,comment_id,vote_num,content)
                           values('%s','%s',%d,'%s')""" % ('reply'+str(childcomment_id), 'comment'+str(comment_id),
                                                           vote_count, content)
            cursor.execute(sql_main)
            cursor.execute(sql_user)
            cursor.execute(sql_reply)
            db.commit()

        if ans_json['paging']['is_end']:
            break
        next_url = ans_json['paging']['next']
        url = SpiderConfig.url + SpiderConfig.url_api + next_url[21:]  # 这里next给出的url没有带api/v4，需要添加上，不然无法请求成功
        response = requests.get(url, headers=SpiderConfig.headers)
        ans_json = json.loads(response.text)
    db.close()


def commentSpider(ans_id, ansor_id):
    url = SpiderConfig.url + SpiderConfig.url_api + r'/answers/' + str(ans_id) + r'/root_comments'
    response = requests.get(url, params=SpiderConfig.CommentSpiderParam, headers=SpiderConfig.headers)
    ans_json = json.loads(response.text)
    db = ZhihuSQL.connect()
    cursor = db.cursor()
    while True:
        for data in ans_json['data']:
            comment_id = data['id']  # 评论的id
            content = data['content']  # 评论的内容
            vote_count = data['vote_count']  # 点赞数量
            created_time = data['created_time']  # 创建时间
            featured = data['featured']  # 是否是热评
            author_id = data['author']['member']['id']  # 撰写评论的用户的id
            author_name = data['author']['member']['name']  # 撰写评论的用户的名称
            child_comment_count = data['child_comment_count']  # 子评论的数量
            created_time_array = datetime.datetime.utcfromtimestamp(created_time)  # 将时间戳转化为数组
            created_time_real = created_time_array.strftime("%Y-%m-%d %H:%M:%S")  # 将时间数组转化为字符串的形式
            author_name = pymysql.escape_string(author_name)
            author_id = pymysql.escape_string(author_id)
            ansor_id = pymysql.escape_string(ansor_id)
            content = pymysql.escape_string(content)

            sql_main = """INSERT INTO zhihu(user1_id, user2_id, ACT_TYPE, content_id, TIME)
                          values('%s','%s',4,'%s',str_to_date(\'%s\','%%Y-%%m-%%d %%H:%%i:%%s'))"""\
                       % (author_id, ansor_id, 'answer'+str(ans_id), created_time_real)

            sql_user = """INSERT INTO usertable(user_id,name) select '%s','%s' from dual where not
                                              exists(select 1 from usertable where user_id ='%s')""" \
                       % (author_id, author_name, author_id)

            sql_comment = """INSERT INTO commenttable(comment_id,answer_id,featured,vote_num,reply_num,content)
                             values('%s', '%s', '%s', %d, %d, '%s')"""\
                          % ('comment'+str(comment_id), 'comment'+str(ans_id), featured, vote_count,
                             child_comment_count, content)

            cursor.execute(sql_main)
            cursor.execute(sql_user)
            cursor.execute(sql_comment)
            db.commit()

            if child_comment_count > 0:
                childComentSpider(comment_id)
        if ans_json['paging']['is_end']:
            break

        next_url = ans_json['paging']['next']
        url = SpiderConfig.url + SpiderConfig.url_api + next_url[21:]  # 这里next给出的url没有带api/v4，需要添加上，不然无法请求成功
        response = requests.get(url, headers=SpiderConfig.headers)
        ans_json = json.loads(response.text)
    db.close()


def voterSpider(ans_id, ansor_id):
    url = SpiderConfig.url + SpiderConfig.url_api + r'/answers/' + str(ans_id) + r'/voters'
    response = requests.get(url, params=SpiderConfig.VoterSpiderParam, headers=SpiderConfig.headers)
    ans_json = json.loads(response.text)
    db = ZhihuSQL.connect()
    cursor = db.cursor()
    while True:
        for data in ans_json['data']:
            voter_id = data['id']
            voter_name = data['name']
            voter_name=pymysql.escape_string(voter_name)
            voter_id = pymysql.escape_string(voter_id)
            ansor_id = pymysql.escape_string(ansor_id)
            sql_main = """INSERT INTO zhihu(user1_id, user2_id, ACT_TYPE, content_id)
                          values('%s','%s',3, '%s')""" % (voter_id, ansor_id, 'answer'+str(ans_id))
            sql_user = """INSERT INTO usertable(user_id,name) select '%s','%s' from dual where not 
            exists(select 1 from usertable where user_id ='%s')""" \
                         % (voter_id, voter_name, voter_id)
            cursor.execute(sql_main)
            cursor.execute(sql_user)
            db.commit()
        if ans_json['paging']['is_end']:
            break
        url = ans_json['paging']['next']
        response = requests.get(url, headers=SpiderConfig.headers)
        ans_json = json.loads(response.text)

    db.close()


def AnswerSpider(url, quesor_id):
    url = url+r'/answers'
    response = requests.get(url, params=SpiderConfig.AnswerSpiderParam, headers=SpiderConfig.headers)
    ans_json = json.loads(response.text)
    db = ZhihuSQL.connect()
    cursor = db.cursor()
    while True:
        for data in ans_json['data']:
            # TODO 对数据进行操作
            ans_id = data['id']  # 回答的id
            comment_count = data['comment_count']  # 评论数量
            vote_count = data['voteup_count']  # 点赞数量
            author_name = data['author']['name']  # 撰写回答的人的名字
            author_id = data['author']['id']  # 撰写回答的人的id,是一串32位的字符串
            created_time = data['created_time']  # 发布答案的时间,时间戳形式
            updated_time = data['updated_time']  # 最近一次修改时间
            content = data['content']  # 回答的具体内容
            question_id = data['question']['id']  # 问题的id
            created_time_array = datetime.datetime.utcfromtimestamp(created_time)  # 将时间戳转化为数组
            created_time_real = created_time_array.strftime("%Y-%m-%d %H:%M:%S")  # 将时间数组转化为字符串的形式
            author_name = pymysql.escape_string(author_name)
            author_id = pymysql.escape_string(author_id)
            quesor_id = pymysql.escape_string(quesor_id)
            content = pymysql.escape_string(content)

            sql_ans = """INSERT INTO anstable(answer_id,question_id,comment_num,vote_num,content)
                     values('%s','%s',%d,%d,'%s')""" % ('answer'+str(ans_id), 'question'+str(question_id),
                                                        comment_count, vote_count, content)
            sql_user = """INSERT INTO usertable(user_id,name) select '%s','%s' from dual where not
                                              exists(select 1 from usertable where user_id ='%s')""" \
                       % (author_id, author_name, author_id)

            sql_maintable = """INSERT INTO zhihu(user1_id, user2_id, ACT_TYPE, content_id, TIME)
                               values('%s','%s',1,'%s', str_to_date(\'%s\','%%Y-%%m-%%d %%H:%%i:%%s'))""" \
                            % (author_id, quesor_id, 'answer'+str(ans_id), created_time_real)
            cursor.execute(sql_maintable)
            cursor.execute(sql_user)
            cursor.execute(sql_ans)
            db.commit()

            # voterSpider(ans_id, author_id)  # 爬取给该回答点赞的人
            commentSpider(ans_id, author_id)  # 爬取该回复下的评论

        if ans_json['paging']['is_end']:
            break
        url = ans_json['paging']['next']
        response = requests.get(url, headers=SpiderConfig.headers)  # 注意这里因为url从next中获得，已经带有参数了，不需要加参数
        try:
            ans_json = json.loads(response.text)
        except json.decoder.JSONDecodeError:
            file = open('logs.txt', 'a', encoding='utf-8')
            file.write(response.text)
            file.write(url)
            file.close()
    db.close()


def TopicSpider(type, TopicID, TopicName):

    if type == 'top_activity':
        param = {
            'limit': '5',
            'after_id': '0'
        }
    else:
        param = {
            'limit': '5',
            'offset': '0'
        }
    ID = TopicID[7:]
    url = SpiderConfig.url+SpiderConfig.url_api+r'/topics/'+ID+r'/feeds/'+type
    response = requests.get(url, params=param, headers=SpiderConfig.headers)
    ans_json = json.loads(response.text)

    i = 10    # 设置请求话题页面内容的次数，一次可以返回5个data
    while True and ((i > 0) or (i == -1)):
        for data in ans_json['data']:
            # TODO 提取问题页面的url，并且将问题的信息保存到数据库
            if data['target']['type'] == 'answer':
                db = ZhihuSQL.connect()
                cursor = db.cursor()
                sql = """select 1 from questiontable where question_id = %s limit 1""" \
                      % (data['target']['question']['id'])  # 判断问题是否爬取过
                cursor.execute(sql)
                result = cursor.fetchall()
                # print(result)

                if result:
                    continue
                else:
                    url_question = data['target']['question']['url']
                    param_que = {'include': 'author,answer_count'}  # 请求的参数加上这两个可以返回问题下的回答数量及提出问题的人
                    response_ques = requests.get(url_question, params=param_que, headers=SpiderConfig.headers)
                    ques_json = json.loads(response_ques.text)
                    author_id = ques_json['author']['id']  # 提问者的id
                    author_name = ques_json['author']['name']  # 提问者的姓名
                    answer_count = ques_json['answer_count']  # 问题下的回答数量
                    que_id = ques_json['id']  # 问题的id
                    created_time = ques_json['created']  # 问题发布时间，给出的是时间戳的形式
                    created_time_array = datetime.datetime.utcfromtimestamp(created_time)  # 将时间戳转化为数组
                    created_time_real = created_time_array.strftime("%Y-%m-%d %H:%M:%S")  # 将时间数组转化为字符串的形式
                    # TODO 插入获取到的信息
                    author_name = pymysql.escape_string(author_name)
                    author_id = pymysql.escape_string(author_id)
                    sql_main = """INSERT INTO zhihu(user1_id, user2_id, ACT_TYPE, content_id, TIME)
                             values('%s','0',0,'%s',str_to_date(\'%s\','%%Y-%%m-%%d %%H:%%i:%%s'))"""\
                          % (author_id, 'question'+str(que_id), created_time_real)

                    sql_user = """INSERT INTO usertable(user_id,name) select '%s','%s' from dual where not
                                  exists(select 1 from usertable where user_id ='%s')""" \
                               % (author_id, author_name, author_id)

                    sql_question = """INSERT INTO questiontable(question_id, topic, ans_num)
                                      values("%s","%s",%d)""" % ('question'+str(que_id), TopicName, answer_count)

                    cursor.execute(sql_user)
                    cursor.execute(sql_main)
                    cursor.execute(sql_question)
                    db.commit()
                    db.close()

                    url_answer = data['target']['question']['url']
                    AnswerSpider(url_answer, author_id)  # 爬取问题下的回答

        if ans_json['paging']['is_end'] == 'true':
            break
        url = ans_json['paging']['next']
        response = requests.get(url, headers=SpiderConfig.headers)  # 注意这里因为url从next中获得，已经带有参数了，不需要加参数
        ans_json = json.loads(response.text)
        i = i-1
        print(i)
        if i < -1:
            i = -1


