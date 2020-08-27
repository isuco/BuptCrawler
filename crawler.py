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

def DelHtml(htmlString):
    pre = re.compile('<[^>]+>')
    s1 = pre.sub(" ", htmlString)
    return s1

def getPerName(text):
    pre=re.search('(.*)他有',text)
    return pre.group(1)

def ProcessBackGroundDataGroup(tag):
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
            value = infolist[i * 2 + 1].string
            if value is None:
                value = infolist[i * 2 + 1].text
            com_detail_info[key] = value
    return com_detail_info

def ProcessMainMemberDataGroup(tag):
    com_relative_per={}
    per_table = tag.select('.clearfix .table')[0].tbody.contents
    for col in per_table:
        per_name = getPerName(col.contents[1].text[1:])
        per_pos = col.contents[2].text
        com_relative_per[per_name] = per_pos
    return com_relative_per

def ProcessIntroDataGroup(tag):
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
    com_relative_per={}
    admin_table = tag.select('.data-content .table')[0].tbody.contents
    for col in admin_table:
        per_name = col.contents[1].text[1:]
        per_pos = col.contents[3].text
        com_relative_per[per_name] = per_pos
    return com_relative_per

def HttpResponse(url):
    User_Agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0'
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
        'Cookie': 'aliyungf_tc=AQAAAFV/bHMKPwcAQg5we9r40B5mUXJn; csrfToken=K5LiMrF4Z2X0remAkEKy1dqB; jsid=SEM-BAIDU-PZ0824-SY-000001; TYCID=6e494c00e78711ea97e07f267e553642; ssuid=7596876568; _ga=GA1.2.871234549.1598437947; _gid=GA1.2.768205796.1598437947; RTYCID=66d0f47c78b5488180e870a4ef0e985c; CT_TYCID=ce9bcb6846904207ac93ce4795d556fd; nice_id658cce70-d9dc-11e9-96c6-833900356dc6=06829402-e78c-11ea-bdc1-69c81e8afa48; bad_id658cce70-d9dc-11e9-96c6-833900356dc6=06829401-e78c-11ea-bdc1-69c81e8afa48; bannerFlag=true; cloud_token=3c0ca3085c1b486e8f95edb112bc1398; Hm_lvt_e92c8d65d92d534b0fc290df538b4758=1598437946,1598437991,1598522499; tyc-user-info=%257B%2522claimEditPoint%2522%253A%25220%2522%252C%2522vipToMonth%2522%253A%2522false%2522%252C%2522explainPoint%2522%253A%25220%2522%252C%2522personalClaimType%2522%253A%2522none%2522%252C%2522integrity%2522%253A%252210%2525%2522%252C%2522state%2522%253A%25220%2522%252C%2522score%2522%253A%25220%2522%252C%2522announcementPoint%2522%253A%25220%2522%252C%2522bidSubscribe%2522%253A%2522-1%2522%252C%2522vipManager%2522%253A%25220%2522%252C%2522onum%2522%253A%25220%2522%252C%2522monitorUnreadCount%2522%253A%25220%2522%252C%2522discussCommendCount%2522%253A%25220%2522%252C%2522showPost%2522%253Anull%252C%2522claimPoint%2522%253A%25220%2522%252C%2522token%2522%253A%2522eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIxNTAwMTA5MTI5OCIsImlhdCI6MTU5ODUyMjU1NSwiZXhwIjoxNjMwMDU4NTU1fQ.lWYyEjDKV-Ad-bfKhOt4hF_njvKG4RG-DHLiShXdP8SmnICrHOJKE8KRR4954rvr2zJSag1Mg8vMU5lV89J2WA%2522%252C%2522schoolAuthStatus%2522%253A%25222%2522%252C%2522scoreUnit%2522%253A%2522%2522%252C%2522redPoint%2522%253A%25220%2522%252C%2522myTidings%2522%253A%25220%2522%252C%2522companyAuthStatus%2522%253A%25222%2522%252C%2522myAnswerCount%2522%253A%25220%2522%252C%2522myQuestionCount%2522%253A%25220%2522%252C%2522signUp%2522%253A%25221%2522%252C%2522privateMessagePointWeb%2522%253A%25220%2522%252C%2522nickname%2522%253A%2522%25E9%2592%259F%25E7%2581%25B5%2522%252C%2522privateMessagePoint%2522%253A%25220%2522%252C%2522bossStatus%2522%253A%25222%2522%252C%2522isClaim%2522%253A%25220%2522%252C%2522yellowDiamondEndTime%2522%253A%25220%2522%252C%2522new%2522%253A%25221%2522%252C%2522yellowDiamondStatus%2522%253A%2522-1%2522%252C%2522pleaseAnswerCount%2522%253A%25220%2522%252C%2522vnum%2522%253A%25220%2522%252C%2522bizCardUnread%2522%253A%25220%2522%252C%2522mobile%2522%253A%252215001091298%2522%257D; auth_token=eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIxNTAwMTA5MTI5OCIsImlhdCI6MTU5ODUyMjU1NSwiZXhwIjoxNjMwMDU4NTU1fQ.lWYyEjDKV-Ad-bfKhOt4hF_njvKG4RG-DHLiShXdP8SmnICrHOJKE8KRR4954rvr2zJSag1Mg8vMU5lV89J2WA; tyc-user-phone=%255B%252215001091298%2522%255D; token=154f6daa6f7346b6ba87f6483b364d0c; _utm=419be1deeeb345b986f8abe506c9c16b; Hm_lpvt_e92c8d65d92d534b0fc290df538b4758=1598522563'            }
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
            return com_detail_info,com_relative_per
        else:
            com_info=search_results[0]
        #公司详情页面跳转
        info_href = com_info.select('.content .header')[0].a['href']
        soup=HttpResponse(info_href)
        #基本信息爬
        infoblocks=soup.body.select('.mt74 .container.-top .company-warp.-public .detail-list .block-data-group')[0].select(
            '.block-data')
        for datagroup in infoblocks[1:]:
            if 'tyc-event-ch' in datagroup.attrs:
                if datagroup['tyc-event-ch'] == 'CompangyDetail.gongshangxinxin':
                    com_detail_info=dict(com_detail_info,**ProcessBackGroundDataGroup(datagroup))
                elif datagroup['tyc-event-ch'] == 'CompangyDetail.qiyejianjiehk':
                    com_detail_info=dict(com_detail_info,**ProcessIntroDataGroup(datagroup))
                elif datagroup['tyc-event-ch'] in ('CompangyDetail.dongshihuichengyuanhk','CompangyDetail.jianshihuichengyuanhk','CompangyDetail.guanlichengyuanhk'):
                    com_relative_per=dict(com_relative_per,**ProcessAdminiStratorDataGroup(datagroup))
                elif datagroup['tyc-event-ch'] == 'CompangyDetail.zhuyaorenyuan':
                    com_relative_per=dict(com_relative_per,**ProcessMainMemberDataGroup(datagroup))
        return com_detail_info,com_relative_per
    except Exception:
        print('error')
        return com_detail_info,com_relative_per


if __name__ == '__main__':
    with open('org_names.json','r',encoding='utf-8') as f:
        compnames=json.load(f)
    comdata={}
    for name in compnames:
        print(name)
        com_detail_info,com_relative_per = getComByName(name)
        comdata[name]=(com_detail_info,com_relative_per)
        time.sleep(3)
    print()