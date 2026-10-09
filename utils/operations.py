import numpy as np
import warnings

def self_correlation(arr, k=10, max_shift=100):
    arr = np.asarray(arr).flatten()
    original_max_shift = max_shift
    max_shift = min(max_shift, len(arr) - 1)

    if max_shift < original_max_shift:
        warnings.warn(f"Array length is {len(arr)}. Computing shifts only up to {max_shift}.")

    results = []

    for shift in range(1, max_shift + 1):
        corr = np.corrcoef(arr[:-shift], arr[shift:])[0, 1]
        results.append((shift, corr))

    results.sort(key=lambda x: x[1] if not np.isnan(x[1]) else -np.inf, reverse=True)

    for shift, corr in results[:k]:
        print(f"Shift: {shift:3d}, Correlation: {corr:.6f}")

    return results[:k]