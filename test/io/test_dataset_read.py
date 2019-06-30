from .io_test_helpers import *

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

def test_read_anndata_txt():
    read_ds = wot.io.read_anndata("test/resources/small/dataset/dataset.txt")
    expected_ds = hardcoded_small_ds()
    assert_anndata_equal(read_ds, expected_ds)

def test_read_anndata_default():
    """read_anndata should interpret any weird extension as txt"""
    read_as_txt = wot.io.read_anndata("test/resources/small/dataset/dataset.txt")
    read_as_wtf = wot.io.read_anndata("test/resources/small/dataset/dataset.weirdextension")
    assert_anndata_equal(read_as_txt, read_as_wtf)
