
# 目标：获取某个时间区间内的所有「事件」所对应的「事件概述」与「事件影响」。
#
# step1、获取某个时间区间内的所有 cluster（事件） 的信息（包括 cluster_id、title、publish_time、keywords等）
# step2、利用 step1 结果中的 cluster_id 获取 每个簇内的所有特征（“事件概述”、“事件影响”）
# step3、根据需求，组合 step1 和 step2 的数据，进行适当变换，按照一定格式存储到文件中。
# '''
import io
import os
import json
import requests
import logging.config
import codecs
import time_utils
import hashlib
import requests


# step1
def get_cluster_info_from_api(start_time, end_time):
    cluster_ids = []
    cluster_infos = []
    url = "http://information-doc-service:31001/cluster/search"

    totalCount = 0

    try:
        cp = 1
        while True:
            params = dict()
            params["cp"] = cp
            params["ps"] = 50
            params["clusterTypes"] = ['热点事件']
            params["delFlag"] = 0
            params["timeField"] = 'publishAt'
            params["startAt"] = start_time
            params["endAt"] = end_time

            r = requests.get(url, params)
            result_json = r.json()
            # print(result_json)
            # break
            totalCount = result_json['data']['totalCount']
            if len(result_json['data']['list']) == 0:
                break
            for item in result_json['data']['list']:
                cluster_id = item['id']  # 簇的id
                keywords = item['keywords']  # 簇的关键词（由簇内的所有资讯标题统计出的）
                createAt = item['createAt']  # 簇的创建时间


                publishAt = item['publishAt']  # 簇（事件）内最新（近）的一篇资讯的发布时间
                title = item['title']  # 簇（事件）的标题 目前为簇内某（按相关程度）篇资讯的一个标题
                hot = item['hot']  # 簇内的资讯数量 即热度

                cluster_ids.append(cluster_id)
                cluster_infos.append({'cluster_id': cluster_id,
                                      'keywords': keywords,
                                      'createAt': createAt,
                                      'publishAt': publishAt,
                                      'title': title,
                                      'hot': hot})
            cp += 1
    except Exception as e:
        # logger.exception("Exception: {}".format(e))
        print("Exception: {}".format(e))
    # logger.info("get_cluster_info_from_api count: {}".format(totalCount))
    print("get_cluster_info_from_api count: {}".format(totalCount))
    # print(cluster_ids)
    return cluster_ids, cluster_infos


# step2
def get_cluster_infoids_feature_from_api(clusterIds):
    url = 'http://index-information-service:31001/information/relation/search'

    totalCount = 0
    clusters = []
    # 由于 clusterIds 可能很多，分批取
    batch_size = 50
    epoch = int(len(clusterIds) / batch_size) + 1       #在clusterIds中每隔50个取一个clusterId
    begin = 0

    # 遍历取数据
    for i in range(0, epoch):

        clusterIds_ = clusterIds[begin: begin + batch_size]
        # clusters.append(clusterIds)
        begin += batch_size

        try:
            cp = 1
            while True:
                params = dict()
                params["cp"] = cp
                params["ps"] = 50
                params["clusterIds"] = clusterIds_
                params["delFlag"] = 0
                params["relationTypes"] = "事件概述"
                params["human"] = 0
                # params["startAt"] = start_time
                # params["endAt"] = end_time
                params["relationMethods"] = 'CLUSTER'

                r = requests.get(url, params)
                result_json = r.json()

                # print(result_json)
                # break
                totalCount = result_json['data']['totalCount']
                if len(result_json['data']['list']) == 0:
                    break
                for item in result_json['data']['list']:
                    # contentId
                    # id
                    # editAt
                    # mediaFrom
                    # 'relationType': ['事件影响']
                    # title
                    cluster_id = item['clusterId']
                    content = item['content']
                    createAt = item['createAt']
                    publishAt = item['publishAt']
                    relationType = item['relationType']
                    # if '事件影响' in relationType:
                    #   print(content)
                    #  print(relationType)
                    with io.open('./for_dndx/cluster_feature.txt', 'a', encoding='utf-8') as f2:
                        f2.write(json.dumps(item, ensure_ascii=False) + "\n")

                cp += 1
        except Exception as e:
            # logger.exception("Exception: {}".format(e))
            print("Exception: {}".format(e))
    # logger.info("get_cluster_infoids_feature_from_api count: {}".format(totalCount))
    # print(clusters)
    print("get_cluster_infoids_feature_from_api count: {}".format(totalCount))


# step2
def get_info_ids_by_cluster_id_from_api(cluster_id):
    info_ids = []
    info_ids_detail = []
    url = "http://index-information-service:31001/cluster/information/search"

    totalCount = 0

    try:
        cp = 1
        while True:
            params = dict()
            params["cp"] = cp
            params["ps"] = 50
            params["clusterIds"] = cluster_id
            params["clusterTypes"] = ['热点事件']

            r = requests.get(url, params)
            result_json = r.json()

            # print(result_json)
            # break
            totalCount = result_json['data']['totalCount']
            if len(result_json['data']['list']) == 0:
                break

            for item in result_json['data']['list']:
                cluster_id = item['clusterId']  # 簇的id
                info_id = item['infoid']
                machineTitle = item['machineTitle']  # 资讯的标题
                url = item['url']

                info_ids.append(info_id)
                info_ids_detail.append({'cluster_id': cluster_id,
                                        'info_id': info_id,
                                        'machineTitle': machineTitle,
                                        'url': url})
            cp += 1
    except Exception as e:
        # logger.exception("Exception: {}".format(e))
        print("Exception: {}".format(e))
    # logger.info("get_cluster_info_from_api count: {}".format(totalCount))
    print("get_info_ids_by_cluster_id_from_api count: {}".format(totalCount))
    return info_ids, info_ids_detail


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

def get_news_detial_by_infoids_from_api_(info_ids):

    detail_url = 'http://information-doc-service:31001/information/detail/'
    ids_count = 0
    info_ids_detail = []

    for info_id in info_ids:
        try:
            detail_result = requests.get(detail_url + info_id)
            detail_json = detail_result.json()

            if 'title' in detail_json['data'] and 'content' in detail_json['data']:
                title = detail_json['data']['title']
                detail_json['data']['seg_title'] = split_sentence(title)
                detail_json['data']['content'] = detail_json['data']['content']
                content = strip_tags(detail_json['data']['content'])
                detail_json['data']['seg_content'] = split_sentence(content)
                info_ids_detail.append(detail_json['data'])
                ids_count += 1
        except Exception as e:
            print('title and content not in news')
            continue
    ids_count += 1

    print("all_ids: {}".format(ids_count))
    return info_ids_detail


if __name__ == '__main__':
    start_time = 1551196800000  # 1.14.00
    end_time = 1551283200000

    start_time = time_utils.n_days_ago_milli_time(100)

    end_time = time_utils.current_milli_time()

    cluster_ids, cluster_infos = get_cluster_info_from_api(start_time, end_time)

    cluster_ids_ = []
    for i in range(0, len(cluster_ids)):
        info_ids, info_ids_detail = get_info_ids_by_cluster_id_from_api(cluster_ids[i])
        if len(info_ids) > 3:
            cluster_ids_.append(cluster_ids[i])

            temp_dic = cluster_infos[i]
            temp_dic['info_ids'] = info_ids

            with io.open('./for_dndx/cluster_info.txt', 'a', encoding='utf-8') as f:
                f.write(json.dumps(temp_dic, ensure_ascii=False) + "\n")

            info_ids_detail = get_news_detial_by_infoids_from_api_(info_ids)
            for info_id_detail in info_ids_detail:
                with io.open('./for_dndx/infoids_detail.txt', 'a', encoding='utf-8') as f1:
                    f1.write(json.dumps(info_id_detail, ensure_ascii=False) + "\n")

    get_cluster_infoids_feature_from_api(cluster_ids_)



