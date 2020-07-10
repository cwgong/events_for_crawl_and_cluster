# -*- coding: utf-8 -*-
#
# '''
# 目标：获取某个时间区间内的所有簇「事件」所对应的簇内资讯id。
#
# step1、获取某个时间区间内的所有 cluster（事件） 的信息（包括 cluster_id、title、publish_time、keywords等）
# step2、利用 step1 结果中的 cluster_id 获取 每个簇内的所有资讯id
# '''
import io
import os
import json
import requests
import logging.config
import codecs
import time_utils
import hashlib
import datetime,time


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
    return cluster_ids, cluster_infos


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

if __name__ == '__main__':

    start_time = 1540828800.0  # 1.14.00
    end_time = 1551369600.0

    cluster_ids, cluster_infos = get_cluster_info_from_api(start_time, end_time)
    for cluster_id in cluster_ids:
        info_ids, info_ids_detail = get_info_ids_by_cluster_id_from_api(cluster_id)
        print(info_ids)









