import http.client
import xml.etree.ElementTree as ET

import resource

conn = http.client.HTTPConnection("apis.data.go.kr")


f = open("공항코드.txt","r",encoding='UTF-8')
aiport_dict = dict()        # 공항명(지역이름) : 공항코드 를 담는 딕셔너리
while True:
    data = f.readline().split()     # 한 줄씩 읽어서
    if not data : break             # 없으면 중단
    aiport_dict[data[1]] = data[0]  # 딕셔너리에 추가

def search_api( 종류, user_input = None):
    serviceKey = "eLcNVCfcVblDAm4R38R6ZyXiv6NCbnm4BW%2BDZkJ8n6pyZ%2B%2B0neiwxu9JxX8Vfq6p11Kprd%2Fc7csZGGulLZjvEQ%3D%3D&"
    if 종류 == '기상':
        if not user_input in aiport_dict:   # 입력 받은 공항명이 있는지 검사
            print("해당 위치의 공항이 존재하지 않습니다.")
            return []
        else:
            arrival = aiport_dict[user_input]   # 공항명으로 공항코드 가져오기
            print(arrival)
            if resource.p.toggle_get() == "출발":
                operation = "getPassengerArrivalsWorldWeather"
            else:
                operation = "getPassengerDeparturesWorldWeather"
            info = "StatusOfPassengerWorldWeatherInfo/"+operation+"?serviceKey=" + serviceKey
            request = "numOfRows=5&pageNo=1&from_time=0000&to_time=2400&airport="+arrival+"&lang=K&type=xml"
    elif 종류 == '주차':
        info = "BusInformation/getBusInfo?serviceKey="+serviceKey
        request = "numOfRows=10&pageNo=1&area=1&type=xml"
    elif 종류 == '셔틀':
        # 도착정보 :/B551177/ShtbusInfo/getShtbArrivalPredInfo?serviceKey=eLcNVCfcVblDAm4R38R6ZyXiv6NCbnm4BW%2BDZkJ8n6pyZ%2B%2B0neiwxu9JxX8Vfq6p11Kprd%2Fc7csZGGulLZjvEQ%3D%3D&type=xml&location=0&numOfRows=10&pageNo=1
        # 출발시간 :/B551177/ShtbusInfo/getShtbTimeInfo?serviceKey=eLcNVCfcVblDAm4R38R6ZyXiv6NCbnm4BW%2BDZkJ8n6pyZ%2B%2B0neiwxu9JxX8Vfq6p11Kprd%2Fc7csZGGulLZjvEQ%3D%3D&type=xml&day_type=1&start_time=0&numOfRows=10&pageNo=1
        info = "ShtbusInfo/getShtbTimeInfo?serviceKey=" + serviceKey
        request = "type=xml&day_type=1&start_time=0&numOfRows=10&pageNo=1"


    key = "/B551177/" + info
    conn.request("GET",key+request)
    req = conn.getresponse()
    # print(req.status,req.reason)
    # print(req.read().decode('utf-8'))
    xml_data = req.read().decode('utf-8')

    root = ET.fromstring(xml_data)
    items = root.find(".//items")
    data_list = []
    for item in items.findall("item"):
        data_dict = {}
        for child in item:
            data_dict[child.tag] = child.text
        data_list.append(data_dict)

    for d in data_list:
        print(d)
    return data_list