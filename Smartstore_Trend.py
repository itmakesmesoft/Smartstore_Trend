from bs4.element import ProcessingInstruction
import pandas as pd
import openpyxl
import time
import requests # 크롤링에 사용하는 패키지
from datetime import datetime, timedelta # import time
import json
import random

url = 'https://datalab.naver.com/shoppingInsight/getCategoryClickTrend.naver'
# 헤더정보
header = { # 유저의 정보를 입력(차단을 막기 위함)
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
    'referer': 'https://datalab.naver.com/shoppingInsight/sCategory.naver'
}


#---------------------- 설정값 --------------------------
firstCid = int(input("탐색을 시작할 Cid 값 : "))
secondCid = int(input("탐색을 종료할 Cid 값 : ")) # 탐색을 종료할 cid 값 | cidStart와 cidEnd를 같은 값으로 입력 시 오류 발생
rangeDate = int(input("탐색 기간 : ")) # 탐색 기간(일)
fill='y' # y:범위 내 연속된 모든 카테고리 탐색 | n: 입력한 두 개의 카테고리만 탐색
continuity='n' # 이어서 할 경우'y', 처음부터 시작할 경우 'n'
#--------------------------------------------------------


#-----------------------기본값---------------------------
res_index=0 # 크롤링 된 결과값에서 필요한 데이터의 인덱스
resData=[]
stdValue = {} # 기준으로 할 메인 cid의 value 값이 담길 딕셔너리
now = datetime.now() # 현재 시간
startDate = (now - timedelta(days=rangeDate)).strftime('%Y-%m-%d') # 오늘 날짜에서 rangeDate+1만큼 뺌
endDate = (now - timedelta(days=1)).strftime('%Y-%m-%d') # 오늘 날짜에서 1만큼 뺌
#--------------------------------------------------------


#--------------------------------------------------------
def crawling(firstCid, secondCid, res_index): # 네이버 쇼핑인사이트 데이터 크롤링하는 함수 | res_index: 구하고자 하는 res 내 인덱스 값
    resData=[]
    data={"cid": [50000000+firstCid, 50000000+secondCid], "timeUnit": "date", "startDate": startDate, "endDate": endDate} # form값을 입력
    if res_index==2:
        data["cid"].append(50000001+secondCid)
    Fdata = requests.post(url, headers=header, data=data) # url에 url 정보를 넣고, headers(유저의 정보)에 header변수를, data에 data(입력된 form값)을 전송 후 데이터 요청
    time.sleep(.5) #--------------------------------------서버 호출 텀
    time.sleep(random.randint(0,1)) #---------------------서버 호출 텀
    if Fdata.status_code == requests.codes.ok:
        res = json.loads(Fdata.text)["result"] 
        for i in range(0,res_index+1):
            if res[i]["fullTitle"]!=None and res[i]["data"]:
                resData+=[res[i]]
            else:
                break
        return resData
    else:
        print("Error code", Fdata.status_code)
        if Fdata.status_code==503 or Fdata.status_code==502:
            print("10분 뒤 다시시도")
            time.sleep(600)
            crawling(firstCid, secondCid, res_index)
        return
#----------------------------------------------------------

cntTry=round((secondCid-firstCid)/2+1,0)
predTime=round((cntTry*.5)+((cntTry//25)*3)+((cntTry//100)*27)+((cntTry//500)*60)+((cntTry//1000)*120),0)
print("예상시간", str(timedelta(seconds=predTime)))
print("서버 전송 시도 : 총",cntTry,"회")

if fill=="Y" or fill=="y":
    # -------- firstCid 찾기 --------
    if continuity=="n": # 이어서 하는 경우엔 firstCid 찾는 과정 생략
        for i in range(firstCid, secondCid+1):
            first=crawling(i, i+1, 2)
            try:
                if first[0]["code"]:
                    firstCid=int(first[0]["code"])-50000000
                    first="done"
                    break
            except:
                if i==secondCid:
                    print("범위 내 Cid 없음")
                pass
    # --------secondCid 찾고 resData에 추가 -------
    if first=="done":
        j=firstCid
        while j < secondCid:
            print("진행상황",round((j-firstCid+1)/(secondCid-firstCid)*100,1),"%")
            scnd=j+1
            count=j-firstCid
            if secondCid-j>=2:
                res_index=2
            else:
                res_index=1
            second=crawling(firstCid, scnd, res_index)
            if first=="written":
                try:
                    for k in range(1, len(second)):
                        for n in range(0,rangeDate):
                            valueA = resData[0]["data"][n]["value"]
                            valuea = second[0]["data"][n]["value"]
                            valueb = second[k]["data"][n]["value"]
                            value = round(valueA*valueb/valuea, 10)
                            # print("기준A :",valueA, "A :", valuea ,"B :", valueb, "환산 B값 :",value)
                    resData+=second[1:]
                except:
                    print(j+50000000,"번 cid Pass")
                    pass
            else:
                resData=second
                first="written"
            #-------- 서버 요청 텀 -----------
            if count!=0 and count% 25 == 0:
                time.sleep(random.randint(1,5))
            if count!=0 and count% 100 == 0:
                time.sleep(random.randint(25,29))
            if count!=0 and count% 500 == 0:
                time.sleep(random.randint(50,70))
            if count!=0 and count% 1000 == 0:
                time.sleep(random.randint(100,140))
            #--------------------------------
            if secondCid-j>=2:
                j+=2
            else:
                j+=1
    # print(resData)
elif fill=="N" or fill=="n":
    resData=crawling(firstCid, secondCid, 1)
    # print(resData)
#----------------------------------------------------------



#----------------데이터 가공 과정---------------------------
for i in range(0, len(resData)):
    total=0
    # print("후처리중",i+1,"/",len(resData))
    for j in range(0,len(resData[i]["data"])):
        total += resData[i]["data"][j]["value"]
    if resData[i]["fullTitle"] != resData[i]["title"] and resData[i]["fullTitle"]:
        catClass=len(resData[i]["fullTitle"].split(' > '))
        resData[i]["catClass"] = catClass
    else:
        resData[i]["catClass"] = 1
    average=total/rangeDate
    resData[i]["data"] = average



#--------------데이터 엑셀 저장------------------------------
resData=pd.DataFrame(data=resData)
# resData = resData.set_index('code')
print(resData)
print("[기간 :", startDate, "~", endDate+"]") # 기간 표시
resData.to_excel('네이버 통계.xlsx')