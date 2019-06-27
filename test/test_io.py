import pandas as pd
import numpy as np
import anndata
import pytest
import wot.io

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

# Tests

def test_read_day_pairs_from_file():
    expected_pairs = sample_day_pairs()
    read_pairs = wot.io.read_day_pairs("test/resources/day_pairs_example.txt")
    assert isinstance(read_pairs, pd.DataFrame)
    assert (read_pairs.columns == expected_pairs.columns).all()
    assert (read_pairs == expected_pairs).all().all()

def test_read_day_pairs_from_string():
    pairs_string = "t0,t1,lambda1;0,1,50;1,2,80;2,4,30;4,5,10"
    expected_pairs = sample_day_pairs()
    read_pairs = wot.io.read_day_pairs(pairs_string)
    assert isinstance(read_pairs, pd.DataFrame)
    assert (read_pairs.columns == expected_pairs.columns).all()
    assert (read_pairs == expected_pairs).all().all()

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
    assert isinstance(computed_obs, pd.DataFrame)
    assert (computed_obs.columns == expected_obs.columns).all()
    assert (computed_obs == expected_obs).all().all()

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
    assert isinstance(read_gene_sets, anndata.AnnData)
    assert len(read_gene_sets.obs.columns) == 0
    assert (read_gene_sets.obs == expected_gene_sets.obs).all().all()
    assert read_gene_sets.var.columns == expected_gene_sets.var.columns
    assert (read_gene_sets.var == expected_gene_sets.var).all().all()
    assert (read_gene_sets.X == expected_gene_sets.X).all()

def test_read_gmt():
    read_gene_sets = wot.io.read_gmt("test/resources/small_gene_sets.gmt")
    expected_gene_sets = sample_gene_sets()
    assert isinstance(read_gene_sets, anndata.AnnData)
    assert len(read_gene_sets.obs.columns) == 0
    assert (read_gene_sets.obs == expected_gene_sets.obs).all().all()
    assert read_gene_sets.var.columns == expected_gene_sets.var.columns
    assert (read_gene_sets.var == expected_gene_sets.var).all().all()
    assert (read_gene_sets.X == expected_gene_sets.X).all()

def test_read_grp():
    read_gene_set = wot.io.read_grp("test/resources/small_gene_set_1.grp")
    obs = pd.DataFrame(index = [ 'gene_1' ])
    var = pd.DataFrame(index = [ 'small_gene_set_1' ])
    x = np.array([ [ 1 ] ])
    expected_gene_set = anndata.AnnData(X=x, obs=obs, var=var)
    assert isinstance(read_gene_set, anndata.AnnData)
    assert len(read_gene_set.obs.columns) == 0
    assert (read_gene_set.obs == expected_gene_set.obs).all().all()
    assert len(read_gene_set.var.columns) == 0
    assert (read_gene_set.var == expected_gene_set.var).all().all()
    assert (read_gene_set.X == expected_gene_set.X).all()

def test_read_grp_with_feature_ids():
    read_gene_set = wot.io.read_grp("test/resources/small_gene_set_1.grp",
            feature_ids = [ 'gene_1', 'gene_2' ])
    obs = pd.DataFrame(index = [ 'gene_1', 'gene_2' ])
    var = pd.DataFrame(index = [ 'small_gene_set_1' ])
    x = np.array([ [ 1 ], [ 0 ] ])
    expected_gene_set = anndata.AnnData(X=x, obs=obs, var=var)
    assert isinstance(read_gene_set, anndata.AnnData)
    assert len(read_gene_set.obs.columns) == 0
    assert (read_gene_set.obs == expected_gene_set.obs).all().all()
    assert len(read_gene_set.var.columns) == 0
    assert (read_gene_set.var == expected_gene_set.var).all().all()
    assert (read_gene_set.X == expected_gene_set.X).all()
