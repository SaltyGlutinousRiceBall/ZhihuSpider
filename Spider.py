#-*-coding:utf-8-*-
import ManySpiders
import SpiderConfig
import ZhihuSQL
import datetime
import requests
import json
import pymysql

keywords = r'夙愿'
db = ZhihuSQL.connect()
cursor = db.cursor()
# TODO 创建表
cursor.execute(ZhihuSQL.maintable)
cursor.execute(ZhihuSQL.user_table)
cursor.execute(ZhihuSQL.question_table)
cursor.execute(ZhihuSQL.answer_table)
cursor.execute(ZhihuSQL.comment_table)
cursor.execute(ZhihuSQL.reply_table)
db.close()

print(datetime.datetime.now())

a, topicId, topicName = ManySpiders.hastopic(keywords)
# TODO 如果a为真，表示关键字有话题
if a:
    ManySpiders.TopicSpider(SpiderConfig.questionSortType, topicId, topicName)
    print(datetime.datetime.now())
else:
    url = r'http://www.zhihu.com/api/v4/search_v3'
    param = {
        't': 'general',
        'q': keywords,
        'correction': '1',
        'offset': '0',
        'limit': '20',
        'search_hash_id': '518a3381800d1d7597363bc961824b1c'
    }

    response = requests.get(url, params=param, headers=SpiderConfig.headers)
    ans_json = json.loads(response.text)
    print(ans_json)

    i = 10  # 设置请求话题页面内容的次数，一次可以返回5个data
    while True and ((i > 0) or (i == -1)):
        for data in ans_json['data']:
            if data['object']['type'] == 'answer':
                db = ZhihuSQL.connect()
                cursor = db.cursor()
                sql = """select 1 from questiontable where question_id = %s limit 1""" \
                      % (data['object']['question']['id'])  # 判断问题是否爬取过
                cursor.execute(sql)
                result = cursor.fetchall()
                print(result)

                if result:
                    continue
                else:
                    url_question = data['object']['question']['url']
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
                                                 values('%s','0',0,'%s',str_to_date(\'%s\','%%Y-%%m-%%d %%H:%%i:%%s'))""" \
                               % (author_id, 'question' + str(que_id), created_time_real)

                    sql_user = """INSERT INTO usertable(user_id,name) select '%s','%s' from dual where not
                                                      exists(select 1 from usertable where user_id ='%s')""" \
                               % (author_id, author_name, author_id)

                    sql_question = """INSERT INTO questiontable(question_id, topic, ans_num)
                                                          values("%s","%s",%d)""" % (
                                             'question' + str(que_id), '无', answer_count)

                    cursor.execute(sql_user)
                    cursor.execute(sql_main)
                    cursor.execute(sql_question)
                    db.commit()
                    db.close()

                    url_answer = data['object']['question']['url']
                    ManySpiders.AnswerSpider(url_answer, author_id)  # 爬取问题下的回答

        if ans_json['paging']['is_end'] == 'true':
            break
        url = ans_json['paging']['next']
        response = requests.get(url, headers=SpiderConfig.headers)  # 注意这里因为url从next中获得，已经带有参数了，不需要加参数
        ans_json = json.loads(response.text)
        i = i-1
        print(i)
        if i < -1:
            i = -1


