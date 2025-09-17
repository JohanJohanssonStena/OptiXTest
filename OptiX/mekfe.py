import pandas as pd
import numpy as np
import re

df = pd.read_excel('Lagersaldo uttag.xlsx')
artnum = np.array(df['Part No'].tolist())
desc = np.array(df['Part Description'].tolist())
p = []
for i, item in enumerate(desc):
    if 'mek' in item and 'Fe' in item:
        p.append(i)

print(len(p))
def extract_numbers(strings):
    results = []
    for s in strings:
        # Replace comma with dot for decimal consistency
        s = s.replace(',', '.')

        # Match ranges like "5-20%" or "5.5 - 20.75%"
        range_match = re.search(r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*%', s)
        if range_match:
            results.append([float(range_match.group(1)), float(range_match.group(2))])
            continue

        # Match single numbers like "max 10%" or "<40%" or "up to 12.5%"
        single_match = re.search(r'(\d+(?:\.\d+)?)\s*%', s)
        if single_match:
            results.append([float(single_match.group(1))])
            continue

        # If no match, append empty list
        results.append([])
    return results



print(extract_numbers(desc[p]))
