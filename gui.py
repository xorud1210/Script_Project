from tkinter import *

class mainGui:

    def __init__(self):
        self.window = Tk()
        self.window.geometry("800x600")
        self.window['bg'] = "gray"

        self.frame_search = Frame(self.window)
        self.frame_search.grid(row=0,column=0)
        self.image_button = PhotoImage(file="image/search_button25.png")
        self.button_search = Button(self.frame_search, image=self.image_button)
        self.button_search['bg'] = 'dark gray'
        self.button_search.pack(side='right')

        self.window.mainloop()
