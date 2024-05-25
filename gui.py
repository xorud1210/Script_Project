from tkinter import *
import search

class mainGui:

    def __init__(self):
        self.window = Tk()
        self.window.geometry("800x600")
        self.window['bg'] = "gray"

        self.frame_search = Frame(self.window)
        self.frame_search.grid(row=0,column=0)
        self.image_button = PhotoImage(file="image/search_button25.png")
        self.button_search = Button(self.frame_search, image=self.image_button, command=self.search)
        self.button_search['bg'] = 'dark gray'
        self.entry_search = Entry(self.frame_search)

        self.entry_search.pack(side='left')
        self.button_search.pack(side='right')

        self.window.mainloop()

    def search(self):
        airlines = set()
        gates = set()
        arrivetimes = set()
        arrival = self.entry_search.get()
        data = search.search_flight(arrival)

        if not data: return

        print(data)
        for item in data:
            for key,value in item.items():
                if 'airline' in item:
                    airlines.add(item['airline'])
                if 'gatenumber' in item:
                    gates.add(item['gatenumber'])
                if 'estimatedDateTime' in item:
                    arrivetimes.add(item['estimatedDateTime'])
        print(airlines)
        print(gates)
        print(arrivetimes)