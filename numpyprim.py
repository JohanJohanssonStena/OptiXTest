import numpy as np
import math
n = 1000000
n2 = 10000
prim = np.array([ 2,  3,  5,  7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97], dtype='int8')
for i in range(np.max(prim),n2):
    a = prim[0 == i % prim]
    if 0==a.size:
       prim = np.append(prim, i)
r = np.array(list(range(np.max(prim),n+1)))
for i in prim:
    r = r[r % i != 0]
print(r[1:100])
print('step 1 done')
for i in r:
    a = prim[0:math.ceil(math.sqrt(len(prim)))][0 == i % prim[0:math.ceil(math.sqrt(len(prim)))]]
    if 0==a.size:
       prim = np.append(prim, i)
print(prim)