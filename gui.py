from tkinter import *
import search
import requests
from PIL import Image, ImageTk
import io
from googlemaps import Client
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import Counter
import datetime

Google_API_Key = 'AIzaSyBahrp2wpi8q5bUWU1IN71zobn3WG-EAtA'
gmaps = Client(key=Google_API_Key)

class mainGui:

    def __init__(self):
        self.window = Tk()
        self.window.geometry("1000x800")
        self.window['bg'] = "light gray"
        self.window.title("Flight Information")


        self.frame_search = Frame(self.window)
        self.toggle_button_text = StringVar()
        self.toggle_button_text.set("출발")
        self.button_toggle = Button(self.frame_search, textvariable=self.toggle_button_text,
                                    command=self.toggle_text)
        self.button_toggle.pack(side='left', padx=10, pady=10)
        self.frame_search.grid(row=0,column=0)
        self.image_button = PhotoImage(file="image/search_button25.png")
        self.button_search = Button(self.frame_search, image=self.image_button, command=self.search)
        self.button_search['bg'] = 'dark gray'
        self.entry_search = Entry(self.frame_search)

        self.entry_search.pack(side='left')
        self.button_search.pack(side='right')

        self.frame_flight_info = Frame(self.window, bg="white")
        self.frame_flight_info.place(x=10, y=70, width=450, height=650)

        self.listbox = Listbox(self.frame_flight_info, font=("Arial", 12), bg="white", activestyle="none")
        self.scrollbar = Scrollbar(self.frame_flight_info, orient="vertical", command=self.listbox.yview)
        self.listbox.config(yscrollcommand=self.scrollbar.set)

        self.listbox.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas_chart = Canvas(self.window, bg="dark gray")
        self.canvas_chart.place(x=470, y=70, width=540, height=300)

        self.canvas_map = Canvas(self.window, bg="black")
        self.canvas_map.place(x=470, y=380, width=540, height=300)

        self.label_map = Label(self.canvas_map)
        self.label_map.pack()

        self.frame_weather = Frame(self.window, bg="light gray")
        self.frame_weather.place(x=470, y=690, width=540, height=100)

        self.label_weather_info = Label(self.frame_weather, text="", font=("Arial", 12), bg="light gray")
        self.label_weather_info.pack(pady=10)

        # 지도 설정
        center = gmaps.geocode("인천공항")[0]['geometry']['location']
        self.zoom = 10
        size = "540x300"
        maptype = "roadmap"
        map_url = f"https://maps.googleapis.com/maps/api/staticmap?center={center['lat']},{center['lng']}&zoom={self.zoom}&size={size}&maptype={maptype}&key={Google_API_Key}"
        marker_url = f"&markers=color:red%7C{center['lat']},{center['lng']}"
        map_url += marker_url

        #지도 이미지 업데이트
        response = requests.get(map_url)

        image_data = io.BytesIO(response.content)
        image = Image.open(image_data)
        photo = ImageTk.PhotoImage(image)

        self.label_map.config(image=photo)
        self.label_map.image = photo

    def search(self):
        airlines = []
        gates = []
        arrivetimes = []
        winds = []
        temps = []
        senstemps = []
        himiditys = []
        arrival = self.entry_search.get()
        data = search.search_flight(arrival)

        if not data: return

        for item in data:
            airline = dict()
            for key,value in item.items():
                airline[key] = value
            airlines.append(airline)
                # if 'airline' in item:
                #     airlines.append(item['airline'])
                # if 'gatenumber' in item:
                #     gates.append(item['gatenumber'])
                # if 'estimatedDateTime' in item:
                #     arrivetimes.append(item['estimatedDateTime'])
                # if 'wind' in item:
                #     winds.append(item['wind'])
                # if 'temp' in item:
                #     temps.append(item['temp'])
                # if 'senstemp' in item:
                #     senstemps.append(item['senstemp'])
                # if 'himidity' in item:
                #     himiditys.append(item['himidity'])



        # print(airlines)
        # print(gates)
        # print(arrivetimes)
        for i in range(len(airlines)):
            self.create_flight_info(self.frame_flight_info, f"항공사: 항공사 {airlines[i]['airline']}", f"도착 예정시간:{airlines[i]['estimatedDateTime']}",
                                    f"탑승구: {airlines[i]['gatenumber']}",i)

        self.display_weather_info(airlines[0]['wind'], airlines[0]['temp'], airlines[0]['senstemp'], airlines[0]['himidity'])
        # 지도 업데이트
        self.update_map()
        self.create_bar_chart(arrivetimes)


    def create_flight_info(self, parent, airline, arrival_time, gate, index):
        frame = Frame(parent, bg="light gray", bd=2, relief="groove")
        frame.place(x=10, y=10 + index * 120, width=430, height=110)

        label_airline = Label(frame, text=airline, bg="light gray", font=("Arial", 14))
        label_airline.pack(anchor='w', padx=10, pady=5)

        label_arrival_time = Label(frame, text=arrival_time, bg="light gray", font=("Arial", 12))
        label_arrival_time.pack(anchor='w', padx=10)

        label_gate = Label(frame, text=gate, bg="light gray", font=("Arial", 12))
        label_gate.pack(anchor='w', padx=10)

    def display_weather_info(self, winds, temps, senstemps, himiditys):
        # 날씨 정보를 라벨에 표시하는 함수
        weather_info = (
            f"풍속: {' '.join(winds)}\n"
            f"온도: {' '.join(temps)}\n"
            f"체감 온도: {' '.join(senstemps)}\n"
            f"습도: {' '.join(himiditys)}"
        )
        self.label_weather_info.config(text=weather_info)

    def create_bar_chart(self, arrivetimes):
        hours = [int(time[11:13]) for time in arrivetimes]  # 시간 부분 추출
        hour_counts = Counter(hours)

        #if not hour_counts:
            #return

        # 캔버스 초기화
        self.canvas_chart.delete("all")

        # 막대 그래프 그리기
        max_count = max(hour_counts.values())
        canvas_height = int(self.canvas_chart['height'])
        canvas_width = int(self.canvas_chart['width'])
        bar_width = canvas_width // 24

        for hour, count in hour_counts.items():
            x0 = hour * bar_width
            y0 = canvas_height - (count / max_count) * canvas_height
            x1 = (hour + 1) * bar_width
            y1 = canvas_height
            self.canvas_chart.create_rectangle(x0, y0, x1, y1, fill="blue")
            self.canvas_chart.create_text(x0 + bar_width // 2, y0 - 10, text=str(count), anchor=S)
            self.canvas_chart.create_text(x0 + bar_width // 2, canvas_height + 10, text=str(hour), anchor=N)

    def toggle_text(self):
        # 버튼 텍스트를 토글하는 함수
        if self.toggle_get() == "출발":
            self.toggle_button_text.set("도착")
        else:
            self.toggle_button_text.set("출발")

    def toggle_get(self):
        # 버튼 텍스트 내용을 반환하는 함수
        return self.toggle_button_text.get()


    def update_map(self):
        # 지도 설정

        # 검색시에 도착 공항을 중심으로
        if self.toggle_get() == "출발":      # 출발일 때는 인천공항으로
            center = gmaps.geocode("인천공항")[0]['geometry']['location']
        else:                               # 도착일 때는 검색한 곳으로
            center = gmaps.geocode(f"{self.entry_search.get()}공항")[0]['geometry']['location']

        self.zoom = 10      # 나중에 줌인 줌아웃 설정할 수도 있게
        size = "540x300"
        maptype = "roadmap"
        map_url = f"https://maps.googleapis.com/maps/api/staticmap?center={center['lat']},{center['lng']}&zoom={self.zoom}&size={size}&maptype={maptype}&key={Google_API_Key}"
        marker_url = f"&markers=color:red%7C{center['lat']},{center['lng']}"
        map_url += marker_url

        # 지도 이미지 업데이트
        response = requests.get(map_url)

        image_data = io.BytesIO(response.content)
        image = Image.open(image_data)
        photo = ImageTk.PhotoImage(image)

        self.label_map.config(image=photo)
        self.label_map.image = photo