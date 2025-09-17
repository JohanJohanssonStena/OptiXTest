import numpy as np
import matplotlib.pyplot as plt
name = ['Fe', 'Cu', 'Mn', 'Si']
lower_b = np.array([95, 0.2, 0.5, 0.3])
upper_b = np.array([98, 0.3, 1.0, 0.6])
complete_alloy = np.array([96.2, 0.25, 0.7, 0.4])
intervals = []
for i in range(len(name)):
    interval = f'{name[i]} ({lower_b[i]}-{upper_b[i]})'
    intervals.append(interval)

n = len(name)

fig, ax = plt.subplots(figsize=(8, n *0.6))
ax.set_xlim(0,1)
ax.set_ylim(0.5, n + 0.5)
ax.set_yticks(np.arange(1, n + 1))
ax.set_yticklabels(intervals)



for i in range(n):
    val_norm = (complete_alloy[i] - lower_b[i]) / (upper_b[i] - lower_b[i])

    ax.add_patch(plt.Rectangle((0, i + 1 -0.3), 1 , 0.6, facecolor='lightgray', edgecolor='black'))
    ax.plot([np.ones(4)*0.9, np.ones(4)*0.9], [i + 1 -0.3, i + 1 + 0.3], color='red', linewidth=2)
    ax.plot([val_norm, val_norm], [i + 1 -0.3, i + 1 + 0.3], color='blue', linewidth=2)
    

    ax.text(1.05, i + 1, f'{complete_alloy[i]:.3f}', va='center')

ax.set_title('Toleranskontroll')
ax.set_xlabel('Normaliserat intervall (0-100%)')
plt.tight_layout()
plt.show()

