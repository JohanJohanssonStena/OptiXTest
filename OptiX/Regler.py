import numpy as np
import pandas as pd
import re
import os



set_artnum = np.array([110, 112, 216, 218, 324, 327, 370, 501, 504, 530, 625, 642]).astype(str)

appdata_local = os.getenv('LOCALAPPDATA')
folder1 = 'OptiX'
folder2 = 'Data'
file = 'Regler.xlsx'
full_path = os.path.join(appdata_local, folder1, folder2, file)

df = pd.read_excel(full_path)
col_names = df.columns
amount = df.iloc[0].tolist()
df = df.iloc[1:].reset_index(drop=True)

A_add_on = np.empty((0,len(set_artnum)))

for i in col_names:
    A_add = np.zeros((1, len(set_artnum)))[0]
    col = np.array(df[i].tolist()).astype(str)
    for j in col:
        A_add[j == set_artnum] = 1
    A_add_on = np.vstack((A_add_on, A_add))

amount = np.reshape(amount, (len(amount), 1))




print(A_add_on)
print(amount)
