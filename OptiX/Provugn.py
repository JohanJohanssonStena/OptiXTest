import numpy as np
import pandas as pd
import re
import os
# skapar list från excelfil
df = pd.read_excel('Provugnsprotokoll.xlsx')
ikr = np.array(df['Inköpt råvara'].tolist())
klr = np.array(df['Klassad råvara'].tolist())
obv = np.array(df['Anmärkning'].tolist())
#tar de n senaste proverna
n = 5000
obv = np.delete(obv, range(n, len(ikr)))
ikr = np.delete(ikr, range(n, len(ikr)))
klr = np.delete(klr, range(n, len(klr)))
#bytar inköpt råvara till klassad råvara
klr[klr == '-'] = 'nan'
ikr[klr != 'nan'] = klr[klr != 'nan']
#alla ämnen
elem = ['Si%', 'Fe%', 'Cu%', 'Mn%', 'Mg%', 'Ni%', 'Zn%', 'Ti%', 'Pb%', 'Sn%', 'Cr%', 'Na%', 'Sr%','Sb%', 'P%', 'Bi%', 'Ca%', 'Cd%', 'Zr%', 'Be%', 'B%', 'Li%', 'Al%', 'Hg%']

all_tests=np.empty((n,0))
for i in elem:
    temp_list = np.array(df[i].tolist())
    temp_list = np.delete(temp_list, range(n, len(temp_list)))
    temp_list = temp_list[:, np.newaxis]
    all_tests = np.hstack((all_tests, temp_list))

#filtrering av dokumenet, toma tester, tar bort P, sätter in uträknat Hg och Al värde
p = np.where(all_tests[:,0] == '-')
all_tests = np.delete(all_tests, p, axis=0)
ikr = np.delete(ikr, p)
klr = np.delete(klr, p)
obv = np.delete(obv, p)

pattern = re.compile(r'^\d{3}[Pp]?$')
p = [i for i, val in enumerate(ikr) if not pattern.match(val)]
all_tests = np.delete(all_tests, p, axis=0)
ikr = np.delete(ikr, p)
klr = np.delete(klr, p)
obv = np.delete(obv, p)

ikr = np.char.replace(ikr, 'P', '')
ikr = np.char.replace(ikr, 'p', '')
set_artnum = np.array(list(set(ikr)))
artnum = ikr
flame = artnum[obv == 'Mycket brand3']
flame = np.array(list(set(flame)))
# print(flame)

all_tests[:,23][all_tests[:,23] == '-'] = 0
p = np.where(all_tests[:,22] == '-')
all_tests[p,22] = 100-np.sum(np.squeeze((all_tests[p,0:22].astype(np.float64))),axis=1)
all_tests = all_tests.astype(np.float64)
#färdig filtrerat
#beräkning på medelvärde och standardavvikelse
imp_elem = [1, 2, 6]
imp_tests = all_tests[:,imp_elem]
mean_c = np.mean(imp_tests, axis=0)
imp_tests = imp_tests / mean_c.reshape(1, -1)

imp_tests = np.power(np.sum(np.power(imp_tests, 2), axis=1), 1/2)
set_std = np.empty(0)
set_mean = np.empty(0)
for i in set_artnum:
    p = np.where(i == artnum)
    set_std = np.hstack((set_std, np.std(imp_tests[p])))
    set_mean = np.hstack((set_mean, np.mean(imp_tests[p])))
#kontrollerar vilka värden som är utanför toleransen och tar bort dessa



amount_test = np.empty(0)
for i in set_artnum:
    amount_test = np.hstack((amount_test, len(np.where(i == artnum)[0])))


std_multiplier = 1.645 #1.645 tar bort de sämsta 10 % av mätningarna
p2 = np.empty(0)
for i in range(0,len(set_artnum)):
    p = (np.where(set_artnum[i] == artnum))[0]
    for j in p:
        if (imp_tests[j] > set_mean[i]+set_std[i]*std_multiplier or imp_tests[j] < set_mean[i]-set_std[i]*std_multiplier) and amount_test[i] > 3:
            p2 = np.hstack((p2, j))

p2 = p2.astype(np.int32)
all_tests = np.delete(all_tests, p2, axis=0)
artnum = np.delete(artnum, p2)
#räknar ut medelvärdet med utan de dåliga testerna
set_mean_final = np.empty((0,24))
for i in set_artnum:
    p = np.where(i == artnum)[0]
    set_mean_final = np.vstack((set_mean_final, np.mean(all_tests[p,:], axis=0)))

#
#manuellt dokument
manual_df = pd.read_excel('Saknade analyser.xlsx')
manual_artnum = np.array(manual_df['Klassad råvara'].tolist())
print(manual_df)

manual_tests = np.empty((len(manual_artnum),0))
for i in elem:
    temp_list = np.array(manual_df[i].tolist())
    temp_list = temp_list[:, np.newaxis]
    manual_tests = np.hstack((manual_tests, temp_list))

p = np.isnan(manual_tests[:, 0])
manual_tests = manual_tests[~p]
manual_artnum = manual_artnum[~p]

p = np.isnan(manual_tests[:,22])

manual_tests[np.isnan(manual_tests)] = 0

manual_tests[p,22] = 100-np.sum(np.squeeze((manual_tests[p,0:22].astype(np.float64))),axis=1)
manual_tests = manual_tests.astype(np.float64)

#slår ihop båda.

set_mean_final = np.vstack((set_mean_final, manual_tests))
set_artnum = np.hstack((set_artnum, manual_artnum))
set_artnum_p = set_artnum.copy()

# Läser in åalistan
appdata_local = os.getenv('LOCALAPPDATA')
folder1 = 'OptiX'
folder2 = 'Data'
file = 'AALISTAN.csv'
full_path = os.path.join(appdata_local, folder1, folder2, file)

aa_df = pd.read_csv(full_path, encoding="latin1", sep=";")
aa_df.columns = aa_df.iloc[0]
aa_df = aa_df.iloc[1:].reset_index(drop=True)

all_artnum = np.array(aa_df['Artikelnummer'].tolist())
all_artnum = all_artnum[all_artnum != '0']

#Sätter ett P bakom de artikelnummer som ska ha ett
p_list = np.empty(0, dtype=int)
for i in all_artnum:
    p = np.where(i + 'P' == all_artnum)[0]
    if len(p) > 0:
        p_list = np.hstack((p_list, p))
list = np.char.replace(all_artnum[p_list], 'P','')
for i in range(0,len(list)):
    p = np.where(list[i] == set_artnum_p)[0]
    if len(p) > 0:
        set_artnum_p[p] = all_artnum[p_list][i]


print(set_artnum == set_artnum_p)
print(set_artnum_p)


#skapar tabell och exclfil
# T = np.hstack((set_artnum.reshape(-1, 1).astype(np.int64), set_mean_final))
# df = pd.DataFrame(T)
# print(df)

# df.to_excel('my_array_export.xlsx', index=False)
