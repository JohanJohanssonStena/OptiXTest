import numpy as np

amount = np.array([700, 1200, 500])
bin_mat = np.empty((0,len(amount)+1))
for i in (range(2**len(amount)+1,2**(len(amount)+1))):
    temp = np.array([int(digit) for digit in str(bin(i)[2:])], np.newaxis)
    bin_mat = np.vstack((bin_mat, temp))
bin_mat = np.delete(bin_mat, 0, axis=1)

s_bin_mat = np.sum(bin_mat*amount[np.newaxis,:], axis=1)
sorti = sort_index = np.argsort([np.where(np.sort(s_bin_mat)[::-1] == x)[0][0] for x in s_bin_mat])

print(s_bin_mat[sorti])
print(bin_mat[sorti,:])