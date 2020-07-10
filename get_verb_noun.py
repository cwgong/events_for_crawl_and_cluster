import io
import json
import requests


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

if __name__ == '__main__':

    verbs1 = []
    orgs = []
    nouns = []
    nrs = []
    with io.open('./for_fx4.txt', "r", encoding='utf-8') as f:
        while True:
            line = f.readline()
            if len(line.strip()) > 0:
                json_data = json.loads(line)
                p_seg = json_data['p_seg']
                for term in p_seg:
                    if(term['nature'].startswith('n')):
                        nouns.append(term['word'])
                        # print(term['word'])
                for term in p_seg:
                    if (term['nature'].startswith('v')):
                        verbs1.append(term['word'])
                for term in p_seg:
                    if (term['nature'].startswith('nr') or term['nature'].startswith('fxs')):
                        nrs.append(term['word'])

            else:
                break

    verbs_set = list(set(verbs1))  # 对所得的动词进行去重处理
    verbs_sets = [0] * len(verbs_set)   # 根据去重后的动词数量设置一个单位矩阵

    for word in verbs1:
        if word in verbs_set:   # 如果该词语在动词列表里，就让另外一个单位矩阵对应的位置加一
            verbs_sets[verbs_set.index(word)] += 1

    verb1_dict = dict(map(lambda x, y: [x, y], verbs_set, verbs_sets))
    source_count_sort1 = sorted(verb1_dict.items(), key=lambda d: d[1], reverse=True)  #制作字典并且作排序

    # for word in source_count_sort1:
    #     print(word)

    nouns_set = list(set(nouns))  # ******需要注释
    nouns_sets = [0] * len(nouns_set)

    for word in nouns:
        if word in nouns_set:
            nouns_sets[nouns_set.index(word)] += 1

    noun1_dict = dict(map(lambda x, y: [x, y], nouns_set, nouns_sets))
    source_count_sort1 = sorted(noun1_dict.items(), key=lambda d: d[1], reverse=True)

    # print("名词：")
    # for word in source_count_sort1:
    #     print(word)

    nrs_set = list(set(nrs))  # ******需要注释
    nrs_sets = [0] * len(nrs_set)

    for word in nouns:
        if word in nrs_set:
            nrs_sets[nrs_set.index(word)] += 1

    nr1_dict = dict(map(lambda x, y: [x, y], nrs_set, nrs_sets))
    source_count_sort1 = sorted(nr1_dict.items(), key=lambda d: d[1], reverse=True)

    # print("人名：")    #人名
    # for word in source_count_sort1:
    #     print(word)

    verbs2 = []
    with io.open('./for_fx4.txt', "r", encoding='utf-8') as f:
        while True:
            line = f.readline()
            if len(line.strip()) > 0:
                json_data = json.loads(line)
                p_seg = json_data['p_seg']
                for i in range(len(p_seg)):
                    if p_seg[i]['word'] in nrs_set:
                       for j in range(i+1,len(p_seg)):
                           if p_seg[j]['nature'] == 'v':
                               verbs2.append(p_seg[j]['word'])
                               break

            else:
                break

    verbs2_sets = list(set(verbs2))
    # for word in verbs2_sets:
    #     print(word)

    with io.open('./for_fx4.txt', "r", encoding='utf-8') as f:
        while True:
            line = f.readline()
            if len(line.strip()) > 0:
                json_data = json.loads(line)
                p_seg = json_data['p_seg']
                for i in range(len(p_seg)):
                    if p_seg[i]['word'] in verbs2_sets:
                        j = i
                        while True:
                            j = j - 1
                            if p_seg[j]['nature'].startswith('n') and not p_seg[j]['nature'].startswith('nr') and not p_seg[j]['nature'] is 'n':
                                orgs.append(p_seg[j]['word'])
                                break
                            elif j <= 0:
                                break

            else:
                break

    orgs_set = list(set(orgs))
    orgs_sets = [0] * len(orgs_set)  # 根据去重后的动词数量设置一个单位矩阵

    for word in orgs:
        if word in orgs_set:  # 如果该词语在动词列表里，就让另外一个单位矩阵对应的位置加一
            orgs_sets[orgs_set.index(word)] += 1

    verb1_dict = dict(map(lambda x, y: [x, y], orgs_set, orgs_sets))
    source_count_sort1 = sorted(verb1_dict.items(), key=lambda d: d[1], reverse=True)  # 制作字典并且作排序

    for word in source_count_sort1:
        print(word)
