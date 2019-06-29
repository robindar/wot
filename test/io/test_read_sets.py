from .io_test_helpers import *

# Sample data generation

def sample_gene_sets():
    obs = pd.DataFrame(index = [ 'gene_1', 'gene_2' ])
    var = pd.DataFrame([ 'just a cell set', 'and another', 'and a last one' ],
            index = [ 'set_1', 'set_2', 'set_3' ],
            columns = [ 'description' ])
    x = np.array([ [ 1, 1, 1 ], [ 0, 1, 1 ] ])
    ds = anndata.AnnData(X=x, obs=obs, var=var)
    return ds

def sample_extended_gene_sets():
    obs = pd.DataFrame(index = [ 'gene_1', 'gene_2', 'gene_3', 'gene_4' ])
    var = pd.DataFrame([ 'just a cell set', 'and another', 'and a last one' ],
            index = [ 'set_1', 'set_2', 'set_3' ],
            columns = [ 'description' ])
    x = np.array([ [ 1, 1, 1 ], [ 0, 1, 1 ], [ 0, 0, 0], [ 0, 0, 0 ] ])
    ds = anndata.AnnData(X=x, obs=obs, var=var)
    return ds

# Tests

def test_read_gmx():
    read_gene_sets = wot.io.read_gmx("test/resources/small_gene_sets.gmx")
    expected_gene_sets = sample_gene_sets()
    assert_anndata_equal(read_gene_sets, expected_gene_sets)

def test_read_gmx_with_feature_ids():
    read_gene_sets = wot.io.read_gmx("test/resources/small_gene_sets.gmx",
            feature_ids = [ 'gene_1', 'gene_2', 'gene_3', 'gene_4' ])
    expected_gene_sets = sample_extended_gene_sets()
    assert_anndata_equal(read_gene_sets, expected_gene_sets)

def test_read_gmt():
    read_gene_sets = wot.io.read_gmt("test/resources/small_gene_sets.gmt")
    expected_gene_sets = sample_gene_sets()
    assert_anndata_equal(read_gene_sets, expected_gene_sets)

def test_read_gmt_with_feature_ids():
    read_gene_sets = wot.io.read_gmt("test/resources/small_gene_sets.gmt",
            feature_ids = [ 'gene_1', 'gene_2', 'gene_3', 'gene_4' ])
    expected_gene_sets = sample_extended_gene_sets()
    assert_anndata_equal(read_gene_sets, expected_gene_sets)

def test_read_grp():
    read_gene_set = wot.io.read_grp("test/resources/small_gene_set_1.grp")
    obs = pd.DataFrame(index = [ 'gene_1' ])
    var = pd.DataFrame(index = [ 'small_gene_set_1' ])
    x = np.array([ [ 1 ] ])
    expected_gene_set = anndata.AnnData(X=x, obs=obs, var=var)
    assert_anndata_equal(read_gene_set, expected_gene_set)

def test_read_grp_with_feature_ids():
    read_gene_set = wot.io.read_grp("test/resources/small_gene_set_1.grp",
            feature_ids = [ 'gene_1', 'gene_2' ])
    obs = pd.DataFrame(index = [ 'gene_1', 'gene_2' ])
    var = pd.DataFrame(index = [ 'small_gene_set_1' ])
    x = np.array([ [ 1 ], [ 0 ] ])
    expected_gene_set = anndata.AnnData(X=x, obs=obs, var=var)
    assert_anndata_equal(read_gene_set, expected_gene_set)

def test_read_sets_grp():
    read_gene_set = wot.io.read_sets("test/resources/small_gene_set_1.grp")
    obs = pd.DataFrame(index = [ 'gene_1' ])
    var = pd.DataFrame(index = [ 'small_gene_set_1' ])
    x = np.array([ [ 1 ] ])
    expected_gene_set = anndata.AnnData(X=x, obs=obs, var=var)
    assert_anndata_equal(read_gene_set, expected_gene_set)

def test_read_sets_grp_with_feature_ids():
    read_gene_set = wot.io.read_sets("test/resources/small_gene_set_1.grp",
            feature_ids = [ 'gene_1', 'gene_2' ])
    obs = pd.DataFrame(index = [ 'gene_1', 'gene_2' ])
    var = pd.DataFrame(index = [ 'small_gene_set_1' ])
    x = np.array([ [ 1 ], [ 0 ] ])
    expected_gene_set = anndata.AnnData(X=x, obs=obs, var=var)
    assert_anndata_equal(read_gene_set, expected_gene_set)

def test_read_sets_gmt_gmx():
    for ext in [ "gmt", "gmx" ]:
        read_gene_sets = wot.io.read_sets("test/resources/small_gene_sets." + ext)
        expected_gene_sets = sample_gene_sets()
        assert_anndata_equal(read_gene_sets, expected_gene_sets)

def test_read_sets_gmt_gmx_with_feature_ids():
    for ext in [ "gmt", "gmx" ]:
        read_gene_sets = wot.io.read_sets("test/resources/small_gene_sets." + ext,
                feature_ids = [ 'gene_1', 'gene_2', 'gene_3', 'gene_4' ])
        expected_gene_sets = sample_extended_gene_sets()
        assert_anndata_equal(read_gene_sets, expected_gene_sets)
