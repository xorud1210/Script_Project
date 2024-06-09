import urllib.request
from tkinter import *
import search
import telepot
from telepot.loop import MessageLoop
import requests
from PIL import Image, ImageTk
import io
from googlemaps import Client
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.font_manager as fm
from collections import Counter
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

Google_API_Key = 'AIzaSyBahrp2wpi8q5bUWU1IN71zobn3WG-EAtA'
gmaps = Client(key=Google_API_Key)

class mainGui:

    def __init__(self):
        self.window = Tk()
        self.window.geometry("1000x800")
        self.window['bg'] = "light gray"
        self.window.title("Flight Information")

        self.frames = {}    # 하나의 창? 페이지? 가 한 프레임

        self.create_frames()    # 여기서 쓰이는 창(프레임)을 생성

        self.bot = telepot.Bot('7249865131:AAH6niNiFwVd5zgKxRUuw2-f2uSrQzU8DxM')
        MessageLoop(self.bot, self.handle_message).run_as_thread()
        #bot.sendMessage('7496452214', '테스트입니다')

        self.create_menu()              # 메뉴 바 생성
        self.show_frame('search')       # 프레임 전환 함수 search, shuttle 등
        

    def create_menu(self):
        menubar = Menu(self.window)

        menubar.add_command(label='항공편 검색', command=lambda: self.show_frame("search"))

        menubar.add_command(label='셔틀 정보', command=lambda: self.show_frame("shuttle"))

        self.window.config(menu=menubar)
    def create_frames(self):
        # 새로운 페이지의 프레임 만들 때
        # 페이지의 프레임은 window에 연결, 페이지 안의 내용들은 만든 프레임에 연결

        self.create_search_frame()
        self.create_shuttle_frame()

        for frame in self.frames.values():
            frame.place(relwidth=1, relheight=1)

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()


    def create_search_frame(self):
        self.frames['search'] = Frame(self.window)
        # 검색 상자 프레임
        self.frame_search = Frame(self.frames['search'], bg='skyblue')
        self.frame_search.pack(anchor='center')
        self.set_matplotlib_font()

    def create_main_ui(self):
        self.frame_search = Frame(self.window)
        self.toggle_button_text = StringVar()
        self.toggle_button_text.set("출발")
        self.button_toggle = Button(self.frame_search, textvariable=self.toggle_button_text,
                                    command=self.toggle_text)
        self.button_toggle.pack(side='left', padx=10, pady=10)
        # self.frames['search'].pack()
        self.image_button = PhotoImage(file="image/search_button25.png")
        self.button_search = Button(self.frame_search, image=self.image_button, command=self.search_weather)
        self.button_search['bg'] = 'dark gray'
        self.entry_search = Entry(self.frame_search)

        # email 버튼
        self.button_email_ui = Button(self.frame_search, text="Open UI", command=self.open_new_ui)

        self.entry_search.pack(side='left')
        self.button_search.pack(side='right')
        self.button_email_ui.pack(side='right', padx=10, pady=10)

        # 검색 리스트 / 버튼으로 변경 및 스크롤바 수정
        self.frame_flight_container = Frame(self.frames['search'], bg="white")
        self.frame_flight_container.pack(side="left")

        self.canvas_flight = Canvas(self.frame_flight_container, bg='white',width=450,height=650)
        self.canvas_flight.pack(side="left")

        self.scrollbar = Scrollbar(self.frame_flight_container, orient="vertical", command=self.canvas_flight.yview)
        self.scrollbar.pack(side="right", fill='y')

        self.frame_flight_info = Frame(self.canvas_flight, bg="white")

        self.canvas_flight.config(yscrollcommand=self.scrollbar.set)
        self.canvas_flight.create_window((0,0), window=self.frame_flight_info, anchor='nw')
        self.frame_flight_info.bind("<Configure>", self.on_frame_configure)

        # 그래프
        self.canvas_chart = Canvas(self.frames['search'], bg="dark gray")
        self.canvas_chart.place(x=470, y=70, width=540, height=300)

        # 지도 표시
        self.canvas_map = Canvas(self.frames['search'], bg="black")
        self.canvas_map.place(x=470, y=380, width=540, height=300)

        self.label_map = Label(self.canvas_map)
        self.label_map.pack()

        # 기상 정보 표시
        self.frame_weather = Frame(self.frames['search'], bg="light gray")
        self.frame_weather.place(x=470, y=690, width=540, height=100)

        self.label_weather_info = Label(self.frame_weather, text="", font=("Arial", 12), bg="light gray")
        self.label_weather_info.pack(pady=10)

        # 날씨 이미지
        self.weather_label = Label(self.frames['search'])
        self.weather_label.place(x=935, y=380, width=75, height=75)

        self.update_map()



    def create_shuttle_frame(self):
        self.frames['shuttle'] = Frame(self.window, bg='blue')
        Label(self.frames['shuttle'], text='shuttle frame')

    def on_frame_configure(self, event):
        self.canvas_flight.configure(scrollregion=self.canvas_flight.bbox("all"))

    def clear_ui(self):
        for widget in self.window.winfo_children():
            widget.destroy()

    def create_new_ui(self):
        self.frame_new_ui = Frame(self.window, bg="light gray")
        self.frame_new_ui.pack(fill='both', expand=True)

        Label(self.frame_new_ui, text="This is the new UI", font=("Arial", 16), bg="light gray").pack(pady=20)

        Button(self.frame_new_ui, text="Go Back", command=self.back_to_main_ui).pack(pady=20)
        Button(self.frame_new_ui, text="Send Email", command=self.open_email_ui).pack(pady=20)

    def back_to_main_ui(self):
        # self.clear_ui()
        self.show_frame("search")

    def open_new_ui(self):
        # self.clear_ui()
        self.create_new_ui()

    def search_weather(self):
        self.airlines = []
        arrivetimes = []
        arrival = self.entry_search.get()
        data = search.search_api('기상', arrival)

        if not data: return

        for item in data:
            airline = dict()
            for key,value in item.items():
                airline[key] = value
            self.airlines.append(airline)
            arrivetimes.append(item['estimatedDateTime'])


        for i in range(len(self.airlines)):
            text = f"항공사: {self.airlines[i]['airline']} \n도착 예정시간: {self.airlines[i]['estimatedDateTime']}\n탑승구: {self.airlines[i]['gatenumber']}"
            self.create_flight_info(text)

        self.display_weather_info(self.airlines[0]['wind'], self.airlines[0]['temp'], self.airlines[0]['senstemp'], self.airlines[0]['himidity'])
        # 지도 업데이트
        self.update_map()
        self.update_weather()
        self.create_bar_chart(arrivetimes)

    def search_shuttle(self):
        data = search.search_api('셔틀')
        # 아직 무슨 데이터를 어떻게 주는지 몰라서 나중에 업데이트 해야 될 듯?

    def search_parking(self):
        data = search.search_api('주차')
        # 아직 무슨 데이터를 어떻게 주는지 몰라서 나중에 업데이트 해야 될 듯?

    def create_flight_info(self, text):
        button = Button(self.frame_flight_info,text=text,width=63,height=5)
        button.config(command=lambda btn = button: self.select_flight)
        button.pack(fill='x', pady=5)
        # frame = Frame(parent, bg="light gray", bd=2, relief="groove")
        # frame.place(x=10, y=10 + index * 120, width=410, height=110)
        #
        # label_airline = Label(frame, text=airline, bg="light gray", font=("Arial", 14))
        # label_airline.pack(anchor='w', padx=10, pady=5)
        #
        # label_arrival_time = Label(frame, text=arrival_time, bg="light gray", font=("Arial", 12))
        # label_arrival_time.pack(anchor='w', padx=10)
        #
        # label_gate = Label(frame, text=gate, bg="light gray", font=("Arial", 12))
        # label_gate.pack(anchor='w', padx=10)

    def select_flight(self):
        pass
    def display_weather_info(self, winds, temps, senstemps, himiditys):
        # 날씨 정보를 라벨에 표시하는 함수
        weather_info = (
            f"풍속: {' '.join(winds)}\n"
            f"온도: {' '.join(temps)}\n"
            f"체감 온도: {' '.join(senstemps)}\n"
            f"습도: {' '.join(himiditys)}"
        )
        self.label_weather_info.config(text=weather_info)

    def set_matplotlib_font(self):
        # 여기에서 사용할 폰트 경로를 지정합니다. (예: 'C:/Windows/Fonts/malgun.ttf' 또는 시스템에 맞는 폰트 경로)
        font_path = 'C:/Windows/Fonts/malgun.ttf'
        font_name = fm.FontProperties(fname=font_path).get_name()
        plt.rc('font', family=font_name)
    def create_bar_chart(self, arrivetimes):
        hours = [int(time[0:2]) for time in arrivetimes]  # 시간 부분 추출
        hour_counts = Counter(hours)

        hours_sorted = sorted(hour_counts.keys())
        counts_sorted = [hour_counts[hour] for hour in hours_sorted]

        # 캔버스 초기화
        for widget in self.canvas_chart.winfo_children():
            widget.destroy()

        # 막대 그래프 그리기
        fig, ax = plt.subplots()
        ax.bar(hours_sorted, counts_sorted)


        ax.set_ylabel('비행기 수')
        ax.set_title("시간대별 공항 운행정보")

        # Tkinter에 그래프 표시
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_chart)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
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


    def update_weather(self):
        url = self.airlines[0]['wimage']

        with urllib.request.urlopen(url) as u:
            raw_data = u.read()

        wm = Image.open(io.BytesIO(raw_data))
        image = ImageTk.PhotoImage(wm)
        self.weather_label.config(image=image)
        self.weather_label.image = image

    def open_email_ui(self):
        self.email_ui_window = Toplevel(self.window)
        self.email_ui_window.title("Send Email")
        self.email_ui_window.geometry("400x300")
        self.email_ui_window['bg'] = "light gray"

        Label(self.email_ui_window, text="Your Email:", bg="light gray").pack(pady=5)
        self.entry_from_email = Entry(self.email_ui_window)
        self.entry_from_email.pack(pady=5)

        Label(self.email_ui_window, text="Recipient Email:", bg="light gray").pack(pady=5)
        self.entry_to_email = Entry(self.email_ui_window)
        self.entry_to_email.pack(pady=5)

        Label(self.email_ui_window, text="Password:", bg="light gray").pack(pady=5)
        self.entry_password = Entry(self.email_ui_window, show='*')
        self.entry_password.pack(pady=5)

        Button(self.email_ui_window, text="Send", command=self.send_email).pack(pady=20)

    def send_email(self):
        from_addr = self.entry_from_email.get()
        to_addr = self.entry_to_email.get()
        password = self.entry_password.get()

        try:
            msg = MIMEMultipart()
            msg['From'] = from_addr
            msg['To'] = to_addr
            msg['Subject'] = 'Flight Information'

            body = 'Here is the flight information you requested.'

            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(from_addr, password)
            text = msg.as_string()
            server.sendmail(from_addr, to_addr, text)
            server.quit()

            print("Email sent successfully")
            self.email_ui_window.destroy()
        except Exception as e:
            print(f"Failed to send email: {e}")

    def handle_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type == 'text':
            airport_name = msg['text']
            # 공항 이름을 사용하여 운항 정보를 검색
            flight_info = self.get_flight_info(airport_name)
            # 운항 정보를 사용자에게 전송
            self.bot.sendMessage(chat_id, flight_info)

    def get_flight_info(self, airport_name):
        # 여기에 공항 이름을 기반으로 운항 정보를 검색하는 로직을 추가하세요.
        # 예를 들어, search_api 함수를 사용할 수 있습니다.
        data = search.search_api('기상', airport_name)
        if not data:
            return "운항 정보를 찾을 수 없습니다."

        flight_info = []
        for item in data:
            info = (
                f"항공사: {item['airline']}\n"
                f"도착 예정시간: {item['estimatedDateTime']}\n"
                f"탑승구: {item['gatenumber']}"
            )
            flight_info.append(info)

        return "\n\n".join(flight_info)


class NewUI:
    def __init__(self):
        self.window = Tk()
        self.window.geometry("1000x800")
        self.window['bg'] = "light gray"
        self.window.title("New UI")
