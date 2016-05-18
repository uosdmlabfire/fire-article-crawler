#-*- coding: utf-8 -*-
__author__ = 'sohyeon'

# result0.json keyword : 화재 -삼성화재
# result1.json keyword : 화재 -
# 20150101.json keyword : 화재 / date = 20150101

import requests
import bs4
import re
import json
import urllib
from datetime import datetime, timedelta, date


# Requests
# daum 뉴스 검색 : 화재

# date range function
def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

#media_search
media_list = ['경향신문', '국민일보', '뉴스1', '뉴시스', '동아일보','로이터','문화일보', '세계일보', '연합뉴스', '조선일보','중앙일보', '채널A', '한겨레', '한국일보', 'JTBC', 'KBS', 'MBC', 'MBN','SBS', 'YTN', '뉴스와이어', '뉴시스와이어', '연합뉴스 보도자료']
# 검색 날짜 조건
start_date = date(2015, 1, 2)
end_date = date(2016, 1, 1)

# 검색어
SEARCH_WORD = '화재 -삼성화재 -동부화재 -메리츠화재'

# 크롤링한 기사수
count = 0

for single_date in daterange(start_date, end_date):

    target_date = single_date.strftime("%Y%m%d")
    next_date = (single_date + timedelta(1)).strftime("%Y%m%d")
    query = urllib.parse.quote_plus(SEARCH_WORD)

    # 화재, 뉴스 / 반드시 관련기사 닫기 &cluster=n 으로 검색해야된다!!
    BASE_URL = 'http://search.daum.net/search?w=news&cluster=n&nil_search=btn&DA=NTB&enc=utf8'+ '&sd='+target_date+ '&ed='+next_date+ '&q=' + query

    data = requests.get(BASE_URL)

    # Parsing ( totalCount )
    data = bs4.BeautifulSoup(data.text)

    # 다른 방식으로 total_count 얻어오기
    # total_count = data.find("span", attrs={'id': 'resultCntArea'})


    try :
        match = re.search("totalCount: [0-9]+", data.text)
        total_count = int(match.group(0).split("totalCount: ")[1])
    except Exception as e:
        print(e)
        print("target_date : "+ target_date)
        break

    # Calc Pages
    # 1 페이지당 10개의 기사가 보여진다.c
    # 예, 23개의 기사일 경우 3페이지까지 있다.
    pages = total_count / 10 + 1

    # Parsing Articles per Page
    for page in range(1, int(pages)+1):
        TARGET_URL = BASE_URL + "&p=" + str(page)

        try:
            data = requests.get(TARGET_URL)
        except Exception as e:
            print(e)
        data = bs4.BeautifulSoup(data.text)

        try:
            articles = data.findAll("div", attrs={'class': 'cont_inner'})
        except Exception as e:
            print(e)
            print(TARGET_URL)

        for article in articles:

            # date와 media 부분 추출
            date_and_media = str(article.findAll("span", attrs={'class': 'date'})[0])

            # media를 추출해서 media_list에 있는지 확인, 없으면 다음 기사 추출
            media = date_and_media.split("\n")[2].split("</span>")[1].strip()
            if media not in media_list:
                continue


            title_and_link = article.findAll("a")[0]
            title = title_and_link.text
            link = title_and_link["href"]

            # 시간 추출
            date = date_and_media.split("\n")[1]

            # ~시간전, ~분전, ~초전  시간 고치기
            if re.search('전', date):
                if re.search('시간',date):
                    date = datetime.now() - timedelta(hours=int(date.split("시간")[0]))
                    date = date.strftime("%Y-%m-%d")
                elif re.search('분',date):
                    date = datetime.now() - timedelta(minutes=int(date.split("분")[0]))
                    date = date.strftime("%Y-%m-%d")
                elif re.search('초',date):
                    date = datetime.now() - timedelta(seconds=int(date.split("초")[0]))
                    date = date.strftime("%Y-%m-%d")
            else:
                date = datetime.strptime(date, "%Y.%m.%d")
                date = date.strftime("%Y-%m-%d")

            #본문 html 가져오기
            # get blog_html
            try:
                article_content = requests.get(link.encode('utf-8'))
                article_content.encoding = article_content.apparent_encoding
            except Exception as e:
                print(e)
                print(link)
                continue

            #file에 입력할 하나의 article date
            article_data = {"query": SEARCH_WORD, "title": title, "link": link, "date": date, "media": media, "content": article_content.text.strip()}

            count += 1

            # ensure_ascii 옵션으로 UTF-8 ( 한글로 보이도록 ) 출력한다.
            try:
                with open("article_data/fire_article.json", 'a') as outfile:
                    json.dump(article_data, outfile, ensure_ascii=False)
                    outfile.write("\n")
            except Exception as e:
                print(e)
                print("link: " + link)
                continue


            print("date : " + target_date + " / count : " + str(count))
