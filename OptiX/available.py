import numpy as np
import pandas as pd
import re
import os

df = pd.read_excel('in stock.xlsx')
artnum = np.array(df['Part No'].tolist())
cost = np.array(df['Estimated Material Cost'].tolist())
exchange = np.array(df['Utbyte (Exchange)'].tolist())
quantity = np.array(df['Available Qty'].tolist())
spot = np.array(df['Warehouse'].tolist())

set_artnum = np.array(list(set(list(artnum))))

set_exchange = np.zeros(len(set_artnum))
set_cost = np.zeros(len(set_artnum))
sum_quantity = np.zeros(len(set_artnum))

for i in range(len(set_artnum)):
    p = np.where(set_artnum[i] == artnum)[0]
    p = np.delete(p, spot[p] == 'FLAK' )
    p = np.delete(p, spot[p] == 'PALL' )
    p = np.delete(p, spot[p] == 'BOX' )
    if p.size > 0:
        set_exchange[i] = exchange[p[0]]
        set_cost[i] = cost[p[0]]
        sum_quantity[i] = np.sum(quantity[p])

set_artnum = np.delete(set_artnum, sum_quantity==0)
set_exchange = np.delete(set_exchange, sum_quantity==0)
set_cost = np.delete(set_cost, sum_quantity==0)
sum_quantity = np.delete(sum_quantity, sum_quantity==0)






