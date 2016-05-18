#-*- coding: utf-8 -*-
__author__ = 'sohyeon'

# result0.json keyword : 화재 -삼성화재
# result1.json keyword : 화재 -
# 20150101.json keyword : 화재 / date = 20150101

import urllib
import io
import json
import bs4
from bs4 import Comment
import requests
import os
import re
import chardet


# open json file and save as json_data
with open("./news_meta/20151231.json") as json_file:
    json_data = json.load(json_file)

folder = './articles/'
if not os.path.exists(folder):
    os.makedirs(folder)

i = 0

# call json_data one by one
for data in json_data:
    # get link and title
    link = data['link']
    title = data['title']

    # get article
    article = requests.get('http://news.khan.co.kr/kh_news/khan_art_view.html?artid=201603020801471&code=940202')

    encoding = chardet.detect(article.content)['encoding']
    if encoding is None:
        i += 1
        continue
    else:
        content = bs4.BeautifulSoup(article.content.decode(encoding,'ignore'))

    str_list = []
    # 기사에서 <p> 부분 불러오기
    p_content = content.findAll("p")
    for paragraph in p_content:
        str_list.append(paragraph.text)
    contents = ''.join(str_list)

    if contents is None:
        i += 1
        continue


    # 기사에서 <body> 부분 불러오기
    # content = content.find("body")
    # 기사에서 script, 주석 제거
    # if type(content) is not None:
    #     try:
    #         for script in content.findAll('script'):
    #             script.extract()
    #         for comment in content.findAll(text=lambda text: isinstance(text, Comment)):
    #             comment.extract()
    #     except:
    #         continue
    # else:
    #     continue

    # test: content.text 인코딩 문제 해결후 content로 저장
    # data['content'] = content.text.encode('euc-kr')

    # 기사 하나씩 저장하기

    with io.open(folder+'20151231_'+str(i)+'.txt', 'w+', encoding='utf8') as outfile:
        outfile.write(contents)

    print(link)

    i += 1
    print(i)
    # test: save as json
    # with io.open('result_with_content.json', 'w+', encoding='utf8') as outfile:
    #     json.dump(data, outfile, ensure_ascii=False)
