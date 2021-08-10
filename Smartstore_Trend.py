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

cidStart = 0 # 최소 0
cidEnd = 10 # 카테고리 갯수
rangeDate = 50 # 탐색기간(일)

now = datetime.now()
startDate = (now - timedelta(days=rangeDate+1)).strftime('%Y-%m-%d')
endDate = (now - timedelta(days=1)).strftime('%Y-%m-%d')
print("기간 :", startDate, "~", endDate)






def crawling(cid_index, rangeDate):
    try: # index 에러가 안나는 경우에만 실행 | 인덱스 에러가 나는경우는 해당 인덱스의 시드가 없는 경우
        data={"cid": [50000000, 50000000+i+1], "timeUnit": "date", "startDate": startDate, "endDate": endDate} # form값을 전송
        res = requests.post(url, headers=header, data=data) # url에 url 정보를 넣고, headers(유저의 정보)에 header변수를, data(form값을 전송)에 data를 입력
        if res.status_code == requests.codes.ok:
            result = json.loads(res.text)["result"] #json.loads는 json 문자열을 파이썬 객체로 변환/ 반대로 json.dumps()는 파이썬 객체를 json 문자열로 변환
            code = result[cid_index]["code"]
            title = result[cid_index]["title"]
            fullTitle = result[cid_index]["fullTitle"]

            for j in range(rangeDate): # 크롤링할 기간
                period = result[cid_index]["data"][j]["period"]
                value = result[cid_index]["data"][j]["value"]
                if cid_index==0:
                    stdValue = {}
                    stdValue[j] = value
                    valueA = stdValue[j]
                    valueC = result[0]["data"][j]["value"]
                    valueD = result[1]["data"][j]["value"]
                    value = valueA*valueD/valueC # cid 50000000번 값이 50000000+cid 값에 따라 달라질 수도 있어 stdValue 기준값을 이용해 비례식 계산 | 기준시드값(50000000) : X = 현재시드값(50000000) : 현재시드값(50000002)
                # value = result[1]["data"][i]["value"]
                print("code :", code, "   title :", title, "   fullTitle :", fullTitle, "   period :", period, "   value :", value)

        else:
            print("Error code", res.status_code)
    except: #인덱스 에러가 날 경우 그냥 패스
        pass
    print("-"*110)



# 카테고리 값을 구한다


for i in range(cidStart, cidEnd+1):
    if i == cidStart:# 기준값을 먼저 구한다
        crawling(0, rangeDate)
    crawling(1, rangeDate)
    # print(fullTitle.split(' > '))