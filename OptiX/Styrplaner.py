import numpy as np
import pandas as pd
import re
r = 0.49
df = pd.read_excel('Styrplan uttag.xlsx')


elem = ['Si', 'Fe', 'Cu', 'Mn', 'Mg', 'Ni', 'Zn', 'Ti', 'Pb', 'Sn', 'Cr', 'Na', 'Sr','Sb', 'P', 'Bi', 'Ca', 'Cd', 'Zr', 'Be', 'B', 'Li', 'Al', 'Hg']

sales_article = np.array(df['Försäljningsartikel'].tolist())
set_sales_article = sales_article[0:len(sales_article):6]
# print(set_sales_article)

all_tolerance=np.empty((len(sales_article),0))
for i in elem:
    temp_list = np.array(df[i].tolist())
    temp_list = temp_list[:, np.newaxis]
    all_tolerance = np.hstack((all_tolerance, temp_list))

outer_min = all_tolerance[0:len(sales_article):6]
inner_min = all_tolerance[1:len(sales_article):6]
inner_max = all_tolerance[2:len(sales_article):6]
outer_max = all_tolerance[3:len(sales_article):6]
dec_min = all_tolerance[4:len(sales_article):6]
dec_max = all_tolerance[5:len(sales_article):6]
tol_min = outer_min
tol_min[~np.isnan(inner_min)] = inner_min[~np.isnan(inner_min)]
tol_min = tol_min - r * np.power(10, dec_min*(-1))
tol_max = outer_max
tol_max[~np.isnan(inner_max)] = inner_max[~np.isnan(inner_max)]
tol_max = tol_max + r * np.power(10, (dec_max-1)*(-1))

tol_max[tol_max > 100] = 100
tol_min[tol_min < 0] = 0
print(tol_max)


print(df)