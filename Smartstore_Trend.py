from bs4.element import ProcessingInstruction
import pandas as pd
import numpy as np
import openpyxl
import time
import requests # 크롤링에 사용하는 패키지
from datetime import date, datetime, timedelta # import time
import json
import random
import copy     # copy 모듈을 가져옴


#---------------------- 설정값 --------------------------
excelPath='네이버 통계.xlsx'
#--------------------------------------------------------

#-----------------------기본값---------------------------
firstCid = 0
secondCid = 10
rangeDate = 30
fill='y' # y:범위 내 연속된 모든 카테고리 탐색 | n: 입력한 두 개의 카테고리만 탐색
startPoint = 'n' # 이어서 할 경우'y', 처음부터 시작할 경우 'n'
res_index = 0 # 크롤링 된 결과값에서 필요한 데이터의 인덱스
cntIndex = 0 # 데이터를 가공 시작할 인덱스
stdValue = {} # 기준으로 할 메인 cid의 value 값이 담길 딕셔너리
now = datetime.now() # 현재 시간
startDate = (now - timedelta(days=rangeDate)).strftime('%Y-%m-%d') # 오늘 날짜에서 rangeDate+1만큼 뺌
endDate = (now - timedelta(days=1)).strftime('%Y-%m-%d') # 오늘 날짜에서 1만큼 뺌
lastSavetime=0
#--------------------------------------------------------


#--------------------------------------------------------
def crawling(firstCid, secondCid, res_index): # 네이버 쇼핑인사이트 데이터 크롤링하는 함수 | res_index: 구하고자 하는 res 내 인덱스 값
    resData=[]
    url = 'https://datalab.naver.com/shoppingInsight/getCategoryClickTrend.naver'
    # 헤더정보
    header = { # 유저의 정보를 입력(차단을 막기 위함)
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
    'referer': 'https://datalab.naver.com/shoppingInsight/sCategory.naver'
    }
    data={"cid": [50000000+firstCid, 50000000+secondCid], "timeUnit": "date", "startDate": startDate, "endDate": endDate} # form값을 입력
    if res_index==2:
        data["cid"].append(50000001+secondCid)
    Fdata = requests.post(url, headers=header, data=data) # url에 url 정보를 넣고, headers(유저의 정보)에 header변수를, data에 data(입력된 form값)을 전송 후 데이터 요청
    if Fdata.status_code == requests.codes.ok:
        res = json.loads(Fdata.text)["result"] 
        for i in range(0,res_index+1):
            if res[i]["fullTitle"]!=None and res[i]["data"]:
                resData+=[res[i]] #------------------------------------------!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
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

def SavetoExcel(data, curCid, lastSavetime):
    if datetime.now().timestamp()-lastSavetime>=300 or lastSavetime==0: # 5분마다 자동 저장
        print("저장 중(", round(lastSavetime,0),",", round(datetime.now().timestamp()-lastSavetime,0),")")
        lastSavetime=datetime.now().timestamp()
        savedData=copy.deepcopy(data) #------------------------------------------!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        for i in range(cntIndex, len(savedData)):
            total=0
            for j in range(0,len(savedData[i]["data"])):
                total += savedData[i]["data"][j]["value"]
            average=total/rangeDate
            savedData[i]["data"] = average
            if savedData[i]["fullTitle"] != savedData[i]["title"] and savedData[i]["fullTitle"]:
                catClass=len(savedData[i]["fullTitle"].split(' > '))
                savedData[i]["catClass"] = catClass
            else:
                savedData[i]["catClass"] = 1

        result=pd.DataFrame(data=savedData)
        result = result.set_index('code')
        setting = [{'firstCid':firstCid, 'secondCid':secondCid, 'currentCid':curCid, 'rangeDate':rangeDate, 'startDate':startDate, 'endDate':endDate}]
        setting+=stdValue
        setting = pd.DataFrame(data=setting)
        setting = setting.set_index('firstCid')
        with pd.ExcelWriter(excelPath) as writer:
            result.to_excel(writer, sheet_name='Data')
            setting.to_excel(writer, sheet_name='set')
        print("저장 완료")
    return lastSavetime


def surveyData():
    total=[]
    overseas=[]
    fcnt=-1
    df = pd.read_excel(excelPath, sheet_name=None)
    i=0
    while i < len(df['Data']):
        try:
            cid=str(df['Data'].iloc[i]["code"])
            url = 'https://search.shopping.naver.com/api/search/category?sort=rel&pagingIndex=1&pagingSize=40&viewType=list&productSet=total&catId='+cid
            Sdata = requests.get(url)
            if Sdata.status_code == requests.codes.ok:
                res = json.loads(Sdata.text)
                total.append(res['subFilters'][0]['filterValues'][0]['productCount'])
                overseas.append(res['subFilters'][0]['filterValues'][5]['productCount'])
                # --------------------진행상황 조회--------------------
                cnt=round(i/df['Data'].shape[0]*100,0)
                if cnt!=fcnt:
                    fcnt=cnt 
                print("진행상황 :", round(i/len(df['Data'])*100,0),"%    (상품 조회중",cid,")     (행:", len(df['Data']),"개, i:",i)
                #----------------------------------------------------
                i+=1
            else:
                print("Error code", Sdata.status_code)
                if Sdata.status_code==429:
                    print("서버 과부하로 차단됨. 1분 뒤 다시 시작", cid,"(",i,")조회 실패")
                    time.sleep(60)
        except:
            print("찾을 수 없음(",i,") (",res['subFilters'][0]['filterValues'][0]['productCount']," / ",res['subFilters'][0]['filterValues'][5]['productCount'],")")
            # total.append('')
            # overseas.append('')
        sleepCount(i)



    print("진행상황 : 99.0 %    (저장 중)", len(df['Data']),", ", len(total), ", ", len(overseas))
    # print(total)
    # print(overseas)
    df['Data']["전체상품수"]=total
    df['Data']["해외직구상품수"]=overseas
    df['Data']["적합도(전체)"] = round(df['Data']['data']/df['Data']["전체상품수"]*1000000, 3)
    df['Data']["적합도(해외)"] = round(df['Data']['data']/df['Data']["해외직구상품수"]*1000000, 3)
    df['Data'] = df['Data'].replace([np.inf,-np.inf], '')
    
    with pd.ExcelWriter(excelPath) as writer:
        df['Data'].to_excel(writer, sheet_name='Data', index=False)
        df['set'].to_excel(writer, sheet_name='set', index=False)
    print("진행상황 : 100.0 %    (저장 완료)")

def sleepCount(count):
    time.sleep(.25)
    time.sleep(random.randint(0,1))
    if count% 25 == 0:
        print("서버 부하 방지 텀")
        if count!=0 and count% 1000 == 0:
            time.sleep(random.randint(80,120))
        elif count!=0 and count% 500 == 0:
            time.sleep(random.randint(50,70))
        elif count!=0 and count% 100 == 0:
            time.sleep(random.randint(20,30))
        elif count!=0 and count% 25 == 0:
            time.sleep(random.randint(8,12))
#----------------------------------------------------------


#----------------------------------------------------------
print("크롤링할 항목(번호)을 선택하세요")
func = int(input("(0: 검색지수 및 등록상품 갯수, 1: 등록상품 갯수) : "))

if func==0:
    print("검색 타입을 선택해주세요")
    fill=str(input("(y:범위 내 연속된 모든 카테고리 탐색, n: 입력한 두 개의 카테고리만 탐색) : ")) # y:범위 내 연속된 모든 카테고리 탐색 | n: 입력한 두 개의 카테고리만 탐색
    print("처음부터 시작하시겠습니까?")
    startPoint=str(input("(처음부터 시작할 경우'y', 이어서 받을 경우 'n') : ")) # 이어서 할 경우'y', 처음부터 시작할 경우 'n'

    if fill=="Y" or fill=="y":
        # -------- firstCid 찾기 --------
        if startPoint=='n':
            br = pd.read_excel(excelPath, sheet_name=None)
            resData = br['Data'].to_dict('records')
            set = br['set'].to_dict('records')
            stdValue = br['set'][['period', 'value']].to_dict('records')[1:]
            cntIndex = len(resData) #continue index<< savetoexcel에서 쓰임
            firstCid = int(set[0]['firstCid'])
            secondCid = int(set[0]['secondCid'])
            rangeDate = set[0]['rangeDate']
            curCid = int(set[0]['currentCid'])
            startDate = set[0]['startDate']
            endDate = set[0]['endDate']
            first="written"
        elif startPoint=="y": # 이어서 하는 경우엔 firstCid 찾는 과정 생략
            firstCid = int(input("탐색을 시작할 Cid 값 : "))
            secondCid = int(input("탐색을 종료할 Cid 값 : ")) # 탐색을 종료할 cid 값 | cidStart와 cidEnd를 같은 값으로 입력 시 오류 발생
            rangeDate = int(input("탐색 기간 : ")) # 탐색 기간(일)
            for i in range(firstCid, secondCid+1):
                first=crawling(i, i+1, 2)
                try:
                    if first[0]["code"]:
                        firstCid=int(first[0]["code"])-50000000
                        stdValue = first[0]["data"]
                        first="done"
                        curCid=firstCid
                        break
                except:
                    if i==secondCid:
                        print("범위 내 Cid 없음")
                    pass

        # ------------------ 예상 시간 계산 ------------------
        cntTry=round((secondCid-curCid)/2+1,0)
        predTime=round((cntTry*.75)+((cntTry//25)*3)+((cntTry//100)*23)+((cntTry//500)*50)+((cntTry//1000)*100),0)
        print("예상시간", str(timedelta(seconds=predTime)))
        print("서버 전송 시도 : 총",cntTry,"회")
        # ---------------------------------------------------

        # --------secondCid 찾고 resData에 추가 -------
        if first=="done" or first=="written":
            while curCid < secondCid:
                print("진행상황 :",round((curCid-firstCid+1)/(secondCid-firstCid)*100,1),"%    (크롤링 중)")
                scnd=curCid+1
                count=curCid-firstCid
                if secondCid-curCid>=2:
                    res_index=2
                    curCid+=2
                else:
                    res_index=1
                    curCid+=1
                second=crawling(firstCid, scnd, res_index)
                if first=="written":
                    try:
                        for k in range(1, len(second)):
                            for n in range(0,len(second[0]["data"])):
                                valueA = stdValue[n]["value"]
                                valuea = second[0]["data"][n]["value"]
                                valueb = second[k]["data"][n]["value"]
                                value = round(valueA*valueb/valuea, 10)
                        resData+=second[1:]
                        lastSavetime = SavetoExcel(resData, curCid, lastSavetime)
                    except:
                        print(curCid+50000000,"번 cid Pass") #5710, 5792, 5794, 5796 패스
                        pass
                else:
                    resData=second
                    lastSavetime = SavetoExcel(resData, curCid, lastSavetime)
                    first="written"
                sleepCount(count) #서버 과부하 방지용 슬립


    elif fill=="N" or fill=="n":
        resData=crawling(firstCid, secondCid, 1)
    SavetoExcel(resData, curCid, 0) # 마지막 저장
    surveyData()
    print("[기간 :", startDate, "~", endDate+"]") # 기간 표시
elif func==1:
    surveyData()

# elif func==2:
#     test()