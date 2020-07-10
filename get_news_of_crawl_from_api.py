# -*- encoding:utf8 -*-

'''
# 目标：获取某个时间区间内爬虫爬取的所有资讯新闻（全局资讯）的相关信息（资 讯标题、来源、url、内容等）
#      同时要求将 资讯 title 与 content 分词后的结果也一同存入
#
# step1、先从 'http://information-doc-service:31001/information/search?' 中获取资讯新闻的 id
# step2、再根据 step1 中资讯新闻的 id 从 'http://information-doc-service:31001/information/detail/' 中获取 详细信息（资讯的内容等）
# step3、根据需求，组合 step1 和 step2 的数据，进行适当变换，按照一定格式存储到文件中。
# '''
import io
import os
import time_utils
import json
import requests
import logging as logger
import codecs
import time


def timestamp_to_date(timestamp):
    timeArray = time.localtime(timestamp / 1000)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime


# 去杂质（标签），因为分词时用不到杂质
def strip_tags(html):
    import re
    dr = re.compile(r'<[^>.*]+>', re.S)
    dd = dr.sub('', html)
    return dd


# 分词
def split_sentence(sen):
    nlp_url = 'http://hanlp-rough-service:31001/hanlp/segment/rough'
    try:
        cut_sen = dict()
        cut_sen['content'] = sen
        data = json.dumps(cut_sen).encode("UTF-8")
        cut_response = requests.post(nlp_url, data=data)
        cut_response_json = cut_response.json()
        return cut_response_json['data']
    except Exception as e:
        print.exception("Exception: {}".format(e))
        return []


# step1、step2
def get_news_from_api(start_time, end_time, data_file):
    list_url = 'http://information-doc-service:31001/information/search?'
    detail_url = 'http://information-doc-service:31001/information/detail/'
    ids_count = 0
    try:
        cp = 1
        while True:
            params = dict()
            params["cp"] = cp
            params["ps"] = 1000
            params["timeField"] = 'publishAt'
            params["startAt"] = start_time
            params["endAt"] = end_time

            r = requests.get(list_url, params)
            result_json = r.json()

            if len(result_json['data']) == 0:
                break

            with io.open(data_file, 'a', encoding='utf-8') as f:
                for item in result_json['data']:
                    try:
                        detail_result = requests.get(detail_url + item['id'])
                        detail_json = detail_result.json()

                        if 'title' in detail_json['data'] and 'content' in detail_json['data']:
                            title = detail_json['data']['title']
                            detail_json['data']['seg_title'] = split_sentence(title)
                            detail_json['data']['content'] = detail_json['data']['content']
                            content = strip_tags(detail_json['data']['content'])
                            detail_json['data']['seg_content'] = split_sentence(content)
                    except Exception as e:
                        print('title and content not in news')
                        continue
                    ids_count += 1
                    f.write(json.dumps(detail_json['data'], ensure_ascii=False) + "\n")
            cp += 1
    except Exception as e:
        print("Exception: {}".format(e))

    print("all_ids: {}".format(ids_count))


def test():
    folder = 'for_dndx/'
    start_time = 1538323200000  # 2018.10.1
    end_time = start_time + 24 * 60 * 60 * 1000
    start_time = time_utils.n_days_ago_milli_time(1)

    end_time = time_utils.current_milli_time()
    epoch = 1  # 天数，一天一处理

    for i in range(0, epoch):
        end_time = start_time + 24 * 60 * 60 * 1000
        data_file = folder + timestamp_to_date(start_time).split(' ')[0] + '.txt'
        print(data_file)

        get_news_from_api(start_time, end_time, data_file)

        start_time = end_time


if __name__ == '__main__':
    test()








