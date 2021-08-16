from bs4.element import ProcessingInstruction
import pandas as pd
import openpyxl
import time
import requests # 크롤링에 사용하는 패키지
from datetime import datetime, timedelta # import time
import json
# from bs4 import BeautifulSoup # html 변환에 사용함
# from requests import status_codes
# from requests.models import Response

url = 'https://datalab.naver.com/shoppingInsight/getCategoryClickTrend.naver'
# 헤더정보
header = { # 유저의 정보를 입력(차단을 막기 위함)
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
    'referer': 'https://datalab.naver.com/shoppingInsight/sCategory.naver'
}
#-------------------------Setting------------------------
res_index=0 # 크롤링 된 결과값에서 필요한 데이터의 인덱스
stdValue = {} # 기준으로 할 메인 cid의 value 값이 담길 딕셔너리
firstCid=84  # 탐색을 시작할 cid 값
secondCid=87  # 탐색을 종료할 cid 값 | cidStart와 cidEnd를 같은 값으로 입력 시 오류 발생
cont='y' # y:범위 내 연속된 모든 카테고리 탐색 | n: 입력한 두 개의 카테고리만 탐색
rangeDate = 30 # 탐색 기간(일)
now = datetime.now() # 현재 시간
startDate = (now - timedelta(days=rangeDate+1)).strftime('%Y-%m-%d') # 오늘 날짜에서 rangeDate+1만큼 뺌
endDate = (now - timedelta(days=1)).strftime('%Y-%m-%d') # 오늘 날짜에서 1만큼 뺌
#--------------------------------------------------------


#--------------------------------------------------------

def crawling(firstCid, secondCid, rangeDate, res_index): # 네이버 쇼핑인사이트 데이터 크롤링하는 함수 | res_index: 구하고자 하는 res 내 인덱스 값
    try: # cid가 없는 경우 index error 발생 ==> index error 발생 시 pass
        data={"cid": [50000000+firstCid, 50000000+secondCid], "timeUnit": "date", "startDate": startDate, "endDate": endDate} # form값을 입력
        Fdata = requests.post(url, headers=header, data=data) # url에 url 정보를 넣고, headers(유저의 정보)에 header변수를, data에 data(입력된 form값)을 전송 후 데이터 요청
        if Fdata.status_code == requests.codes.ok:
            res = json.loads(Fdata.text)["result"] #json.loads는 json 문자열을 파이썬 객체로 변환/ 반대로 json.dumps()는 파이썬 객체를 json 문자열로 변환
            # fullTitle = res[res_index]["fullTitle"]
            if res[res_index]['data']: # ---------------데이터 존재유무 검증
                return [res[res_index]]
        else:
            print("Error code", Fdata.status_code)
            return
    except: # index error 발생 시 pass
        return
#----------------------------------------------------------
resData={}
if cont=="y":
    a=crawling(firstCid, secondCid, rangeDate, 0)
    if a:
        for i in range(firstCid, secondCid):
            b=crawling(firstCid, i+1, rangeDate, 1)
            if b:
                if a!="done":
                    a=crawling(firstCid, i+1, rangeDate, 0)
                    resData=a
                    a="done"
                b=crawling(firstCid, i+1, rangeDate, 1)
                resData.append(b[0])
            elif not b and i==secondCid:
                print("카테고리 b가 존재하지 않음")
            print("진행상황",i-firstCid+1,"/",secondCid-firstCid)
            if i!=0 and i% 25 == 0:
                time.sleep(2.7)
            time.sleep(0.3)
    else:
        print("카테고리 a가 존재하지 않음")
elif cont=="n":
    a=crawling(firstCid, secondCid, rangeDate, 0)
    b=crawling(firstCid, secondCid, rangeDate, 1)
    for i in range(0,2):
        for index in range(0, rangeDate):
            if i==0:
                resData=a
            else:
                resData.append(b[0])
        if i==0:   
            print("-"*110) # 카테고리별 구분선

for i in range(0, len(resData)):
    a=0
    print("후처리중",i+1,"/",len(resData))
    for j in range(0,len(resData[i]["data"])):
        a += resData[i]["data"][j]["value"]
    if resData[i]["fullTitle"] != resData[i]["title"] and resData[i]["fullTitle"]:
        catClass=len(resData[i]["fullTitle"].split(' > '))
        resData[i]["catClass"] = catClass
    else:
        resData[i]["catClass"] = 1
    average=a/rangeDate
    resData[i]["data"] = average


resData=pd.DataFrame(data=resData)
resData = resData.set_index('code')
print(resData)
print("[기간 :", startDate, "~", endDate+"]") # 기간 표시
resData.to_excel('네이버 통계.xlsx')