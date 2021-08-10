# import numpy as np
# import pandas as pd
import requests # 크롤링에 사용하는 패키지
from bs4 import BeautifulSoup # html 변환에 사용함
from datetime import datetime, timedelta # import time
import json
from requests import status_codes
from requests.models import Response

url = 'https://datalab.naver.com/shoppingInsight/getCategoryClickTrend.naver'

# 헤더정보 필요
header = { # 유저의 정보를 입력(차단을 막기 위함)
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
    'referer': 'https://datalab.naver.com/shoppingInsight/sCategory.naver'
}
rangeDate = 30
now = datetime.now()
startDate = (now - timedelta(days=30)).strftime('%Y-%m-%d')
endDate = now.strftime('%Y-%m-%d')
print("기간 :", startDate, "~", endDate)









# 기준값을 먼저 구한다
# data={"cid": [50000000, 50000001, 50000002], "timeUnit": "date", "startDate": startDate, "endDate": endDate} # form값을 전송
data={"cid": [50000000, 50000001], "timeUnit": "date", "startDate": startDate, "endDate": endDate} # form값을 전송
std = requests.post(url, headers=header, data=data) # url에 url 정보를 넣고, headers(유저의 정보)에 header변수를, data(form값을 전송)에 data를 입력
if std.status_code == requests.codes.ok:
    stdResult = json.loads(std.text)["result"] #json.loads는 json 문자열을 파이썬 객체로 변환/ 반대로 json.dumps()는 파이썬 객체를 json 문자열로 변환
    stdCode = stdResult[0]["code"]
    stdTitle = stdResult[0]["title"]
    stdFullTitle = stdResult[0]["fullTitle"]
    stdPeriod = {}
    stdValue = {}
    try: # index 에러가 안나는 경우에만 실행 | 새벽의 경우 전날 서버데이터 업뎃이 안되어 있어 오류 발생
        for i in range(rangeDate): # 크롤링할 기간
            stdPeriod[i] = stdResult[0]["data"][i]["period"]
            stdValue[i] = stdResult[0]["data"][i]["value"]
            print("code :", stdCode, "   title :", stdTitle, "   fullTitle :", stdFullTitle, "   period :", stdPeriod[i], "   value :", stdValue[i])
    except: #인덱스 에러가 날 경우 그냥 패스
        pass
else:
    print("Error code", std.status_code)





# 나머지 카테고리 값을 구한다
cidStart = 1 # 최소 1
cidEnd = 10 # 카테고리 갯수

for cidStart in range(cidStart, cidEnd+1):
    try: # index 에러가 안나는 경우에만 실행 | 인덱스 에러가 나는경우는 해당 인덱스의 시드가 없는 경우
        data={"cid": [50000000, 50000000+cidStart], "timeUnit": "date", "startDate": startDate, "endDate": endDate} # form값을 전송
        res = requests.post(url, headers=header, data=data) # url에 url 정보를 넣고, headers(유저의 정보)에 header변수를, data(form값을 전송)에 data를 입력
        if res.status_code == requests.codes.ok:
            result = json.loads(res.text)["result"] #json.loads는 json 문자열을 파이썬 객체로 변환/ 반대로 json.dumps()는 파이썬 객체를 json 문자열로 변환
            code = result[1]["code"]
            title = result[1]["title"]
            fullTitle = result[1]["fullTitle"]
            for i in range(rangeDate): # 크롤링할 기간
                period = result[1]["data"][i]["period"]
                valueA = stdValue[i]
                valueC = result[0]["data"][i]["value"]
                valueD = result[1]["data"][i]["value"]
                value = valueA*valueD/valueC # cid 50000000번 값이 50000000+cid 값에 따라 달라질 수도 있어 stdValue 기준값을 이용해 비례식 계산 | 기준시드값(50000000) : X = 현재시드값(50000000) : 현재시드값(50000002)
                # value = result[1]["data"][i]["value"]
                print("code :", code, "   title :", title, "   fullTitle :", fullTitle, "   period :", period, "   value :", value)

        else:
            print("Error code", res.status_code)
    except: #인덱스 에러가 날 경우 그냥 패스
        pass
    print("-"*110)


    # print(fullTitle.split(' > '))