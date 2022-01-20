# -*- coding: utf-8 -*-
"""

小红书博主信息、笔记信息爬虫（写给雪绒）
—— kuloud 2022/1/20

Example:

1. 自行抓包小红书小程序，找用户token，替换{$authorizations}（其实1个就够了，但是小红书访刷做了很多限制，请求频次10s一次基本够用）
2. 需要定期爬的链接列表，自行替换{$URL}
3. 运行脚本，在当前目录生成对应的csv数据

    $ python3 xhs.py


"""
import re
import requests
import csv
import hashlib
import time

def m_md5(data: str):
    m = hashlib.md5()
    m.update(data.encode())
    return m.hexdigest()

def get_user(user_id, authorization=''):
    headers['authorization'] = authorization
    URI = f'/fe_api/burdock/weixin/v2/user/{user_id}'
    xsign = 'X' + m_md5(URI + "WSUDD")
    headers['x-sign'] = xsign
    return gets(URI)

def get_note(user_id, authorization=''):
    headers['authorization'] = authorization
    URI = f'/fe_api/burdock/weixin/v2/note/{user_id}/single_feed'
    xsign = 'X' + m_md5(URI + "WSUDD")
    headers['x-sign'] = xsign
    return gets(URI)

def gets(url_path):
    base_url = 'https://www.xiaohongshu.com'
    data = requests.get(base_url+url_path, headers=headers,
                        verify=False).json()
    return data

def write_csv_headers(filename, csv_headers):
    f = open(filename, 'a+', encoding='utf-8')  # a+表示追加
    csv_writer = csv.writer(f)

    csv_writer.writerow(csv_headers)

    f.close()

def write_user_info(url, filename, data):
    id = data['id']
    nickname = data['nickname']
    gender = '男' if data['gender'] == 0 else '女' if data['gender'] == 1 else '未知'
    fans = data['fans']
    follows = data['follows']
    notes = data['notes']
    location = data['location']
    collected = data['collected']
    desc = data['desc']
    liked = data['liked']
    level = data['level']['name']
    officialVerifyName = data['officialVerifyName']

    fetch_time = time.strftime("%Y-%m-%d_%H:%M:%S",time.localtime())

    record = "url: {}, 用户名：{}, 性别：{}, 粉丝数：{}, 关注数：{}, 收藏数：{}, 笔记数: {}, 点赞数：{}, 等级：{}, 位置：{}, 认证名：{}, 主页描述：{}, 数据时间：{}".format(
        url, nickname,  gender, fans, follows, collected, notes, liked, level, location, officialVerifyName, desc, fetch_time
    )

    f = open(filename, 'a+', encoding='utf-8')  # a+表示追加
    csv_writer = csv.writer(f)

    print(record)
    csv_writer.writerow([url, nickname,  gender, fans, follows, collected, notes, liked, level, location, officialVerifyName, desc])

    f.close()

def write_note_info(url, filename, data):
    id = data['id']
    title = data['title']
    likes = data['likes']
    collects = data['collects']
    comments = data['comments']
    note_time = data['time']
    type = data['type']

    fetch_time = time.strftime("%Y-%m-%d_%H:%M:%S",time.localtime())

    record = "链接: {}, 标题：{}, 点赞数：{}, 收藏数：{}, 评论数：{}, 类型：{}, 发布日期: {}, 数据时间：{}".format(
        url, title,  likes, collects, comments, type, note_time, fetch_time
    )

    f = open(filename, 'a+', encoding='utf-8')  # a+表示追加
    csv_writer = csv.writer(f)

    print(record)
    csv_writer.writerow([url, title,  likes, collects, comments, type, note_time, fetch_time])

    f.close()

def fetch_users():
    export_file_name = 'xhs_users_{}.csv'.format(time.strftime("%Y-%m-%d_%H:%M:%S",time.localtime()))
    users = [
'{$URL}'
    ]
    csv_headers = ['链接', '用户名',  '性别', '粉丝数', '关注数', '收藏数', '笔记数', '点赞数', '等级', '位置', '认证名', '主页描述', '数据时间']
    write_csv_headers(filename=export_file_name, csv_headers=csv_headers)

    for i, u in enumerate(users):
        try:
            uid = re.findall(r"profile/(.+)\?", u)[0]
            authorization = authorizations[i % len(authorizations)]
            print("{}/{} uid: {}, authorization: {}".format(i + 1, len(users), uid,authorization))
            userData = get_user(uid,authorization=authorization)
            write_user_info(url=u,filename=export_file_name, data=userData['data'])
        except Exception as e:
            print('handle user error: {} \n {}'.format(u, e))
            pass
        time.sleep(10)

def fetch_notes():
    export_file_name = 'xhs_notes_{}.csv'.format(time.strftime("%Y-%m-%d_%H:%M:%S",time.localtime()))
    notes = [
'{$URL}'
    ]
    csv_headers = ['链接', '标题', '点赞数',  '收藏数', '评论数', '类型（视频或者图文）', '发布日期', '数据时间']
    write_csv_headers(filename=export_file_name, csv_headers=csv_headers)

    for i, n in enumerate(notes):
        try:
            if not n.startswith('http://xhslink.com'):
                # write_note_info(url=n,filename=export_file_name, data={})
                continue
            r = requests.get(n, verify=False,allow_redirects=True)
            origin = r.history[0].headers['Location']
            uid = re.findall(r"/discovery/item/(.+)\?", origin)[0]
            authorization = authorizations[i % len(authorizations)]
            print("{}/{} uid: {}, authorization: {}".format(i + 1, len(notes), uid,authorization))
            noteData = get_note(uid,authorization=authorization)
            # print(noteData)
            write_note_info(url=n,filename=export_file_name, data=noteData['data'])
        except Exception as e:
            print('handle note error: {} \n {}'.format(n, e))
            pass
        time.sleep(10)        

if __name__ == '__main__':
    requests.packages.urllib3.disable_warnings()

    headers = {
        'Host': 'www.xiaohongshu.com',
        'device-fingerprint': 'WHJMrwNw1k/EDrs4qQu7qho7mmYuri0YzaIx1p+ZruHXU5ABFod6r13el9Gk7wXXC5zMfJLxaBMpubNTyqfbLczzvrRRHlcJkdCW1tldyDzmauSxIJm5Txg==1487582755342',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat',
        'content-type': 'application/json'
    }

    authorizations = ['{$authorizations}']

    fetch_users()
    fetch_notes()
    
    
