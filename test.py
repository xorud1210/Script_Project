import urllib
import http.client
conn = http.client.HTTPConnection("apis.data.go.kr")

user_input = input()

f = open("공항코드.txt","r",encoding='UTF-8')
aiport_dict = dict()        # 공항명(지역이름) : 공항코드 를 담는 딕셔너리
while True:
    data = f.readline().split()     # 한 줄씩 읽어서
    if not data : break             # 없으면 중단
    aiport_dict[data[1]] = data[0]  # 딕셔너리에 추가

if not user_input in aiport_dict:   # 입력 받은 공항명이 있는지 검사
    print("해당 위치의 공항이 존재하지 않습니다.")
else:
    arrival = aiport_dict[user_input]   # 공항명으로 공항코드 가져오기
    key = "/B551177/StatusOfPassengerWorldWeatherInfo/getPassengerArrivalsWorldWeather?serviceKey=eLcNVCfcVblDAm4R38R6ZyXiv6NCbnm4BW%2BDZkJ8n6pyZ%2B%2B0neiwxu9JxX8Vfq6p11Kprd%2Fc7csZGGulLZjvEQ%3D%3D&"
    request = "numOfRows=2&pageNo=1&from_time=0000&to_time=2400&airport="+arrival+"&lang=K&type=xml"

    conn.request("GET",key+request)
    req = conn.getresponse()
    print(req.status,req.reason)
    print(req.read().decode('utf-8'))


