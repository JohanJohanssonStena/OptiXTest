import tkinter as tk

class AutoCompleteEntry(tk.Entry):
    def __init__(self, master, suggestions, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.suggestions = suggestions
        self.var = self["textvariable"] = tk.StringVar()
        self.var.trace("w", self.on_change)
        self.bind("<Down>", self.select_suggestion)
        self.listbox = None

    def on_change(self, *args):
        input_text = self.var.get()
        if input_text == "":
            self.hide_suggestions()
        else:
            matches = [s for s in self.suggestions if s.lower().startswith(input_text.lower())]
            if matches:
                self.show_suggestions(matches)
            else:
                self.hide_suggestions()

    def show_suggestions(self, matches):
        if not self.listbox:
            self.listbox = tk.Listbox(self.master, height=5)
            self.listbox.bind("<<ListboxSelect>>", self.on_select)
            self.listbox.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height())
        self.listbox.delete(0, tk.END)
        for match in matches:
            self.listbox.insert(tk.END, match)

    def hide_suggestions(self):
        if self.listbox:
            self.listbox.destroy()
            self.listbox = None

    def on_select(self, event):
        if self.listbox:
            selected = self.listbox.get(self.listbox.curselection())
            self.var.set(selected)
            self.hide_suggestions()

    def select_suggestion(self, event):
        if self.listbox and self.listbox.size() > 0:
            self.listbox.select_set(0)
            self.listbox.event_generate("<<ListboxSelect>>")

# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("300x200")

    suggestions = ["Apple", "Appeal", "Cherry", "Chase", "Elderberry", "Fig", "Grape"]
    entry = AutoCompleteEntry(root, suggestions)
    entry.pack(pady=20, padx=20)

    root.mainloop()