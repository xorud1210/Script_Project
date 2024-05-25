from tkinter import *
import search

class mainGui:

    def __init__(self):
        self.window = Tk()
        self.window.geometry("1000x800")
        self.window['bg'] = "light gray"
        self.window.title("Flight Information")

        self.frame_search = Frame(self.window)
        self.frame_search.grid(row=0,column=0)
        self.image_button = PhotoImage(file="image/search_button25.png")
        self.button_search = Button(self.frame_search, image=self.image_button, command=self.search)
        self.button_search['bg'] = 'dark gray'
        self.entry_search = Entry(self.frame_search)

        self.entry_search.pack(side='left')
        self.button_search.pack(side='right')

        self.frame_flight_info = Frame(self.window, bg="white")
        self.frame_flight_info.place(x=10, y=70, width=450, height=650)
        self.canvas = Canvas(self.frame_flight_info, bg="white")
        self.scrollbar = Scrollbar(self.frame_flight_info, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas, bg="white")

        self.canvas_chart = Canvas(self.window, bg="dark gray")
        self.canvas_chart.place(x=470, y=70, width=540, height=300)

        self.canvas_map = Canvas(self.window, bg="black")
        self.canvas_map.place(x=470, y=380, width=540, height=300)

        self.frame_weather = Frame(self.window, bg="gray")
        self.frame_weather.place(x=470, y=690, width=540, height=70)

        self.window.mainloop()

    def search(self):
        airlines = []
        gates = []
        arrivetimes = []
        arrival = self.entry_search.get()
        data = search.search_flight(arrival)

        if not data: return

        print(data)
        for item in data:
            for key,value in item.items():
                if 'airline' in item:
                    airlines.append(item['airline'])
                if 'gatenumber' in item:
                    gates.append(item['gatenumber'])
                if 'estimatedDateTime' in item:
                    arrivetimes.append(item['estimatedDateTime'])


        print(airlines)
        print(gates)
        print(arrivetimes)
        for i in range(len(airlines)):
            self.create_flight_info(self.frame_flight_info, f"항공사: 항공사 {airlines[i]}", f"도착 예정시간: 12:{arrivetimes[i]}",
                                    f"탑승구: {gates[i]}",i)

    def create_flight_info(self, parent, airline, arrival_time, gate, index):
        frame = Frame(parent, bg="light gray", bd=2, relief="groove")
        frame.place(x=10, y=10 + index * 120, width=430, height=110)

        label_airline = Label(frame, text=airline, bg="light gray", font=("Arial", 14))
        label_airline.pack(anchor='w', padx=10, pady=5)

        label_arrival_time = Label(frame, text=arrival_time, bg="light gray", font=("Arial", 12))
        label_arrival_time.pack(anchor='w', padx=10)

        label_gate = Label(frame, text=gate, bg="light gray", font=("Arial", 12))
        label_gate.pack(anchor='w', padx=10)