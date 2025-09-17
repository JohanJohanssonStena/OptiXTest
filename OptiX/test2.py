
import numpy as np

all_artnum = np.array(['001', '002', '003', '004', '001P', '004P', '005P']).astype('U16')

set_artnum_p = np.array(['001', '002', '003', '004', '005']).astype('U16')

# Find all article numbers in all_artnum that end with 'P'
p_mask = np.char.endswith(all_artnum, 'P')
p_artnums = all_artnum[p_mask]
# Remove 'P' from the end of each matched article number
base_artnums = np.char.rstrip(p_artnums, 'P')

# Replace matching entries in set_artnum_p with their 'P' version
for i in range(len(p_artnums)):
    set_artnum_p[set_artnum_p == base_artnums[i]] = p_artnums[i]





print(set_artnum_p)