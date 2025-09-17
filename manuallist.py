import numpy as np
import pandas as pd
n = 3000

data_test = pd.read_excel("Provugnsprotokoll.xlsx")
ikr = np.array(data_test['Inköpt råvara'].tolist())
ksd = np.array(data_test['Klassad råvara'].tolist())
n2 = np.size(ikr)
ikr = np.delete(ikr, range(n,n2))
ksd = np.delete(ksd, range(n,n2))
ksd[ksd == '-'] = 'nan'
ikr[ksd != 'nan'] = ksd[ksd != 'nan']
set_ikr = list(set(list(ikr)))

data_list = pd.read_excel("List of all.xlsx")
art_num = np.array(data_list['Artikelnr'].tolist())
art_num = art_num[art_num != 'nan']
art_num = list(art_num)
set_ikr = list(set_ikr)


for i in range(0,len(art_num)):
    if len(art_num[i]) == 4:
        art_num[i] = art_num[i].replace('P','')

for i in range(0,len(set_ikr)):
    if len(set_ikr[i]) == 4:
        set_ikr[i] = set_ikr[i].replace('P','')

art_num = np.array(list(set(art_num)))
set_ikr = np.array(list(set(set_ikr)))

for i in set_ikr:
    art_num = art_num[i != art_num]

#art_num = [art_num[i != art_num] for i in set_ikr]


print(art_num)
print(len(art_num))