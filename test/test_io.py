import pandas as pd
import numpy as np
import anndata
import pytest
import wot.io

# Testing helpers

def assert_np_array_equal(result, expected):
    assert isinstance(result, np.ndarray)
    assert isinstance(expected, np.ndarray)
    assert result.ndim == expected.ndim
    assert result.shape == expected.shape
    assert (result == expected).all()

def assert_pd_frame_equal(result, expected):
    assert isinstance(result, pd.DataFrame)
    assert isinstance(expected, pd.DataFrame)
    assert len(result.columns) == len(expected.columns)
    if len(expected.columns) != 0:
        assert (result.columns == expected.columns).all()
    assert len(result.index) == len(expected.index)
    if len(expected.index) != 0:
        assert (result.index == expected.index).all()
    assert (result == expected).all().all()

def assert_anndata_equal(result, expected):
    assert isinstance(result, anndata.AnnData)
    assert isinstance(expected, anndata.AnnData)
    assert_pd_frame_equal(result.obs, expected.obs)
    assert_pd_frame_equal(result.var, expected.var)
    if type(result.X) == np.float32 or type(expected.X) == np.float32:
        if type(expected.X) == np.float32 and type(expected.X) == np.float32:
            assert result.X == expected.X
        else:
            assert (result.X == expected.X).all()
    elif type(result.X) == np.ndarray and type(expected.X) == np.ndarray:
        assert_np_array_equal(result.X, expected.X)
    else:
        print(f"ERROR: unsupported comparison between anndata.X types {type(result.X)} and {type(expected.X)}")

# Sample data generation

def sample_day_pairs():
    data = [ [ 0, 1, 50 ], [ 1, 2, 80 ], [ 2, 4, 30 ], [ 4, 5, 10 ] ]
    return pd.DataFrame(data, columns=[ "t0", "t1", "lambda1" ])

def sample_dataset():
    x = np.array([ [ 1, 2, 3, 0 ], [ 4, 5, 6, 0 ] ])
    obs = pd.DataFrame(index = [ 'cell_1', 'cell_2' ])
    var = pd.DataFrame(index = [ 'g1', 'g2', 'g3', 'g4' ])
    ds = anndata.AnnData(X=x, obs=obs, var=var)
    return ds

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

def test_read_day_pairs_from_file():
    expected_pairs = sample_day_pairs()
    read_pairs = wot.io.read_day_pairs("test/resources/day_pairs_example.txt")
    assert_pd_frame_equal(read_pairs, expected_pairs)

def test_read_day_pairs_from_string():
    pairs_string = "t0,t1,lambda1;0,1,50;1,2,80;2,4,30;4,5,10"
    expected_pairs = sample_day_pairs()
    read_pairs = wot.io.read_day_pairs(pairs_string)
    assert_pd_frame_equal(read_pairs, expected_pairs)

def test_row_metadata_completion_errors():
    dataset = sample_dataset()
    for file_param in [ "days", "growth_rates", "covariate" ]:
        kwargs = { file_param: "nonexistent.txt" }
        with pytest.raises(ValueError):
            wot.io.add_row_metadata_to_dataset(dataset, **kwargs)

def test_row_metadata_completion_default_growth_rates():
    dataset = sample_dataset()
    wot.io.add_row_metadata_to_dataset(dataset)
    assert (dataset.obs['cell_growth_rate'] == 1.).all()

def test_row_metadata_completion():
    expected_obs = pd.DataFrame([ [ 1, 2., 1 ], [ 2, 3., 0 ] ],
            columns = [ 'day', 'cell_growth_rate', 'covariate' ],
            index = [ 'cell_1', 'cell_2' ])
    dataset = sample_dataset()
    wot.io.add_row_metadata_to_dataset(dataset,
            days="test/resources/small_days.txt",
            growth_rates="test/resources/small_growth_rates.txt",
            covariate="test/resources/small_covariate.txt")
    computed_obs = dataset.obs
    assert_pd_frame_equal(computed_obs, expected_obs)

def test_get_filename_and_extension():
    test_cases = [
            [ "filename.txt", "filename", "txt" ],
            [ "filename.with.dots.txt", "filename.with.dots", "txt" ],
            [ "filename with spaces.txt", "filename with spaces", "txt" ],
            [ "filename.gmt.txt", "filename", "gmt" ],
            [ "confusing_filename_gmt.txt", "confusing_filename_gmt", "txt" ],
            [ "filename.grp.txt", "filename", "grp" ],
            [ "filename.gct.txt", "filename", "gct" ],
            [ "filename.gmx.txt", "filename", "gmx" ],
            [ "filename.loom", "filename", "loom" ],
            ]
    for filename, basename, ext in test_cases:
        assert wot.io.get_filename_and_extension(filename) == (basename, ext)

def test_check_file_extension():
    test_cases = [
            [ "file.loom", "loom", "file.loom" ],
            [ "UPCASE.LOOM", "loom", "UPCASE.LOOM" ],
            [ "wEirdcAse.lOom", "loom", "wEirdcAse.lOom" ],
            [ "wEirdcAse", "loom", "wEirdcAse.loom" ],
            [ "file.grp.txt", "grp.txt", "file.grp.txt" ],
            # FIXME: the behavior of check_file_extension may need to change on these
            [ "file", "grp", "file.grp" ],
            [ "file", "grp.txt", "file.grp.txt" ],
            [ "file.grp", "grp.txt", "file.grp.grp.txt" ],
            [ "normalcase.loom", "loOm", "normalcase.loom.loOm" ],
            ]
    for filename, extension, result in test_cases:
        assert wot.io.check_file_extension(filename, extension) == result

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
