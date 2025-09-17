import tkinter as tk
import matplotlib
import numpy as np

matplotlib.use('TkAgg')

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

n = [8,12]
x = 4
y = 4
ew = 1
ns = 0
A = np.zeros(n)
A[y,x] = 2
A[y,x-1] = 4

class App(tk.Tk):
    def __init__(self, A):
        super().__init__()
        self.title('Snake')
        self.restart()
        self.figure = Figure(figsize=(6,6), dpi=100)
        self.axes = self.figure.add_subplot()
        self.axes.imshow(A, cmap = 'gray', vmin = 0, vmax = 2)
        
        self.figure_canvas = FigureCanvasTkAgg(self.figure, self)
        NavigationToolbar2Tk(self.figure_canvas, self)
        self.figure_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.restart()
        
        self.bind('<Up>', self.move_n)
        self.bind('<Down>', self.move_s)
        self.bind('<Left>', self.move_w)
        self.bind('<Right>', self.move_e)

    def movement(self, _event = None):
        stop = True
        self.x += self.ew
        self.y += self.ns
        self.A += self.A*1.01
        if (self.x < 0 or self.y < 0) or (self.x > n[1]-1 or self.y > n[0]-1):
            stop = False
            self.lost()
        if stop:
            if self.A[self.y, self.x] > 2:
                stop = False
                self.lost()
        if stop:
            if self.A[self.y, self.x] >= 0:
                self.A[np.where(np.max(self.A) == self.A)] = 0
            self.A[self.y,self.x] = 2


            if np.size(np.where(self.A < 0)) == 0:
                self.food()
            self.axes.imshow(self.A, cmap = 'gray', vmin = -1, vmax = 2).set_data(self.A)
            self.figure_canvas.draw()
            self.timer()

    def food(self, _event=None):
        self.food_y = np.random.randint(0,self.n[0])
        self.food_x = np.random.randint(0,self.n[1])
        while self.A[self.food_y, self.food_x] != 0:
            self.food_y = np.random.randint(0,self.n[0])
            self.food_x = np.random.randint(0,self.n[1])
        self.A[self.food_y, self.food_x] = -1

    def timer(self):
        if self.move:
            self.after(1000, self.movement)
    def move_n(self, _event = None):
        self.ew = 0
        self.ns = -1
    def move_s(self, _event = None):
        self.ew = 0
        self.ns = 1
    def move_w(self, _event = None):
        self.ew = -1
        self.ns = 0
    def move_e(self, _event = None):
        self.ew = 1
        self.ns = 0
    def button_combined(self):
        self.movement()
        self.d_button()
    def d_button(self):
        self.start_button.destroy()
    def restart_combined(self):
        self.restart_button.destroy()
        self.restart()
    def lost(self):
        self.move = False
        self.restart_button = tk.Button(text='Restart', command=self.restart_combined)
        self.restart_button.place(x=500, y=500)

    def restart(self):
        self.A = np.zeros(n)
        self.n = n
        self.x = x
        self.y = y
        self.ew = ew
        self.ns = ns
        self.move = True

        self.start_button = tk.Button(text='Start', command=self.button_combined)
        self.start_button.place(x=500, y=500)


app = App(A)
app.geometry('1000x1000')
app.mainloop()