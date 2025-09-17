import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np


# Initialize main window
root = tk.Tk()
root.title("Interactive Histogram")


size = 0.15
# Create a figure and axis for the histogram
name = ['Fe', 'Cu', 'Mn', 'Si'] * 6
lower_b = np.array([95, 0.2, 0.5, 0.3] * 6)
upper_b = np.array([98, 0.3, 1.0, 0.6] * 6)
complete_alloy = np.array([96.2, 0.25, 0.7, 0.4] * 6)
intervals = []
for i in range(len(name)):
    interval = f'{name[i]} ({lower_b[i]}-{upper_b[i]})'
    intervals.append(interval)

n = len(name)

fig, ax = plt.subplots(figsize=(8, n *2*size))
ax.set_xlim(0,1)
ax.set_ylim(0.5, n + 0.5)
ax.set_yticks(np.arange(1, n + 1))
ax.set_yticklabels(intervals)

move_upper_b = np.ones(24)

red_lines = []
for i in range(n):
    val_norm = (complete_alloy[i] - lower_b[i]) / (upper_b[i] - lower_b[i])

    ax.add_patch(plt.Rectangle((0, i + 1 -size), 1 , 2*size, facecolor='lightgray', edgecolor='black'))
    red_line = ax.plot([move_upper_b[i], move_upper_b[i]], [i + 1 -size, i + 1 + size], color='red', linewidth=2)
    red_lines.append(red_line)
    ax.plot([val_norm, val_norm], [i + 1 - size, i + 1 + size], color='blue', linewidth=2)

    ax.text(1.05, i + 1, f'{complete_alloy[i]:.3f}', va='center')

# ax.set_title('Toleranskontroll')
# ax.set_xlabel('Normaliserat intervall (0-100%)')
plt.tight_layout()
# Embed the matplotlib figure in Tkinter
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.grid(row=0, column=0, rowspan=24)

# Function to change a value
def change_value(index, delta):
    move_upper_b[index] += delta
    red_lines[index][0].remove()
    new_line = ax.plot([move_upper_b[index], move_upper_b[index]], [index + 1 -size, index + 1 + size], color='red', linewidth=2)
    red_lines[index] = new_line
    canvas.draw()

# Create buttons for each value
for i in range(0, 24):
    frame = tk.Frame(root)
    frame.grid(row=i, column=2)

    tk.Button(frame, text="+", command=lambda i=i: change_value(23-i, 0.05)).grid(row=0, column=1)
    # tk.Label(frame, text=f"V{i+1}").pack()
    tk.Button(frame, text="-", command=lambda i=i: change_value(23-i, -0.05)).grid(row=0, column=0)

# Start the GUI loop
root.mainloop()
 