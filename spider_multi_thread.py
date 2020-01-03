"""
:Description:  异步实现并发
:Author:  Dexter Lien
:Create:  2020/1/3 12:12
Copyright (c) 2020, Dexter Lien All Rights Reserved.
"""
from contextlib import contextmanager
from datetime import datetime
from pyquery import PyQuery as pq
import requests
import os, json, uuid, shutil
import threading

from sqlalchemy.orm import sessionmaker, scoped_session
from model import *

Session = sessionmaker(bind=engine)
session = Session()


def fetch_one(url: str, session: Session):
    # 生成唯一标识码
    uid = uuid.uuid4().hex
    response = requests.get(url)
    if response.status_code == 200:
        doc = pq(response.content)
        # 电影标题
        title = doc('.info-title').text()
        # 磁力链接(多个)
        magnet_ = doc('.picture-container a')
        magnets = [{'name': a.text, 'url': a.attrib['href']} for a in magnet_]
        # 基本信息
        info_ = doc('.tiny-title')
        infos = []
        try:
            for i in info_:
                # 豆瓣评分后面使用了单独的span标签,需要额外处理一下
                if i.text.find('豆瓣') != -1:
                    k = i.text.split(':')[0]
                    v = i.find('span').text
                else:
                    k = i.text[:i.text.index('：')]
                    v = i.text[i.text.index('：') + 1:]
                infos.append({k: v})
        except:
            print('--基本信息获取出错--', url)

        # 剧情介绍
        intro = doc('.information-text').text()
        # 海报图片
        # pic_src = doc('.masonry__item img').attr('src')
        # try:
        #     with open(os.path.join('poster', f'{uid}.jpg'), 'wb') as f:
        #         pic_response = requests.get(pic_src, timeout=5)
        #         if pic_response.status_code == 200:
        #             f.write(pic_response.content)
        #
        #     print(f'[成功] UID:{uid}, 电影名:{title}')
        # except:
        #     print(f'[失败] 电影名:{title} URL:{url} 海报:{pic_src}')

        movie = {
            'uid': uid,
            'title': title,
            'magnets': json.dumps(magnets, ensure_ascii=False),
            'infos': json.dumps(infos, ensure_ascii=False),
            'intro': intro
        }

        session.add(Movie(**movie))


if __name__ == '__main__':
    # 对之前存在的数据进行清理
    # 清空数据表
    session.execute('delete from movies')
    session.commit()

    if os.path.exists('poster'):
        print('存在已有数据,进行清理')
        shutil.rmtree('poster')

    os.makedirs('poster')

    print('开怼')

    start = datetime.now()
    base_url = 'https://www.cilixiong.com/movie/'

    jobs = []

    for i in range(1, 5001):
        cur_url = base_url + f'{i}.html'
        t = threading.Thread(target=fetch_one, args=[cur_url, session])
        jobs.append(t)
        t.start()

    for job in jobs:
        job.join()

    session.commit()
    end = datetime.now()
    used_time = end - start
    print(f'总用时: {used_time.seconds}秒')
