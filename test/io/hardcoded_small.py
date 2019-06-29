import numpy as np
import pandas as pd
import anndata

def hardcoded_small_day_pairs():
    data = [ [ 1, 2, 50 ], [ 2, 3, 80 ], [ 1, 3, 10 ] ]
    return pd.DataFrame(data, columns = [ 't0', 't1', 'lambda1' ])
