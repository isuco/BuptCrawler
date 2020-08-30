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

def DelHtml(htmlString):
    pre = re.compile('<[^>]+>')
    s1 = pre.sub(" ", htmlString)
    return s1

def getPerName(text):
    pre=re.search('(.*)他有',text)
    return pre.group(1)

def ProcessBackGroundDataGroup(tag):
    #背景信息爬
    com_detail_info={}
    basic_info_table = tag.select('.data-content .table.-striped-col.-border-top-none.-breakall')[
        0].tbody.contents
    # 评分部分
    score_html = basic_info_table[0].contents[4].contents[0].contents
    if len(score_html) < 3:
        score = score_html[1].string
    else:
        score = score_html[1].string + score_html[2].string
    com_detail_info['score'] = score
    for col in basic_info_table:
        infolist = col.contents
        for i in range(len(infolist) // 2):
            key = infolist[i * 2].string
            if key is None:
                key = infolist[i * 2].text
                if "统一社会信用代码" in key:
                    key="统一社会信用代码"
                elif "纳税人识别号" in key:
                    key="纳税人识别号"
                elif "组织机构代码" in key:
                    key="组织机构代码"
            value = infolist[i * 2 + 1].string
            if value is None:
                value = infolist[i * 2 + 1].text
            com_detail_info[key] = value
    return com_detail_info

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
    intro_table = tag.select('.data-content .table.-striped-col')[0].tbody.contents
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
            return com_detail_info,com_relative_per
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
        infoblocks=soup.body.select('.mt74 .container.-top .company-warp.-public .detail-list .block-data-group')[0].select(
            '.block-data')
        for datagroup in infoblocks[1:]:
            if 'tyc-event-ch' in datagroup.attrs:
                if datagroup['tyc-event-ch'] == 'CompangyDetail.gongshangxinxin':
                    com_detail_info=dict(com_detail_info,**ProcessBackGroundDataGroup(datagroup))
                elif datagroup['tyc-event-ch'] == 'CompangyDetail.qiyejianjiehk':
                    com_detail_info=dict(com_detail_info,**ProcessIntroDataGroup(datagroup))
                # elif datagroup['tyc-event-ch'] in ('CompangyDetail.dongshihuichengyuanhk','CompangyDetail.jianshihuichengyuanhk','CompangyDetail.guanlichengyuanhk'):
                #     com_relative_per=dict(com_relative_per,**ProcessAdminiStratorDataGroup(datagroup))
                # elif datagroup['tyc-event-ch'] == 'CompangyDetail.zhuyaorenyuan':
                #     com_relative_per=dict(com_relative_per,**ProcessMainMemberDataGroup(datagroup))
        return com_detail_info,com_relative_per,0
    except Exception:
        print('error')
        return com_detail_info,com_relative_per,-1

def reviseData(datas,compnames,propertyMap):
    datas_revised=[]
    for i in range(len(datas)):
        data=datas[i]
        r_data=copy.deepcopy(data)
        r_data['original_id']=compnames[i]
        r_data['property']['Domcile']


if __name__ == '__main__':
    with open('org_names.json','r',encoding='utf-8') as f:
        compnames=json.load(f)

    with open('PropertyMap.json','r',encoding='utf-8') as f:
        propertymap=json.load(f)
    #已完成爬取数据
    with open('org_datas.json','r',encoding='utf-8') as f:
        orgdatas=json.load(f)
        print()

    promap={}
    for item in propertymap.items():
        for value in item[1]:
            promap[value]=item[0]
    comdatas=orgdatas['datas']
    # comdatas_json={}
    # for name in compnames[len(comdatas):]:
    #     print(name)
    #     comdata,comproperty={},{}
    #     comdata['label']='Organization'
    #     com_detail_info,com_relative_per,tag = getComByName(name)
    #     if tag==-1:
    #         break
    #     for key in com_detail_info.keys():
    #         if key in promap.keys():
    #             comproperty[promap[key]]=com_detail_info[key]
    #     comdata['property']=comproperty
    #     comdatas.append(comdata)
    # for comdata in comdatas:
    #     for key in propertymap:
    #         property=comdata['property']
    #         if key not in property:
    #                 property[key]="--"
    # comdatas_json['datas']=comdatas
    # orgdatas['datas']=comdatas
    with open('org_datas.json','w',encoding='utf-8') as f:
        json.dump(orgdatas, f,ensure_ascii=False)
    # print("爬取完成")