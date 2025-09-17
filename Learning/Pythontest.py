import numpy as np
import matplotlib.pyplot as plt
j = input('--->')
j = int(j)
prim = [2]
for n in range(2,j+1):
    c = 0
    for i in prim:
        if n % i == 0:
            c = 1
    if c == 0:
        prim.append(n)
prim = np.array(prim)
a = np.nonzero(j == prim)
if a[0].size > 0:
    print(f'{j} is a prime number')
else:
    print(f'{j} is not a prime number')