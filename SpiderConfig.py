User_Agent = r"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
             r"Chrome/74.0.3729.131 Safari/537.36"
headers = {
    'cookie': r'_zap=154fc215-123f-4cbc-bc04-48e6274d3ced;'
              ' d_c0="AJAh7D4ypg6PThlE5-QkMnDPa_Nop72y1xo=|1544451411"; '
              '_xsrf=3IWLKly38CdTLrMoBjoIWRiitKsjJ8pZ;'
              ' z_c0="2|1:0|10:1547566271|4:z_c0|92:Mi4xWHpxWkF3QUFBQUFBa0NIc1BqS21EaVlBQUFCZ0Fs'
              'Vk52MG9yWFFCelBlUGN6VXVPQlZQaGJQLUdxcHpkRHc1NmN3|836d1ba7f29e48c226cb3026005926ad3d6'
              '16d3371f3fec453aad219ec265f57"; tst=r; __gads=ID=32d01d3ef667ac14:T=1553164371:S=ALNI_MZfa3pWg2XWF9'
              'QyqobNZoUgxb3DAQ; q_c1=8447e4607d40416bb54fe6178dc9a6cd|1555382300000|1544451412000; '
              '__utma=51854390.563388899.1556943907.1556943907.1556943907.1; __utmz=51854390.1556943907'
              '.1.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utmv=51854390.100--|2=registration'
              '_date=20161021=1^3=entry_date=20161021=1; tgw_l7_route=537a925d07d06cecbf34cd06a153f671',
    "User-Agent": User_Agent
}
# **********************************************************************************************************
# **********************************************************************************************************
# **********************************************************************************************************
# ********************************************只需要修改上面的数据*******************************************
# **********************************************************************************************************
# **********************************************************************************************************

url = r'https://www.zhihu.com'
url_api = r'/api/v4'
questionSortType = r'top_activity'
AnswerSpiderParam = {
    'include': r'data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,annotation_action,annotation_detail,'
               r'collapse_reason,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,content,'
               r'editable_content,voteup_count,reshipment_settings,comment_permission,created_time,'
               r'updated_time,review_info,relevant_info,question,excerpt,relationship.is_authorized,'
               r'is_author,voting,is_thanked,is_nothelp,is_labeled,is_recognized,paid_info;data[*].'
               r'mark_infos[*].url;data[*].author.follower_count,badge[*].topics',
    'limit': '5',
    'offset': '0',
    'platform': 'desktop',
    'sort_by': 'default'
}

CommentSpiderParam = {
    'include': r'data[*].author,collapsed,reply_to_author,disliked,content,voting,vote_count,'
               r'is_parent_author,is_author',
    'order': 'normal',
    'limit': '20',
    'offset': '0',
    'status': 'open'
}

ChildCommentSpiderParam = {
    'include': '$[*].author,reply_to_author,content,vote_count',
    'limit': '20',
    'offset': '0'
}

VoterSpiderParam = {
    'include': r'data[*].answer_count,articles_count,follower_count,gender,is_followed,is_following,badge',
    'limit': '10',
    'offset': '0'
}