
import numpy as np

def block_diagonal_stack(matrices):
    """
    Takes a list of 2D NumPy arrays and returns a block diagonal matrix.
    """
    total_rows = sum(mat.shape[0] for mat in matrices)
    total_cols = sum(mat.shape[1] for mat in matrices)

    result = np.zeros((total_rows, total_cols), dtype=matrices[0].dtype)

    row_offset = 0
    col_offset = 0
    for mat in matrices:
        rows, cols = mat.shape
        result[row_offset:row_offset+rows, col_offset:col_offset+cols] = mat
        row_offset += rows
        col_offset += cols

    return result



A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6, 7], [8, 9, 10]])
C = np.array([[11]])

result = block_diagonal_stack([A, B, C])
print(result)

