from .io_test_helpers import *
from .hardcoded_small import *


def test_read_gmx():
    read_gene_sets = wot.io.read_gmx("test/resources/small/gene_sets/gene_sets.gmx")
    expected_gene_sets = hardcoded_small_gene_sets()
    assert_anndata_equal(read_gene_sets, expected_gene_sets)

def test_read_gmx_with_feature_ids():
    read_gene_sets = wot.io.read_gmx("test/resources/small/gene_sets/gene_sets.gmx",
            feature_ids = [ 'gene_1', 'gene_2', 'gene_3', 'gene_4', 'gene_5' ])
    expected_gene_sets = hardcoded_small_gene_sets_extended()
    assert_anndata_equal(read_gene_sets, expected_gene_sets)

def test_read_gmt():
    read_gene_sets = wot.io.read_gmt("test/resources/small/gene_sets/gene_sets.gmt")
    expected_gene_sets = hardcoded_small_gene_sets()
    assert_anndata_equal(read_gene_sets, expected_gene_sets)

def test_read_gmt_with_feature_ids():
    read_gene_sets = wot.io.read_gmt("test/resources/small/gene_sets/gene_sets.gmt",
            feature_ids = [ 'gene_1', 'gene_2', 'gene_3', 'gene_4', 'gene_5' ])
    expected_gene_sets = hardcoded_small_gene_sets_extended()
    assert_anndata_equal(read_gene_sets, expected_gene_sets)

def test_read_grp():
    read_gene_set = wot.io.read_grp("test/resources/small/gene_sets/set_1.grp")
    expected_gene_set = hardcoded_small_gene_set_1()
    assert_anndata_equal(read_gene_set, expected_gene_set)

def test_read_grp_with_feature_ids():
    read_gene_set = wot.io.read_grp("test/resources/small/gene_sets/set_1.grp",
            feature_ids = [ 'gene_1', 'gene_2', 'gene_3', 'gene_4' ])
    expected_gene_set = hardcoded_small_gene_set_1_semiextended()
    assert_anndata_equal(read_gene_set, expected_gene_set)

def test_read_sets_grp():
    read_gene_set = wot.io.read_sets("test/resources/small/gene_sets/set_1.grp")
    expected_gene_set = hardcoded_small_gene_set_1()
    assert_anndata_equal(read_gene_set, expected_gene_set)

def test_read_sets_grp_with_feature_ids():
    read_gene_set = wot.io.read_sets("test/resources/small/gene_sets/set_1.grp",
            feature_ids = [ 'gene_1', 'gene_2', 'gene_3', 'gene_4' ])
    expected_gene_set = hardcoded_small_gene_set_1_semiextended()
    assert_anndata_equal(read_gene_set, expected_gene_set)

def test_read_sets_gmt_gmx():
    for ext in [ "gmt", "gmx" ]:
        read_gene_sets = wot.io.read_sets("test/resources/small/gene_sets/gene_sets." + ext)
        expected_gene_sets = hardcoded_small_gene_sets()
        assert_anndata_equal(read_gene_sets, expected_gene_sets)

def test_read_sets_gmt_gmx_with_feature_ids():
    for ext in [ "gmt", "gmx" ]:
        read_gene_sets = wot.io.read_sets("test/resources/small/gene_sets/gene_sets." + ext,
                feature_ids = [ 'gene_1', 'gene_2', 'gene_3', 'gene_4', 'gene_5' ])
        expected_gene_sets = hardcoded_small_gene_sets_extended()
        assert_anndata_equal(read_gene_sets, expected_gene_sets)
