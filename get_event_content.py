import io
import json
import re
import requests

def abstract_rule_2(p_seg):
    segs = [x['word'] for x in p_seg]
    p = ''.join(segs)
    if len(p) > 40 and len(p) < 500:
        # key_words = ['日','当日','今日','昨日','日前','近日','日电']
        key_words = ['日','日电']
        for word in key_words:
            if word in segs:
                if '摄' not in segs:
                    return 1
    return 0

def abstract_rule_3(p_seg):
    judgement = 0
    segs = [x['word'] for x in p_seg]
    p = ''.join(segs)
    if len(p) > 40 and len(p) < 500:
        key_words = ['日','日电']
        for seg in segs:
            if seg in key_words:
                if '摄' not in segs:
                    judgement += 1
    return judgement

def abstract_rule_1(p_seg):
    segs = [x['word'] for x in p_seg]
    p = ''.join(segs)
    if len(p) > 40 and len(p) < 500:
        key_words = ['日','当日','今日','昨日','日前','近日','日电']
        for word in key_words:
            if word in segs:
                if '摄' not in segs:
                    return 1
    return 0


# def abstract_rule(p):
#     if len(p) > 40 and len(p) < 500:
#         if '月' in p and '日' in p:
#             if '摄' not in p:
#                 return 1
#         if '昨日' in p or '今日' in p:
#             return 1
#         if '近日' in p:
#             return 1
#         if '日' in p:
#             return 1
#     return 0


def removeAllTag(s):
    s = re.sub('<[^>]+>', '', s)
    return s

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

    x = []
    x1 = []
    c = 0
    c1 = 0
    c2 = 0
    c3 = 0
    c4 = 0
    with io.open('./for_fx7.txt', "r", encoding='utf-8') as f:
        while True:
            line = f.readline()
            if len(line.strip()) > 0:
                json_data = json.loads(line)
                title = json_data['title']
                publishAt = json_data['publishAt']
                c +=1
                content = json_data['content']
                content_seg = json_data['seg_content']      #只是一篇资讯的分词
                url = json_data['url']
                title_seg = json_data['seg_title']
                if json_data["dataSource"] == "CRAWL":
                    content = content.split('</p><p>')
                else:
                    content = content.split('</p></p><p><p>')

                # con = 0
                # con_t = ''
                # con1 = 0
                # con_t1 = ''
                # for i in range(0, len(content)):
                #     p = removeAllTag(content[i])
                #     if i < 6:
                #         p_seg = split_sentence(p)
                #         if abstract_rule_1(p_seg) == 1:
                #             #if '税务' in p:
                #             # print(p)
                #             #print('============================')
                #             x.append({'p':p,
                #                      'p_seg':p_seg,
                #                      'title':title,
                #                       'title_seg':title_seg,
                #                       'url':url})
                #             c1 += 1
                #             con += 1
                #             con_t = p
                #             break

                for i in range(0, len(content)):
                    p = removeAllTag(content[i])
                    if i < 6:
                        p_seg = split_sentence(p)
                        # if abstract_rule_2(p_seg) == 1:
                        if abstract_rule_2(p_seg) == 1:
                            #if '税务' in p:
                            print(p)
                            print('============================')
                            x.append({'p':p,
                                     'p_seg':p_seg,
                                     'title':title,
                                       'title_seg':title_seg,
                                      'publishAt':publishAt,
                                      'url':url})
                            c2 += 1
                            # con1 += 1
                            # con_t1 = p
                            break

                # if con_t == con_t1:
                #     continue
                # if con == 0 and con1 != 0:
                #     print('con_t1  ',con_t1)
                #     c3 += 1
                # if con == 1 and con1 == 0:
                #     print('con_t   ',con_t)
                #     c4 += 1
                # if con == 1 and con1 == 1:
                #     print('con_t1 vs con_t  ', con_t1)
                #     print('con_t vs con_t1  ', con_t)




            else:
                break

    # for item in x:
    #     with io.open('./datetime_data3.txt', "a", encoding='utf-8') as f:
    #         f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(c)
    # print(c1)
    print(c2)
    # print(c3)
    # print(c4)

    # print("第二个：")
    # with io.open('./for_fx5.txt', "r", encoding='utf-8') as f:
    #     while True:
    #         line = f.readline()
    #         if len(line) > 0:
    #             json_data = json.loads(line)
    #             title = json_data['title']
    #             c2 += 1
    #             content = json_data['content']
    #             content_seg = json_data['seg_content']
    #
    #             url = json_data['url']
    #
    #             if json_data["dataSource"] == "CRAWL":
    #                 content = content.split('</p><p>')
    #             else:
    #                 content = content.split('</p></p><p><p>')
    #
    #             for i in range(0, len(content)):
    #                 p = removeAllTag(content[i])
    #                 condition = 0
    #                 if i < 6:
    #                     if abstract_rule(p) == 1:
    #                         # if '税务' in p:
    #                         #print(p)
    #                         #print('============================')
    #
    #                         c3 += 1
    #                         condition += 1
    #                         break
    #
    #                 if condition ==0:
    #                     c4 += 1
    #                     if c4 % 20 == 1:
    #                         print(content)
    #                         print(url)
    #                     break


            # else:
            #     break





    # print(c2)
    # print(c3)
    # print(c4)



