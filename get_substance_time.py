import io
import json
import re
import requests
import time
import datetime

def abstract_rule_2(p_seg):
    judgement = 0

    segs = [x['word'] for x in p_seg]
    natures = [x['nature'] for x in p_seg]
    p = ''.join(segs)
    if len(p) > 40 and len(p) < 500:
        # key_words = ['日','当日','今日','昨日','日前','近日','日电']
        key_words = ['日','日电']
        if '摄' not in segs:
            for i in range(0,len(segs)):
                if segs[i] in key_words:
                    if natures[i-1] == 'm':
                        judgement += 1
    return judgement

def abstract_rule_5(p_seg):
    judgement = 0
    date_times_1 = []
    date_times_2 = []
    condition_1 = 0
    condition_spread = 0
    condition_fact = 0
    flag = 0

    segs = [x['word'] for x in p_seg]
    natures = [x['nature'] for x in p_seg]
    p = ''.join(segs)
    if len(p) > 40 and len(p) < 500:
        key_words = ['当日','今日','昨日','日前','近日']
        # key_words = ['日','日电']
        if '摄' not in segs:
            for word in key_words:
                if word in segs:
                    flag = segs.index(word)                #获取一个转述性概述中第一个含有‘近日’等关键词的位置下标
                    condition_1 += 1
                    break

            if condition_1 > 0:
                for i in range(0,len(segs)):
                    if segs[i] == '日电':
                        if natures[i-1] == 'm':
                            if judgement == 0:              #如果有‘近日’等关键词且概述中出现了‘日电’，将‘日电’的日期作为event_spread_time
                                judgement += 1
                                if natures[i - 2] != 't':
                                    date_times_1.append(segs[i-1]+segs[i])
                                    condition_spread = 0
                                elif natures[i - 2] == 't':
                                    date_times_1.append(segs[i - 2] + segs[i - 1] + segs[i])
                                    condition_spread = 1
                            elif judgement > 0:             #如果有‘近日’等关键词且概述中出现了多个‘日电’或‘日电’在‘今日’关键词后或‘日’之后，将第二个‘日电’作为event_spread_time，
                                judgement += 1
                                if natures[i - 2] != 't':
                                    date_times_1 = [segs[i-1]+segs[i]]
                                    condition_spread = 0
                                elif natures[i - 2] == 't':
                                    date_times_1 =[segs[i - 2] + segs[i - 1] + segs[i]]
                                    condition_spread = 1


                    if segs[i] == '日':
                        if natures[i-1] == 'm':

                            if flag < i:
                                if judgement == 0:          #如果有‘近日’等关键词在该日期前并且该日期前面没有‘日’或‘日电’，认为‘近日’是event_spread_time，该时间是evnet_fact_time
                                    judgement += 1
                                    if natures[i - 2] != 't':
                                        date_times_2.append(segs[i-1]+segs[i])
                                        condition_fact = 0
                                    elif natures[i - 2] == 't':
                                        date_times_2.append(segs[i - 2] + segs[i - 1] + segs[i])
                                        condition_fact = 1
                                elif judgement == 1:         #如果有‘近日’等关键词在该日期前并且该日期前面有一个‘日’或‘日电’，认为‘近日’是event_fact_time，该时间也是event_fact_time
                                    judgement += 1
                                    if natures[i - 2] != 't':
                                        date_times_2.append(segs[i-1]+segs[i])
                                        condition_fact = 0
                                    elif natures[i - 2] == 't':
                                        date_times_2.append(segs[i - 2] + segs[i - 1] + segs[i])
                                        condition_fact = 1
                                elif judgement > 1:         #如果有‘近日’等关键词在该日期前并且该日期前面有多个‘日’或‘日电’，时间点过多，置空event_fact_time列表
                                    judgement += 1
                                    date_times_2 = []
                                    condition_fact = 0

                            if flag > i:
                                if judgement == 0:           #如果有‘近日’等关键词且在该日期之后，并且该日期前没有‘日’或‘日电’，认为该日期为event_spread_time
                                    judgement += 1
                                    if natures[i - 2] != 't':
                                        date_times_1.append(segs[i - 1] + segs[i])
                                        condition_spread = 0
                                    elif natures[i - 2] == 't':
                                        date_times_1.append(segs[i - 2] + segs[i - 1] + segs[i])
                                        condition_spread = 1
                                elif judgement == 1:         #如果有‘近日’等关键词且在该日期之后，并且该日期前有一个‘日’或‘日电’，认为该日期为event_fact_time
                                    judgement += 1
                                    if natures[i - 2] != 't':
                                        date_times_2.append(segs[i-1]+segs[i])
                                        condition_fact = 0
                                    elif natures[i - 2] == 't':
                                        date_times_2.append(segs[i - 2] + segs[i - 1] + segs[i])
                                        condition_fact = 1
                                elif judgement > 1:          #如果有‘近日’等关键词且在该日期之后，并且该日期前有多个‘日’或‘日电’，时间点过多，置空event_fact_time
                                    judgement += 1
                                    date_times_2 = []
                                    condition_fact = 0

            if condition_1 == 0:
                for i in range(0,len(segs)):
                    if segs[i] == '日电':
                        if natures[i-1] == 'm':
                            if judgement == 0:                   #极端情况：如果一则概述有两个‘日电’，把第二个日电作为发布时间
                                judgement += 1
                                if natures[i - 2] != 't':
                                    date_times_1.append(segs[i-1]+segs[i])
                                    condition_spread = 0
                                elif natures[i - 2] == 't':
                                    date_times_1.append(segs[i - 2] + segs[i - 1] + segs[i])
                                    condition_spread = 1
                            if judgement > 0:                       #如果‘日电’前出现了一个‘日’，把前一个‘日‘舍掉，将日电改为event_spread_time
                                judgement += 1
                                if natures[i - 2] != 't':
                                    date_times_1 = [segs[i-1]+segs[i]]
                                    condition_spread = 0
                                elif natures[i - 2] == 't':
                                    date_times_1 =[segs[i - 2] + segs[i - 1] + segs[i]]
                                    condition_spread = 1

                    if segs[i] == '日':
                        if natures[i - 1] == 'm':
                            if judgement == 0:              #如果概述中不含‘日电’，将最先出现的时间作为发布时间
                                judgement += 1
                                if natures[i - 2] != 't':
                                    date_times_1.append(segs[i-1]+segs[i])
                                    condition_spread = 0
                                elif natures[i - 2] == 't':
                                    date_times_1.append(segs[i - 2] + segs[i - 1] + segs[i])
                                    condition_spread = 1
                            elif judgement == 1:
                                judgement += 1
                                if natures[i - 2] != 't':
                                    date_times_2.append(segs[i - 1] + segs[i])
                                    condition_fact = 0
                                elif natures[i - 2] == 't':
                                    date_times_2.append(segs[i - 2] + segs[i - 1] + segs[i])
                                    condition_fact = 1
                            elif judgement > 1:           #如果一则概述中有两个以上包含‘日’或‘日电’时，不能确定哪一个时间为event_fact_time，因此置空列表
                                judgement += 1
                                date_times_2 = []
                                condition_fact = 1

    return judgement,date_times_1,date_times_2,condition_spread,condition_fact


def abstract_rule_4(p_seg):
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

def time_constitute(publishAt,daily_str):
    daily_str_segs = split_sentence(daily_str)
    daily_str_seg = [x['word'] for x in daily_str_segs]
    daily_int = daily_str_seg[1]
    if (daily_int.isdigit()) == False:
        return 0
    if int(daily_int) > 31:
        return 0
    else:
        ltime_1 = time.localtime((publishAt)/1000)
        timeStr_1 = time.strftime("%Y-%m-%d", ltime_1)
        tmp_date_list = timeStr_1.split('-')
        dateC = datetime.datetime(int(tmp_date_list[0]), int(tmp_date_list[1]), int(daily_int))
        timestamp = time.mktime(dateC.timetuple())
        ltime_2 = time.localtime(timestamp)
        timeStr_2 = time.strftime("%Y-%m-%d", ltime_2)
        print(timeStr_2)



def removeAllTag(s):
    s = re.sub('<[^>]+>', '', s)
    return s

def remove_lists(lists):
    illegal_char = [' ','[',']']
    tmp_list = []
    for i in illegal_char:
        for j in lists:
            val = re.sub(i,'',j)
            tmp_list.append(val)
        lists = []
        lists = tmp_list
        tmp_list = []
    return lists

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

def loop_output(lists):
    for element in lists:
        print(str(element))


if __name__ == '__main__':

    x = []
    x1 = []
    c = 0
    c1 = 0
    c2 = 0
    c3 = 0
    c4 = 0
    c5 = 0
    with io.open('./for_fx7.txt', "r", encoding='utf-8') as f:
        while True:
            line = f.readline()
            if len(line.strip()) > 0:
                json_data = json.loads(line)
                title = json_data['title']
                c +=1
                content = json_data['content']
                content_seg = json_data['seg_content']      #只是一篇资讯的分词
                url = json_data['url']
                publishAt = json_data['publishAt']
                title_seg = split_sentence(title)
                if json_data["dataSource"] == "CRAWL":
                    content = content.split('</p><p>')
                else:
                    content = content.split('</p></p><p><p>')

                con = 0
                con_t = ''
                con1 = 0
                con_t1 = ''
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
                        judgement,date_times_1,date_times_2,condition_spread,condition_fact = abstract_rule_5(p_seg)
                        if judgement > 0:
                            c1 += 1
                            #if '税务' in p:
                            print(p)
                            print("event_spread_time日期为：")
                            if condition_spread == 1:               #前面有月份
                                print(date_times_1)
                            elif condition_spread == 0:
                                if date_times_1 != []:
                                    time_constitute(publishAt,date_times_1)

                            print("event_fact_time日期为：")
                            # print(date_times_2)
                            if condition_fact == 1:
                                print(date_times_2)
                            elif condition_fact == 0:
                                if date_times_2 != []:
                                    time_constitute(publishAt, date_times_2)

                            print('============================')
                            x.append({'p':p,
                                     'p_seg':p_seg,
                                     'title':title,
                                       'title_seg':title_seg,
                                      'url':url})
                            if date_times_1 != []:
                                c4 += 1
                            if date_times_2 != []:
                                c5 += 1
                            if judgement == 1:
                                c2 += 1
                            elif judgement ==2:
                                c3 += 1
                            # con += 1
                            # con_t = p
                            break




                # for i in range(0, len(content)):
                #     p = removeAllTag(content[i])
                #     if i < 6:
                #         p_seg = split_sentence(p)
                #         # if abstract_rule_2(p_seg) == 1:
                #         if abstract_rule_4(p_seg) == 1:
                #             #if '税务' in p:
                #             #print(p)
                #             #print('============================')
                #             x.append({'p':p,
                #                      'p_seg':p_seg,
                #                      'title':title,
                #                        'title_seg':title_seg,
                #                       'url':url})
                #             c2 += 1
                #             con1 += 1
                #             con_t1 = p
                #             break

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
    print(c1)
    print(c2)
    print(c3)
    print(c4)
    print(c5)

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



