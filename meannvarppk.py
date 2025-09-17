import pandas as pd
import numpy as np
n = 3000
data = pd.read_excel("Provugnsprotokoll.xlsx")
ikr = np.array(data['Inköpt råvara'].tolist())
ksd = np.array(data['Klassad råvara'].tolist())
n2 = np.size(ikr)
ikr = np.delete(ikr, range(n,n2))
ksd = np.delete(ksd, range(n,n2))

# import data for all elements
all_elem = np.empty((n,0))
elem = ['Si%','Fe%','Cu%','Mn%', 'Mg%', 'Ni%', 'Zn%', 'Ti%', 'Pb%', 'Sn%', 'Cr%','Na%', 'Sr%', 'Sb%', 'P%', 'Bi%', 'Ca%', 'Cd%','Zr%', 'Be%','B%', 'Li%', 'Al%', 'Hg%']
for i in elem:
    single_elem = np.array(data[i].tolist())
    single_elem = np.delete(single_elem, range(n,n2))
    all_elem = np.hstack((all_elem, np.reshape(single_elem,(n,1))))
#replace values with "klassad råvara"
ksd[ksd == '-'] = 'nan'
ikr[ksd != 'nan'] = ksd[ksd != 'nan']
#fix impurities
set_ikr = np.array(list(set(list(ikr))))

yld = np.array(data['Utbyte Medel'].tolist())
yld = np.delete(yld, range(n,n2))
all_elem = all_elem[yld != '-'][:]
ikr = ikr[yld != '-']
yld = yld[yld != '-']

ikr = ikr[all_elem[:,1] != '-']
yld = yld[all_elem[:,1] != '-']
all_elem = all_elem[all_elem[:,1] != '-'][:]
p = np.where(all_elem[:,23] == '-')
all_elem[p,23] = 0.0
for i in list(np.squeeze(p)):
    all_elem[i,22] = str(100 - np.sum(np.float64(all_elem[i,0:22])))
    
yld = np.float64(yld)
all_elem = np.float64(all_elem)

yld_mean = np.array([], dtype='float64')
yld_std = np.array([], dtype='float64')
len_p = np.array([], dtype='int64')
elem_mean = np.empty((0,24), dtype='float64')
elem_std = np.empty((0,24), dtype='float64')

for i in set_ikr:
    p = np.where(i == ikr)
    yld_mean = np.append(yld_mean, np.mean(yld[p]))
    yld_std = np.append(yld_std, np.std(yld[p]))
    len_p = np.append(len_p, np.size(p))

    elem_mean = np.vstack((elem_mean, np.mean(all_elem[p,:], axis=1)))
    elem_std = np.vstack((elem_std, np.std(all_elem[p,:], axis=1)))

p = np.empty((1,0), dtype='int64')
imp_elem = np.array(['Si%', 'Fe%', 'Cu%', 'Zn%', 'Al%'])
npelem = np.array([elem])
for i in range(0,len(imp_elem)):
    p = np.append(p, np.squeeze(np.where(imp_elem[i] == npelem)))
p = list(set(list(p)))
s_elem_std = np.empty((1,0))
for i in range(0,elem_std.shape[0]):
    s_elem_std = np.append(s_elem_std, sum(elem_std[i,p]/elem_mean[i,p]))

s_elem_std = s_elem_std[len_p >= 3]
art_num = set_ikr[len_p >= 3]
s_elem_std, art_num = zip(*sorted(zip(list(s_elem_std), list(art_num))))
s_elem_std = np.reshape(np.array(s_elem_std), (len(s_elem_std),1))
art_num = np.reshape(np.array(art_num), (len(art_num),1))
D = np.hstack((art_num, s_elem_std))
df = pd.DataFrame(D)
#print(df)
#df.to_excel('my_dat.xlsx', index=False)

L = np.empty((0,28), dtype='U20')
for i in range(0,len(set_ikr)):
    arr = np.array([[set_ikr[i]], [set_ikr[i]], [set_ikr[i]]], dtype='U20')
    arr = np.hstack((arr,np.array([[len_p[i]], [len_p[i]], [len_p[i]]], dtype='U20')))
    arr = np.hstack((arr, np.array([['Mean'], ['Std'], ['CV ratio']])))
    arr = np.hstack((arr, np.array([[yld_mean[i]], [yld_std[i]], [yld_std[i]/yld_mean[i]]], dtype='U20')))
    for j in range(0,len(elem)):
        arr = np.hstack((arr, np.array([[elem_mean[i,j]], [elem_std[i,j]], [elem_std[i,j]/elem_mean[i,j]]], dtype='U20')))
    L = np.vstack((L, arr))
df = pd.DataFrame(L)
titles = ['Artikel', 'Antal test', 'Data typ', 'Utbyte', 'Si%','Fe%','Cu%','Mn%', 'Mg%', 'Ni%', 'Zn%', 'Ti%', 'Pb%', 'Sn%', 'Cr%','Na%', 'Sr%', 'Sb%', 'P%', 'Bi%', 'Ca%', 'Cd%','Zr%', 'Be%','B%', 'Li%', 'Al%', 'Hg%']
df.columns = titles
#print(df)
#df.to_excel('my_data.xlsx', index=False)

#yld_result = np.array(['Artikel', 'Medel', 'Avvikelse', 'Test'], dtype='U20')
#for i in range(0,len(set_ikr)):
#    h = np.array([set_ikr[i], round(yld_mean[i],6), round(yld_std[i],6), len_p[i],],dtype='U20')
#    yld_result = np.vstack((yld_result,h))
#print(pd.DataFrame(yld_result))