import numpy as np
import pandas as pd
import re
from difflib import SequenceMatcher
# skapar list från excelfil
df = pd.read_excel('Provugnsprotokoll.xlsx')
ikr = np.array(df['Inköpt råvara'].tolist())
klr = np.array(df['Klassad råvara'].tolist())
obv = np.array(df['Anmärkning'].tolist())
supplier = df['Leverantör'].tolist()
supplier = np.array([i.upper() for i in supplier])
#tar de n senaste proverna
n = 5000
obv = np.delete(obv, range(n, len(ikr)))
ikr = np.delete(ikr, range(n, len(ikr)))
klr = np.delete(klr, range(n, len(klr)))
supplier = np.delete(supplier, range(n, len(supplier)))

supplier = np.array([item.strip() for item in supplier]) #rensar mellanslag innan och efter
def clean_string(s):
    return re.sub(r'^\d{5}\s+', '', s)
supplier = np.array([clean_string(word) for word in supplier])

abbreviations = {"SR": "STENA RECYCLING", "JKP": "JÖNKÖPING"}
cities = ["JÖNKÖPING", "ÅSTORP", "ÖREBRO", "OSLO", "KARLSKOGA", "VÄXJÖ", "LJUNGBY", "NYBRO", "VEDDESTA", "LINDKÖPING", "NOSSEBRO", "SKÖVDE", "VETLANDA", "VETLAMDA"]
supplier = np.array([' '.join([abbreviations.get(word, word) for word in sentence.split()]) for sentence in supplier])

supplier = np.array(["STENA ALUMINIUM AB" if "STENA ALU" in word else word for word in supplier])
supplier = np.array(["STENA RECYCLING HALMSTAD" if "HALM" in word or "HALSM" in word else word for word in supplier])
supplier = np.array(["NORD-SCHROTT GMBH & CO KG" if "SCHROTT" in word else word for word in supplier])
supplier = np.array(["JYDSK ALUMINIUM INDUSTRI AB" if "JYDSK" in word else word for word in supplier])
supplier = np.array(["METALLFABRIKEN LJUNGHÄLL AB" if "LJUNGH" in word else word for word in supplier])
supplier = np.array(["B&B RECYCLING GMBH" if "B&B" in word or "BOB" in word else word for word in supplier])
supplier = np.array(["SCANMETALS DEUTSCHLAND GMBH" if "SCANM" in word else word for word in supplier])
supplier = np.array(["AGES GROUP" if "AGES" in word else word for word in supplier])
supplier = np.array(["FRIESLAND SCHROOT BV" if "FRIESELAND" in word or "FREISELAND" in word or "FRIESLAND" in word else word for word in supplier])
supplier = np.array(["SIEGFRIED JACOB GMBH & CO KG" if "JACOB" in word else word for word in supplier])
supplier = np.array(["STENA RECYCLING COMBINED" if "STENA RECYC" in word and "HALM" not in word else word for word in supplier])
supplier = np.array(["FUNDO COMPONENTS AB" if "FUNDO" in word else word for word in supplier])
supplier = np.array(["CUREF GMBH" if "CUREF" in word else word for word in supplier])
supplier = np.array(["SCANPAN" if "SCANPAN" in word else word for word in supplier])
supplier = np.array(["SKOGSLUNDS METALLGJUTERI AB" if "SKOGSLUNDS" in word else word for word in supplier])
supplier = np.array(["SEDENBORGS METALLGJUTERI AB" if "SEDENBORGS" in word else word for word in supplier])
supplier = np.array(["STÅL & METALL AB" if "STÅL" in word and "METALL" in word else word for word in supplier])
supplier = np.array(["VEOLIA RECYCLING SWEDEN AB" if "VEOL" in word else word for word in supplier])
supplier = np.array(["STENA TECHNOWORLD AB" if "TECHNOWORLD" in word else word for word in supplier])

supplier = np.array(["STENA RECYCLING COMBINED" if any(city in word for city in cities) else word for word in supplier])

supplier = np.array([''.join(char for char in word if char not in "/.") for word in supplier]) # tar bort tecken

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
supplier = np.delete(supplier, p)

pattern = re.compile(r'^\d{3}[Pp]?$')
p = [i for i, val in enumerate(ikr) if not pattern.match(val)]
all_tests = np.delete(all_tests, p, axis=0)
ikr = np.delete(ikr, p)
klr = np.delete(klr, p)
obv = np.delete(obv, p)
supplier = np.delete(supplier, p)

ikr = np.char.replace(ikr, 'P', '')
ikr = np.char.replace(ikr, 'p', '')
set_artnum = np.array(list(set(ikr)))
artnum = ikr

all_tests[:,23][all_tests[:,23] == '-'] = 0
p = np.where(all_tests[:,22] == '-')
all_tests[p,22] = 100-np.sum(np.squeeze((all_tests[p,0:22].astype(np.float64))),axis=1)
all_tests = all_tests.astype(np.float64)
#färdig filtrerat

combined_ikr_sup = artnum +' ' + supplier
set_combined_ikr_sup = list(set(combined_ikr_sup))
amount_test = np.empty(0)
for i in set_artnum:
    amount_test = np.hstack((amount_test, len(np.where(i == artnum)[0])))

#räknar ut medelvärdet med utan de dåliga testerna
n_test = np.empty(0)
set_mean_final = np.empty((0,24))
set_std_final = np.empty((0,24))
for i in set_artnum:
    p = np.where(i == artnum)[0]
    set_mean_final = np.vstack((set_mean_final, np.mean(all_tests[p,:], axis=0)))
    set_std_final = np.vstack((set_std_final, np.std(all_tests[p, :], axis=0)))
    n_test = np.hstack((n_test, len(p)))

n_test_sup = np.empty(0)
sup_mean = np.empty((0,24))
sup_std = np.empty((0,24))
for i in set_combined_ikr_sup:
    p = np.where(i == combined_ikr_sup)[0]
    sup_mean = np.vstack((sup_mean, np.mean(all_tests[p,:], axis=0)))
    sup_std = np.vstack((sup_std, np.std(all_tests[p,:], axis=0)))
    n_test_sup = np.hstack((n_test_sup, len(p)))

b1 = np.argsort(set_combined_ikr_sup)
b2 = np.argsort(set_artnum)

sup_mean = sup_mean[b1, :]
sup_std = sup_std[b1, :]
set_combined_ikr_sup = np.sort(set_combined_ikr_sup)

set_mean_final = set_mean_final[b2, :]
set_std_final = set_std_final[b2, :]
set_artnum = np.sort(set_artnum)

n_test = n_test[b2]
n_test_sup = n_test_sup[b1]

arr = np.empty((0,24))
lbl = np.empty(0)
lbl2 = np.empty(0)
for i, item in enumerate(set_artnum):
    p = np.where(np.char.startswith(set_combined_ikr_sup, item[:3]))[0]
    arr = np.vstack((arr, set_mean_final[i, :]))
    arr = np.vstack((arr, set_std_final[i, :]))
    arr = np.vstack((arr, sup_mean[p,:]))
    arr = np.vstack((arr, sup_std[p,:]))
    arr = np.vstack((arr, np.array([np.nan] * len(elem))))
    lbl = np.hstack((lbl, set_artnum[i] + ' mean'))
    lbl = np.hstack((lbl, set_artnum[i] + ' std'))
    lbl = np.hstack((lbl, set_combined_ikr_sup[p] + ' mean'))
    lbl = np.hstack((lbl, set_combined_ikr_sup[p] + ' std'))
    lbl = np.hstack((lbl, np.array([''])))
    lbl2 = np.hstack((lbl2, n_test[i]))
    lbl2 = np.hstack((lbl2, n_test[i]))
    lbl2 = np.hstack((lbl2, n_test_sup[p]))
    lbl2 = np.hstack((lbl2, n_test_sup[p]))
    lbl2 = np.hstack((lbl2, np.array([np.nan])))

df_out = pd.DataFrame(arr, columns=elem)
df_out.insert(0, 'n_test', lbl2)
df_out.insert(0, 'Label', lbl)
print(df_out)
df_out.to_excel('leverator.xlsx', index=False)

sub_abs = np.empty(0)
for i, item in enumerate(set_artnum):
    p = np.where(np.char.startswith(set_combined_ikr_sup, item[:3]))[0]
    sub_abs = np.hstack((sub_abs, np.abs(sup_mean[p, 0] - set_mean_final[i, 0])))
b3 = np.argsort(-sub_abs)
print((np.reshape(set_combined_ikr_sup[b3][0:10], (10, 1))))
imp = [0, 1, 2, 3, 6]
ans = 1000
test = np.power(sup_mean[b3[9], imp], 1)
pw = 1/4
for i in range(len(set_artnum)):
    if ans > np.sum(abs(np.power(np.abs(test), pw) - np.power(np.abs(set_mean_final[i, imp]), pw))):
        ans = np.sum(abs(np.power(np.abs(test), pw) - np.power(np.abs(set_mean_final[i, imp]), pw)))
        a = i
print(set_artnum[a])
    
dif_list = []
for i, value1 in enumerate(set_artnum):
    for j, value2 in enumerate(set_combined_ikr_sup):
        if value1 in value2:
            for k in imp:
                if set_mean_final[i, k] * 1.5 < sup_mean[j, k]  or set_mean_final[i, k] > sup_mean[j, k] * 1.5:
                    dif_list.append(str(value2))
                break
print(dif_list)