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


        parking_menu = Menu(menubar, tearoff=0)
        parking_menu.add_command(label='제 1여객터미널', command=lambda: self.show_frame("parking_t1"))
        parking_menu.add_command(label='제 2여객터미널', command=lambda: self.show_frame("parking_t2"))
        menubar.add_cascade(label="주차 정보", menu=parking_menu)

        menubar.add_command(label='예약 정보', command=lambda: self.show_frame("reservation"))

        self.window.config(menu=menubar)
    def create_frames(self):
        # 새로운 페이지의 프레임 만들 때
        # 페이지의 프레임은 window에 연결, 페이지 안의 내용들은 만든 프레임에 연결

        self.create_search_frame()
        self.create_parking_frame()
        self.create_reservation_frame()

        for frame in self.frames.values():
            frame.place(relwidth=1, relheight=1)

    def show_frame(self, name):
        if self.toggle_state == True:
            self.toggle_state = False
            self.frame_parking_info_t1.place_forget()
            self.frame_parking_info_t2.place_forget()

        frame = self.frames[name]
        frame.tkraise()


    def create_search_frame(self):
        self.frames['search'] = Frame(self.window)
        # 검색 상자 프레임
        self.frame_search = Frame(self.frames['search'], bg='skyblue')
        self.frame_search.pack(anchor='center')
        self.set_matplotlib_font()

        # self.frame_search = Frame(self.window)
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


        self.gmail_image = PhotoImage(file="image/gmail25.png")
        self.button_email_ui = Button(self.frame_search, image=self.gmail_image, command=self.open_email_ui)
        self.button_email_ui['bg'] = 'dark gray'
        self.button_email_ui.pack(side='right', padx=10, pady=10)

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

        self.selected_button_search = None


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

        # 즐겨찾기 버튼
        self.star_image = PhotoImage(file='image/star.png')
        self.button_reservation_add = Button(self.frames['search'], bg='white', image=self.star_image, command=self.reservation_add)
        self.button_reservation_add.place(x=1000-64,y=10)

    def reservation_add(self):
        if self.selected_button_search.cget('text') not in self.reservation_list:
            # btn = Button(self.frame_reservation_info, text=self.selected_button_search.cget('text'),width=63,height=5)
            # btn.config(command=lambda button = btn : self.button_click_reservation(button))
            self.reservation_list.append(self.selected_button_search.cget('text'))
            self.update_reservation_list()

    def on_frame_configure(self, event):
        self.canvas_flight.configure(scrollregion=self.canvas_flight.bbox("all"))


    def create_parking_frame(self):
        self.search_parking()

        # t1 주차장
        self.frames['parking_t1'] = Frame(self.window, bg='white', width=1000,height=800)
        self.frame_parking_t1 = Frame(self.frames['parking_t1'])
        self.frame_parking_t1.pack(fill='both')

        map_image = Image.open("image/map_t1.png")
        map_resized = map_image.resize((1000 ,800), Image.LANCZOS)
        self.map_photo = ImageTk.PhotoImage(map_resized)
        self.shuttle_map = Label(self.frame_parking_t1, image=self.map_photo)
        self.shuttle_map.pack(fill='both')

        self.button_t1_P = []
        self.image = []
        for i in range(6):
            self.image.append(PhotoImage(file='image/t1_p'+ str(i) +'.png'))
            self.button_t1_P.append(Button(self.frame_parking_t1, width=100, height = 30, image = self.image[i]))
                                # command=lambda :self.toggle_frame(i,'t1')))
        self.button_t1_P[0].config(command = lambda :self.toggle_frame(0,'t1'))
        self.button_t1_P[1].config(command = lambda :self.toggle_frame(1,'t1'))
        self.button_t1_P[2].config(command = lambda :self.toggle_frame(2,'t1'))
        self.button_t1_P[3].config(command = lambda :self.toggle_frame(3,'t1'))
        self.button_t1_P[4].config(command = lambda :self.toggle_frame(4,'t1'))
        self.button_t1_P[5].config(command = lambda :self.toggle_frame(5,'t1'))

        self.button_t1_P[0].place(x= 137, y=238)
        self.button_t1_P[1].place(x= 713, y=306)
        self.button_t1_P[2].place(x= 133, y=304)
        self.button_t1_P[3].place(x= 499, y=511)
        self.button_t1_P[4].place(x= 234, y=510)
        self.button_t1_P[5].place(x= 292, y=634)

        # 버튼 위치 정보
        self.button_xy = {'t1' : [(137,238),(713, 306),(133,304), (499,511),(234,510),(292,634)]}




        # t2 주차장
        self.frames['parking_t2'] = Frame(self.window, bg='white', width=1000, height=800)
        self.frame_parking_t2 = Frame(self.frames['parking_t2'])
        self.frame_parking_t2.pack(fill='both')

        map_image = Image.open("image/map_t2.png")
        map_resized = map_image.resize((1000, 800), Image.LANCZOS)
        self.map_photo_2 = ImageTk.PhotoImage(map_resized)
        self.shuttle_map_2 = Label(self.frame_parking_t2, image=self.map_photo_2)
        self.shuttle_map_2.pack(fill='both')

        self.button_t2_P = []
        self.image_2 = []

        self.image_2.append(PhotoImage(file='image/t2_short.png'))
        self.button_t2_P.append(Button(self.frame_parking_t2, width=100, height=40, image=self.image_2[0],
                                    command=lambda :self.toggle_frame(0,'t2')))

        self.image_2.append(PhotoImage(file='image/t2_reserve.png'))
        self.button_t2_P.append(Button(self.frame_parking_t2, width=42, height=104, image=self.image_2[1],
                                    command=lambda :self.toggle_frame(1,'t2')))
        self.image_2.append(PhotoImage(file='image/t2_long.png'))
        self.button_t2_P.append(Button(self.frame_parking_t2, width=105, height=48, image=self.image_2[2],
                                    command=lambda :self.toggle_frame(2,'t2')))


        self.button_t2_P[0].place(x=243, y=662)
        self.button_t2_P[1].place(x=533, y=212)
        self.button_t2_P[2].place(x=620, y=285)
        self.button_xy['t2'] = [(243,662),(533,212),(620,285)]


        self.toggle_state = False   # 주차장 정보가 떠있는지 상태값

        # 주차 정보를 띄우는 프레임
        self.frame_parking_info_t1 = Frame(self.frame_parking_t1, bg='lightgray')
        self.frame_parking_info_t2 = Frame(self.frame_parking_t2, bg='lightgray')

        self.parking_info = StringVar()
        self.parking_info.set(" ")

        self.label_parking_info_t1 = Label(self.frame_parking_info_t1, textvariable=self.parking_info)
        self.label_parking_info_t1.pack()
        self.label_parking_info_t2 = Label(self.frame_parking_info_t2, textvariable=self.parking_info)
        self.label_parking_info_t2.pack()

        self.before_select = None


    def create_reservation_frame(self):
        self.reservation_list = []
        self.selected_button_reservation = None

        self.frames['reservation'] = Frame(self.window, bg='gainsboro', width=1000,height=800)

        # 검색 리스트 / 버튼으로 변경 및 스크롤바 수정
        self.reservation_container = Frame(self.frames['reservation'], bg="white")
        self.reservation_container.pack(side="left")

        self.canvas_reservation = Canvas(self.reservation_container, bg='linen', width=450, height=800)
        self.canvas_reservation.pack(side="left")

        self.scrollbar = Scrollbar(self.reservation_container, orient="vertical", command=self.canvas_reservation.yview)
        self.scrollbar.pack(side="right", fill='y')

        self.frame_reservation_info = Frame(self.canvas_reservation, bg="white")

        self.canvas_reservation.config(yscrollcommand=self.scrollbar.set)
        self.canvas_reservation.create_window((0, 0), window=self.frame_reservation_info, anchor='nw')
        self.frame_reservation_info.bind("<Configure>", self.on_frame_configure_r)

        self.image_x = PhotoImage(file="image/x.png")
        self.button_remove = Button(self.frames['reservation'], bg = 'white', image= self.image_x, command=self.remove_reservation)
        self.button_remove.pack(side='left', anchor='center')

    def on_frame_configure_r(self, event):
        self.canvas_reservation.configure(scrollregion=self.canvas_reservation.bbox("all"))

    def remove_reservation(self):
        if self.selected_button_reservation:
            self.reservation_list.remove(self.selected_button_reservation.cget('text'))
            self.selected_button_reservation = None
            self.update_reservation_list()
        #
        # for button in self.reservation_list:
        #     btn = Button(self.frame_reservation_info, text=button.cget('text'),width=63,height=5)



    def update_reservation_list(self):
        # 기존 정보 삭제
        for widget in self.frame_reservation_info.winfo_children():
            widget.destroy()

        # 새로 업데이트
        for txt in self.reservation_list:
            btn = Button(self.frame_reservation_info, text=txt, width=63, height=5)
            btn.config(command=lambda button=btn : self.button_click_reservation(button))
            btn.pack(fill='x', pady=5)



    def toggle_frame(self, i, t):
        if self.toggle_state and self.before_select != None and  self.before_select == i:
            if t == 't1':
                self.frame_parking_info_t1.place_forget()
            elif t == 't2':
                self.frame_parking_info_t2.place_forget()
        else:
            x, y = self.button_xy[t][i]
            if t == 't1':
                self.frame_parking_info_t1.place(x=x-100, y=y - 70)
            elif t == 't2':
                self.frame_parking_info_t2.place(x=x-100, y=y - 70)
            self.update_parking_info(i,t)

        self.toggle_state = not self.toggle_state
        if self.toggle_state and self.before_select != None and self.before_select != i:
            self.toggle_state = True
        self.before_select = i

    def update_parking_info(self, i, t):
        text = ''
        # 노가다
        if t == 't1':
            if i == 0:
                for j in range(3):
                    text += f"{self.data_parking[t][j]['floor']}\t주차된 차량 : {self.data_parking[t][j]['parking']}대 수용가능 차량 : {self.data_parking[t][j]['parkingarea']}대\n"
            elif i == 1:
                for j in range(3,5):
                    text += f"{self.data_parking[t][j]['floor']}\t주차된 차량 : {self.data_parking[t][j]['parking']}대 수용가능 차량 : {self.data_parking[t][j]['parkingarea']}대\n"
            elif i == 2:
                for j in range(5,7):
                    text += f"{self.data_parking[t][j]['floor']}\t주차된 차량 : {self.data_parking[t][j]['parking']}대 수용가능 차량 : {self.data_parking[t][j]['parkingarea']}대\n"
            elif i == 3:
                j = 7
                text += f"{self.data_parking[t][j]['floor']}\t주차된 차량 : {self.data_parking[t][j]['parking']}대 수용가능 차량 : {self.data_parking[t][j]['parkingarea']}대\n"
            elif i == 4:
                j = 8
                text += f"{self.data_parking[t][j]['floor']}\t주차된 차량 : {self.data_parking[t][j]['parking']}대 수용가능 차량 : {self.data_parking[t][j]['parkingarea']}대\n"
            elif i == 5:
                j = 9
                text += f"{self.data_parking[t][j]['floor']}\t주차된 차량 : {self.data_parking[t][j]['parking']}대 수용가능 차량 : {self.data_parking[t][j]['parkingarea']}대\n"
        elif t == 't2':
            if i == 0:
                for j in range(5):
                    text += f"{self.data_parking[t][j]['floor']}\t주차된 차량 : {self.data_parking[t][j]['parking']}대 수용가능 차량 : {self.data_parking[t][j]['parkingarea']}대\n"
            elif i == 1:
                j = 5
                text += f"{self.data_parking[t][j]['floor']}\t주차된 차량 : {self.data_parking[t][j]['parking']}대 수용가능 차량 : {self.data_parking[t][j]['parkingarea']}대\n"
            elif i == 2:
                j = 6
                text += f"{self.data_parking[t][j]['floor']}\t주차된 차량 : {self.data_parking[t][j]['parking']}대 수용가능 차량 : {self.data_parking[t][j]['parkingarea']}대\n"
        self.parking_info.set(text)


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


        for widget in self.frame_flight_info.winfo_children():
            widget.destroy()
            self.selected_button_search = None
        for i in range(len(self.airlines)):
            if self.toggle_get() == "출발":
                path = self.entry_search.get() + "---> 인천\n"
            else:
                path = self.entry_search.get() + "<--- 인천\n"
            text = path + f"항공사: {self.airlines[i]['airline']} \n도착 예정시간: {self.airlines[i]['estimatedDateTime']}\n탑승구: {self.airlines[i]['gatenumber']}"
            self.create_flight_info(text)

        self.display_weather_info(self.airlines[0]['wind'], self.airlines[0]['temp'], self.airlines[0]['senstemp'], self.airlines[0]['himidity'])
        # 지도 업데이트
        self.update_map()
        self.update_weather()
        self.create_bar_chart(arrivetimes)


    def search_parking(self):
        data = search.search_api('주차')

        self.data_parking = { 't1' :[], 't2' : []}
        for item in data:
            d = dict()
            for key, value in item.items():
                d[key] = value
            if 'T1' in item['floor']:
                self.data_parking['t1'].append(d)
            else:
                self.data_parking['t2'].append(d)



    def create_flight_info(self, text):
        button = Button(self.frame_flight_info,text=text,width=63,height=5)
        button.config(command=lambda btn=button: self.button_click(btn))
        button.pack(fill='x', pady=5)

    def button_click(self, button):
        if self.selected_button_search:
            self.selected_button_search.config(bg="SystemButtonFace")

        button.config(bg="lightblue")
        self.selected_button_search = button

    def button_click_reservation(self, button):
        if self.selected_button_reservation:
            self.selected_button_reservation.config(bg="SystemButtonFace")

        button.config(bg="lightblue")
        self.selected_button_reservation = button

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

            # 운항 정보를 본문에 추가
            body = 'Here is the flight information you requested:\n\n'
            for airline in self.airlines:
                body += (
                    f"항공사: {airline['airline']}\n"
                    f"도착 예정시간: {airline['estimatedDateTime']}\n"
                    f"탑승구: {airline['gatenumber']}\n\n"
                )

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
            if msg['text'] == "주차장 정보":
                self.bot.sendMessage(chat_id, self.get_parking_info())
                return
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

    def get_parking_info(self):
        data = self.search_parking()

        text = ''

        for _,d in self.data_parking.items():
            text += _[0].upper() + _[1] + '\n'
            for i in d:
                text += f"{i['floor']}\t주차된 차량 : {i['parking']}대 수용가능 차량 : {i['parkingarea']}대\n"

        return "\n\n" + text


class NewUI:
    def __init__(self):
        self.window = Tk()
        self.window.geometry("1000x800")
        self.window['bg'] = "light gray"
        self.window.title("New UI")
