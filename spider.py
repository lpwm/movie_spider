"""
:Description:  电影磁力链接那啥
:Author:  Dexter Lien
:Create:  2020/1/3 12:12
Copyright (c) 2020, Dexter Lien All Rights Reserved.
"""
from datetime import datetime
from pyquery import PyQuery as pq
import requests
import os, json, uuid, shutil

from sqlalchemy.orm import sessionmaker
from model import *
Session = sessionmaker(bind=engine)
session = Session()


def fetch_one(url: str):
    # 生成唯一标识码
    uid = uuid.uuid4().hex
    response = requests.get(url)
    doc = pq(response.content)
    # 电影标题
    title = doc('.info-title').text()
    # 磁力链接(多个)
    magnet_ = doc('.picture-container a')
    magnets = [{'name': a.text.replace(' 磁力下载', ''), 'url': a.attrib['href']} for a in magnet_]
    # 基本信息
    info_ = doc('.tiny-title')
    infos = []
    for i in info_:
        # 豆瓣评分后面使用了单独的span标签,需要额外处理一下
        if i.text.find('豆瓣') != -1:
            k = i.text.split(':')[0]
            v = i.find('span').text
        else:
            k, v = i.text.split('：')

        infos.append({k: v})
    # 剧情介绍
    intro = doc('.information-text').text()
    # 海报图片
    pic_src = doc('.masonry__item img').attr('src')
    with open(os.path.join('poster', f'{uid}.jpg'), 'wb') as f:
        f.write(requests.get(pic_src).content)

    print(f'UID:{uid}, 电影名:{title}')
    return {
        'uid': uid,
        'title': title,
        'magnets': json.dumps(magnets, ensure_ascii=False),
        'infos': json.dumps(infos, ensure_ascii=False),
        'intro': intro
    }


if __name__ == '__main__':
    # 对之前存在的数据进行清理
    if os.path.exists('poster'):
        shutil.rmtree('poster')
        # 清空数据表
        session.execute('delete from movies')
        session.commit()

    os.makedirs('poster')

    start = datetime.now()
    base_url = 'https://www.cilixiong.com/movie/'
    movies = []
    for i in range(1, 6):
        cur_url = base_url + f'{i}.html'
        movie = fetch_one(cur_url)
        movies.append(movie)

    # 数据写入SQLite
    session.add_all([Movie(**m) for m in movies])
    session.commit()

    end = datetime.now()
    used_time = end - start
    print(f'总用时: {used_time.seconds}秒')
    # json_data = json.dumps(movies, ensure_ascii=False, indent=4)
    # # 注意指定写入文件的编码,否则中文写入后容易出现问题
    # with open('movies.json', 'w', encoding='utf-8') as f:
    #     f.write(json_data)
    # print('JSON格式数据保存成功!')
