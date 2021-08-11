# import numpy as np
# import pandas as pd
import requests # 크롤링에 사용하는 패키지
from bs4 import BeautifulSoup # html 변환에 사용함
from datetime import datetime, timedelta # import time
import json
from requests import status_codes
from requests.models import Response

url = 'https://datalab.naver.com/shoppingInsight/getCategoryClickTrend.naver'
# 헤더정보
header = { # 유저의 정보를 입력(차단을 막기 위함)
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
    'referer': 'https://datalab.naver.com/shoppingInsight/sCategory.naver'
}
#-------------------------Setting
cidStart = 11 # 탐색을 시작할 cid 값
cidEnd = 16 # 탐색을 종료할 cid 값 | cidStart와 cidEnd를 같은 값으로 입력 시 오류 발생
rangeDate = 10 # 탐색 기간(일)
now = datetime.now() # 현재 시간
startDate = (now - timedelta(days=rangeDate+1)).strftime('%Y-%m-%d') # 오늘 날짜에서 rangeDate+1만큼 뺌
endDate = (now - timedelta(days=1)).strftime('%Y-%m-%d') # 오늘 날짜에서 1만큼 뺌
print("기간 :", startDate, "~", endDate) # 기간 표시
#---------------------------------


def crawling(cidStart, cidEnd, rangeDate, res_index): #res_index: 구하고자 하는 res 내 인덱스 값
    stdValue = {}
    i = cidStart
    while i < cidEnd:
        try: # cid가 없는 경우 index error 발생 ==> index error 발생 시 pass
            data={"cid": [50000000+cidStart, 50000001+i], "timeUnit": "date", "startDate": startDate, "endDate": endDate} # form값을 입력
            Fdata = requests.post(url, headers=header, data=data) # url에 url 정보를 넣고, headers(유저의 정보)에 header변수를, data에 data(입력된 form값)을 전송 후 데이터 요청
            i+=1
            if Fdata.status_code == requests.codes.ok:
                res = json.loads(Fdata.text)["result"] #json.loads는 json 문자열을 파이썬 객체로 변환/ 반대로 json.dumps()는 파이썬 객체를 json 문자열로 변환
                code = res[res_index]["code"]
                title = res[res_index]["title"]
                fullTitle = res[res_index]["fullTitle"]

                if res[0]['data'] and res[1]['data']: # ---------------데이터 존재유무 검증
                #----------------------------------------------------------------입력 과정
                    for j in range(rangeDate): # ----------------------------크롤링할 기간
                        period = res[res_index]["data"][j]["period"]
                        value = res[res_index]["data"][j]["value"]
                        if res_index==0:
                            stdValue[j] = value
                        else:
                            valueA = stdValue[j]
                            valueC = res[0]["data"][j]["value"]
                            valueD = res[res_index]["data"][j]["value"]
                            value = valueA*valueD/valueC # cid 50000000번 값이 50000000+cid 값에 따라 달라질 수도 있어 stdValue 기준값을 이용해 비례식 계산 | 기준cid값(50000000) : X = 현재cid값(50000000) : 현재cid값(50000002)
                        print("code :", code, "   title :", title, "   fullTitle :", fullTitle, "   period :", period, "   value :", value)
                    print("-"*110) # -------------------------------------카테고리별 구분선
                    if res_index==0:
                        res_index=1
                        i-=1
                #-------------------------------------------------------------------------
                elif not res[0]['data'] and res_index==0:
                    cidStart=i
            else:
                print("Error code", Fdata.status_code)
        except: # index error 발생 시 pass
            pass

crawling(cidStart, cidEnd, rangeDate, 0)
