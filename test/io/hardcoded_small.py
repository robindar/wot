import numpy as np
import pandas as pd
import anndata

def hardcoded_small_day_pairs():
    data = [ [ 1, 2, 50 ], [ 2, 3, 80 ], [ 1, 3, 10 ] ]
    return pd.DataFrame(data, columns = [ 't0', 't1', 'lambda1' ])

def hardcoded_small_ds():
    x = np.array([
        [ 1.0, 2.0, 3.0, 4.0 ],
        [ 1.2, 2.2, 3.2, 4.2 ],
        [ 4.3, 3.3, 2.3, 1.3 ],
        [ 2.4, 3.4, 1.4, 4.4 ],
        [ 3.5, 1.5, 4.5, 2.5 ]
        ])
    obs = pd.DataFrame(index = [ 'cell_1', 'cell_2', 'cell_3', 'cell_4', 'cell_5' ])
    var = pd.DataFrame(index = [ 'gene_1', 'gene_2', 'gene_3', 'gene_4' ])
    ds = anndata.AnnData(X=x, obs=obs, var=var)
    return ds

def hardcoded_small_ds_with_metadata():
    x = np.array([
        [ 1.0, 2.0, 3.0, 4.0 ],
        [ 1.2, 2.2, 3.2, 4.2 ],
        [ 4.3, 3.3, 2.3, 1.3 ],
        [ 2.4, 3.4, 1.4, 4.4 ],
        [ 3.5, 1.5, 4.5, 2.5 ]
        ])
    obs = pd.DataFrame([ [ 1, 1., 1 ], [ 2, 2., 1 ], [ 1, 1., 0 ], [ 2, 2., 0 ], [ 1, 1., 1 ]],
            columns = [ 'day', 'cell_growth_rate', 'covariate' ],
            index = [ 'cell_1', 'cell_2', 'cell_3', 'cell_4', 'cell_5' ])
    var = pd.DataFrame(index = [ 'gene_1', 'gene_2', 'gene_3', 'gene_4' ])
    ds = anndata.AnnData(X=x, obs=obs, var=var)
    return ds
