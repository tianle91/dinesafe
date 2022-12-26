def normalize(arr, lowest_val: float = 0., hightest_val: float = 1.):
    if lowest_val >= hightest_val:
        raise ValueError('lowest val must be strictly smaller than highest val')
    # normalize to 0, 1
    arr_min, arr_max = min(arr), max(arr)
    arr_range = arr_max - arr_min
    arr = (arr - arr_min) / arr_range
    if lowest_val == 0. and hightest_val == 1.:
        return arr
    # return rescaled
    return lowest_val + arr * (hightest_val - lowest_val)
