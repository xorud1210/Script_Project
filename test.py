import urllib
import http.client
conn = http.client.HTTPConnection("apis.data.go.kr")

arrival = input()
key = "/B551177/StatusOfPassengerWorldWeatherInfo/getPassengerArrivalsWorldWeather?serviceKey=eLcNVCfcVblDAm4R38R6ZyXiv6NCbnm4BW%2BDZkJ8n6pyZ%2B%2B0neiwxu9JxX8Vfq6p11Kprd%2Fc7csZGGulLZjvEQ%3D%3D&"
request = "numOfRows=2&pageNo=1&from_time=0000&to_time=2400&airport="+arrival+"&lang=K&type=xml"

conn.request("GET",key+request)
req = conn.getresponse()
print(req.status,req.reason)
print(req.read().decode('utf-8'))


