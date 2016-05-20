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

# host_search(20)
HOST_LIST = ['경향신문', '국민일보', '뉴스1', '뉴시스', '동아일보', '로이터', '문화일보', '세계일보', '조선일보', '중앙일보', '채널A', '한겨레', '한국일보', 'JTBC', 'KBS', 'MBN', 'YTN', '뉴스와이어', '뉴시스와이어', '연합뉴스 보도자료']

# search date option
START_DATE = date(2010, 1, 1)
END_DATE = date(2016, 1, 1)

# query
QUERY_WORDS = '화재 -삼성화재 -동부화재 -메리츠화재'

# date range function
def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

# make url with date, query option
def make_url(date):
    target_date = date.strftime("%Y%m%d")
    next_date = (date + timedelta(1)).strftime("%Y%m%d")
    query = urllib.parse.quote_plus(QUERY_WORDS)
    # article's url must have &cluster=n
    url = 'http://search.daum.net/search?w=news&cluster=n&nil_search=btn&DA=NTB&enc=utf8'+ '&sd='+target_date+ '&ed='+target_date+ '&q=' + query
    return url

# get page html
def get_html(url):
    # requests
    data = requests.get(url)
    # get html
    html = bs4.BeautifulSoup(data.text)
    return html

# calculate the number of pages
# one page contains 10 articles
# (ex)13 articles need 2 pages
def page_count(html):
    total_count = html.find("span", attrs={'id': 'resultCntArea'})
    total_count = [int(s) for s in re.findall('\d+', total_count.text)][2]
    pages = total_count / 10 + 1
    return pages

# get article list
def get_article_list(html):
    articles = html.find("div", attrs={'id': 'newsColl'})
    articles = articles.findAll("div", attrs={'class': 'cont_inner'})
    return articles

# reshape date to "%Y-%m-%d" format
def reshape_date(date):
    # ~시간전, ~분전, ~초전 시간 고치기
    if re.search('전', date):
        if re.search('시간', date):
            date = datetime.now() - timedelta(hours=int(date.split("시간")[0]))
            date = date.strftime("%Y-%m-%d")
        elif re.search('분', date):
            date = datetime.now() - timedelta(minutes=int(date.split("분")[0]))
            date = date.strftime("%Y-%m-%d")
        elif re.search('초', date):
            date = datetime.now() - timedelta(seconds=int(date.split("초")[0]))
            date = date.strftime("%Y-%m-%d")
    else:
        date = datetime.strptime(date, "%Y.%m.%d")
        date = date.strftime("%Y-%m-%d")
    return date

# get article's maintext of html by host
def get_maintext(page, host):
    content = bs4.BeautifulSoup(page.content)

    body = None
    if host == "경향신문": body = content.find("div", attrs={'class': 'art_body'})
    elif host == '뉴스1': body = content.find("div", attrs={'id': 'articles_detail'})
    elif host in ('뉴시스', '동아일보', '국민일보'): body = content.find("div", attrs={'id': 'articleBody'})
    elif host == '문화일보': body = content.find("div", attrs={'id': 'NewsAdContent'})
    elif host == '세계일보': body = content.find("div", attrs={'id': 'article_txt'})
    elif host == '채널A': body = content.find("div", attrs={'class': 'article'})
    elif host == '조선일보': body = content.find("div", attrs={'class': 'par'})
    elif host == '중앙일보': body = content.find("div", attrs={'id': 'article_body'})
    elif host == '한겨레': body = content.find("div", attrs={'class': 'article-text'})
    elif host == '한국일보': body = content.find("article", attrs={'id': 'article-body'})
    elif host == 'JTBC': body = content.find("div", attrs={'id': 'articlebody'})
    elif host == 'KBS': body = content.find("div", attrs={'id': 'cont_newstext'})
    elif host == 'MBN': body = content.find("div", attrs={'id': 'newsViewArea'})
    elif host == 'YTN': body = content.find("div", attrs={'class': 'article_paragraph'})
    elif host in ('로이터', '연합뉴스 보도자료', '뉴스와이', '뉴시스와이어'): body = content.find("div", attrs={'id': 'dmcfContents'})
    # 다음 뉴스 홈페이지에 올라온 기사일 수 있다
    if body is None: body = content.find("div", attrs={'id': 'dmcfContents'})
    if body is None: body = content.find("body")

    return body.text

# write data to UTF-8 by ensure_ascii option
def write_data(date, data):
    with open("./out_article/fire_article/"+date+".json", 'a+') as outfile:
        json.dump(data, outfile, ensure_ascii=False)
        outfile.write("\n")

def main():
    # the number of articles
    count = 0

    # get search result page per day
    for single_date in daterange(START_DATE, END_DATE + timedelta(1)):

        # get result page's url of one target day
        base_url = make_url(single_date)

        # get the number of pages
        try:
            result_html = get_html(base_url)
            pages = page_count(result_html)
        except Exception as e:
            print(e)
            print(base_url)
            continue

        # parsing articles per page
        for page in range(1, int(pages)+1):

            # get one page's url (article's option is '&p=')
            target_url = base_url + "&p=" + str(page)

            #get article list
            try:
                page_html = get_html(target_url)
                articles = get_article_list(page_html)
            except Exception as e:
                print(e)
                print(target_url)
                continue


            for article in articles:

                # get article's date and host
                date_and_host = str(article.findAll("span", attrs={'class': 'date'})[0])

                # get article in major media
                host = date_and_host.split("\n")[2].split("</span>")[1].strip()
                if host not in HOST_LIST:
                    continue

                # get article's title and link
                title_and_link = article.findAll("a")[0]
                title = title_and_link.text
                link = title_and_link["href"]

                # get article's date
                date = date_and_host.split("\n")[1]
                # reshape date to "%Y-%m-%d" format
                date = reshape_date(date)

                # get blog's original html
                try:
                    # requests
                    article_page = requests.get(link)
                    # set article encoding
                    article_page.encoding = article_page.apparent_encoding
                    article_html = article_page.text.strip()
                except Exception as e:
                    print(e)
                    print(link)
                    continue

                # get article's maintext
                try:
                    article_main =get_maintext(article_page, host)
                except Exception as e:
                    article_main = 0
                    print(e)
                    print(link)

                # one article data to write
                article_data = {"query": QUERY_WORDS, "title": title, "link": link, "date": date,
                                "content": article_html, "host": host, "body": article_main}

                # write data
                try:
                    write_data(date, article_data)
                except Exception as e:
                    print(e)
                    print(link)
                    continue

                # count number of articles that wrote to file
                count += 1
                print("date : " + single_date.strftime("%Y%m%d") + " / count : " + str(count))


if __name__ == '__main__':
    main()
