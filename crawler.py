#-*- coding-8 -*-
import requests
import lxml
import sys
from bs4 import BeautifulSoup
import xlwt
import time
import urllib
import re
import json
import cookies as ck
import random
import copy
import os

INPUT_FILE='org_names.json'
OUTPUT_FILE='org_product_datas.json'
def DelHtml(htmlString):
    pre = re.compile('<[^>]+>')
    s1 = pre.sub(" ", htmlString)
    return s1

def getPerName(text):
    pre=re.search('(.*)他有',text)
    return pre.group(1)

# def ProcessBackGroundDataGroup(tag):
#     #背景信息爬
#     com_detail_info={}
#     basic_info_table = tag.select('.data-content .table')[0].tbody.contents
#     # # 评分部分
#     # score_html = basic_info_table[0].contents[4].contents[0].contents
#     # if len(score_html) < 3:
#     #     score = score_html[1].string
#     # else:
#     #     score = score_html[1].string + score_html[2].string
#     # com_detail_info['score'] = score
#     for col in basic_info_table:
#         infolist = col.contents
#         for i in range(len(infolist) // 2):
#             key = infolist[i * 2].string
#             if key is None:
#                 key = infolist[i * 2].text
#             value = infolist[i * 2 + 1].string
#             if value is None:
#                 value = infolist[i * 2 + 1].text
#             com_detail_info[key] = value
#     return com_detail_info

def ProcessProduct(tag):
    #供应商、竞品、业务信息、产品、客户爬
    com_product_info = []
    headers=[]
    intro_headers = tag.select('.data-content thead')[0].select('th')
    for h in intro_headers:
        head=h.string
        if head is None:
            head=h.text
        headers.append(head)
    intro_tables = tag.select('.data-content tbody')
    if len(intro_tables) > 1:
        intro_table = intro_tables[-1]
    else:
        intro_table = intro_tables[0]
    for col in intro_table:
        product={}
        for i,h in enumerate(headers):
            product[h]=col.contents[i].text
        com_product_info.append(product)
    return com_product_info

def ProcessMainMemberDataGroup(tag):
    #主要人员爬
    com_relative_per={}
    per_table = tag.select('.clearfix .table')[0].tbody.contents
    for col in per_table:
        per_name = getPerName(col.contents[1].text[1:])
        per_pos = col.contents[2].text
        com_relative_per[per_name] = per_pos
    return com_relative_per

def ProcessIntroDataGroup(tag):
    #公司简介爬
    com_detail_info={}
    intro_tables = tag.select('.data-content tbody')
    if len(intro_tables)>1:
        intro_table=intro_tables[-1]
    else:
        intro_table=intro_tables[0]
    for col in intro_table:
        infolist = col.contents
        for i in range(len(infolist) // 2):
            key = infolist[i * 2].string
            if key is None:
                key = infolist[i * 2].text
            value = infolist[i * 2 + 1].string
            if value is None:
                value = infolist[i * 2 + 1].text
            com_detail_info[key] = value
    return com_detail_info

def ProcessAdminiStratorDataGroup(tag):
    #管理成员爬
    com_relative_per={}
    admin_table = tag.select('.data-content .table')[0].tbody.contents
    for col in admin_table:
        per_name = col.contents[1].text[1:]
        per_pos = col.contents[3].text
        com_relative_per[per_name] = per_pos
    return com_relative_per

def HttpResponse(url):
    User_Agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0'
    cookie=random.choice(ck.cookies)
    headers = {
        'Host': 'www.tianyancha.com',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        'Referer': 'https: // www.tianyancha.com/search?key=%E5%80%A2%E5%86%A0%E6%8E%A7%E8%82%A1%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        #在此填上自己登陆后搜索使用的cookie
        'Cookie': cookie
    }
    try:
        response = requests.get(url,headers = headers)
        if response.status_code != 200:
            response.encoding = 'utf-8'
            print(response.status_code)
            print('ERROR')
        soup = BeautifulSoup(response.text,'lxml')
        return soup
    except Exception:
        print('请求都不让，这天眼查也搞事情吗？？？')
        return None

def getComByName(com_name):
    try:
        url = 'https://www.tianyancha.com/search?key='+com_name
        soup=HttpResponse(url)
        com_detail_info={}
        com_relative_per={}
        if soup is None:
            return com_detail_info,com_relative_per,-1
        com_all_info = soup.body.select('.mt74 .container.-top .container-left .search-block.header-block-container')[0]
        search_results= com_all_info.select('.search-item.sv-search-company')
        if len(search_results)==0:
            print('未找到相关公司信息')
            return com_detail_info,com_relative_per,-2
        else:
            com_info=search_results[0]
        #公司详情页面跳转
        info_href = com_info.select('.content .header')[0].a['href']
        soup=HttpResponse(info_href)
        infoblocks=soup.body.select('.mt74 .container.-top .company-warp.-public .detail-list')[0].select(
            '.block-data')
        com_guests_info=[]
        com_services_info=[]
        com_producers_info=[]
        com_opponents_info=[]
        com_product_info=[]
        for datagroup in infoblocks:
            if 'tyc-event-ch' in datagroup.attrs:
                #有些公司会在信息块名后加上hk,或是其他后缀
                # if 'CompangyDetail.gongshangxinxin' in datagroup['tyc-event-ch'] \
                #     or 'CompangyDetail.qiyejianjie' in datagroup['tyc-event-ch'] \
                #     or 'CompangyDetail.lianxixinxin' in datagroup['tyc-event-ch']:
                #     com_detail_info=dict(com_detail_info,**ProcessIntroDataGroup(datagroup))
                # elif datagroup['tyc-event-ch'] in ('CompangyDetail.dongshihuichengyuanhk','CompangyDetail.jianshihuichengyuanhk','CompangyDetail.guanlichengyuanhk'):
                #     com_relative_per=dict(com_relative_per,**ProcessAdminiStratorDataGroup(datagroup))
                # elif datagroup['tyc-event-ch'] == 'CompangyDetail.zhuyaorenyuan':
                #     com_relative_per=dict(com_relative_per,**ProcessMainMemberDataGroup(datagroup))
                # if 'CompangyDetail.qiyeyewu' in datagroup['tyc-event-ch']:
                #     com_services_info+=ProcessProduct(datagroup)
                # elif 'CompangyDetail.jingpinxinxi' in datagroup['tyc-event-ch']:
                #     com_opponents_info+=ProcessProduct(datagroup)
                # elif 'CompangyDetail.gongyingshang' in datagroup['tyc-event-ch']:
                #     com_producers_info+=ProcessProduct(datagroup)
                # elif 'CompangyDetail.gongyingshang' in datagroup['tyc-event-ch']:
                #     com_guests_info+=ProcessProduct(datagroup)
                if 'CompangyDetail.chanpin' in datagroup['tyc-event-ch']:
                    com_product_info+=ProcessProduct(datagroup)

        com_detail_info['guests']=com_guests_info
        com_detail_info['producers']=com_producers_info
        com_detail_info['opponents']=com_opponents_info
        com_detail_info['services']=com_services_info
        com_detail_info['products']=com_product_info
        # process_dict = {}
        # for key in com_detail_info.keys():
        #     if "统一社会信用代码" in key:
        #         process_dict['统一社会信用代码'] = com_detail_info[key]
        #     elif "纳税人识别号" in key:
        #         process_dict['纳税人识别号'] = com_detail_info[key]
        #     elif "组织机构代码" in key:
        #         process_dict['组织机构代码'] = com_detail_info[key]
        # com_detail_info=dict(com_detail_info,**process_dict)
        return com_detail_info,com_relative_per,0
    except Exception:
        print('error')
        return com_detail_info,com_relative_per,-1

# def reviseData():
#
#     with open('','r',encoding='utf-8') as f:
#         compnames=json.load(f)
#
#     with open('PropertyMap.json','r',encoding='utf-8') as f:
#         propertymap=json.load(f)
#     with open(INPUT_FILE,'r',encoding='utf-8') as f:
#         orgdatas=json.load(f)
#         print()
#     comdatas = orgdatas['datas']
#     datas_revised=[]
#     for i in range(len(comdatas)):
#         data=comdatas[i]
#         r_data=copy.deepcopy(data)
#         r_data['original_id']=compnames[i]
#         r_data['property']['Domicile']=r_data['domicile']
#         for key in r_data['property'].keys():
#             if r_data[key]=='-':
#                 r_data[key]='--'
#     orgdatas['datas'] = datas_revised
#     with open(OUPUT_FILE, 'w', encoding='utf-8') as f:
#         json.dump(orgdatas, f, ensure_ascii=False)



if __name__ == '__main__':
    #需要爬取的公司名
    with open(INPUT_FILE,'r',encoding='utf-8') as f:
        compnames=json.load(f)

    # with open('PropertyMap.json','r',encoding='utf-8') as f:
    #     propertymap=json.load(f)
    #读取已完成爬取数据
    if not os.path.exists(OUTPUT_FILE):
        orgdatas={"datas":[]}
    else:
        with open(OUTPUT_FILE,'r',encoding='utf-8') as f:
            orgdatas=json.load(f)
    # promap={}
    # for item in propertymap.items():
    #     for value in item[1]:
    #         promap[value]=item[0]
    # comdatas=orgdatas_new['datas']
    comdatas=orgdatas['datas']
    comdatas_json={}
    #从上次中断的地方继续爬
    for name in compnames[len(comdatas):]:
        print(name)
        comdata={}
        comdata['label']='Organization'
        comdata['original_id'] = name
        com_detail_info,com_relative_per,tag = getComByName(name)
        if tag==-1:
            break
        comdata['produce_info']=com_detail_info
        comdatas.append(comdata)

        # for key in com_detail_info.keys():
        #     if key in promap.keys():
        #         comproperty[promap[key]]=com_detail_info[key]
    # for comdata in comdatas:
    #     for key in propertymap:
    #         property=comdata['property']
    #         if key not in property:
    #                 property[key]="--"
    comdatas_json['datas']=comdatas
    with open(OUTPUT_FILE,'w',encoding='utf-8') as f:
        json.dump(comdatas_json, f,ensure_ascii=False)
    print("爬取完成")