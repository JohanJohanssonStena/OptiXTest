import tkinter as tk

root = tk.Tk()
root.title('Simple App')

def add_to_list(event=None):
    text = entry.get()
    if text:
        text_list.insert(tk.END, text)
        entry.delete(0, tk.END)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

frame = tk.Frame(root)
frame.grid(row=0, column=0, sticky='nsew')

frame.columnconfigure(0, weight=1)
frame.rowconfigure(1, weight=1)

entry = tk.Entry(frame)
entry.grid(row=0,column=0,sticky='ew')

entry.bind('<Return>',add_to_list)

entry_btn = tk.Button(frame, text='Add',command=add_to_list)
entry_btn.grid(row=0, column=1)

text_list = tk.Listbox(frame)
text_list.grid(row=1,column=0,columnspan=2, sticky='nsew')

root.mainloop()