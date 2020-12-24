import tkinter as tk

class Grid_manager:

    def __init__(self, frame):
        self.row = 0
        self.column = 0
        for k in range(4):
            frame.columnconfigure(k, weight=1)

    def insert(self, element, pady=3, padx=0, stick='W', nextSpot=True):
        if nextSpot:
            self.column += 1
        element.grid(row=self.row, column=self.column, pady=pady, padx=padx, stick=stick)

    def new_row(self, newColumn=0):
        self.row += 1
        self.column = newColumn