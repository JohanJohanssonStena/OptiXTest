import tkinter as tk

root = tk.Tk()
root.title('Simple App')

def on_click():
    lbl.config(text='Button clicked')

lbl = tk.Label(root, text='Label 1')
lbl.grid(row=0, column=0)

print(lbl.config().keys())

btn = tk.Button(root, text='Button 1', command=on_click)
btn.grid(row=0, column=1)
root.mainloop()
