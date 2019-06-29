from .io_test_helpers import *
from .hardcoded_small import *


def test_read_day_pairs_from_file():
    expected_pairs = hardcoded_small_day_pairs()
    read_pairs = wot.io.read_day_pairs("test/resources/small/day_pairs.txt")
    assert_pd_frame_equal(read_pairs, expected_pairs)

def test_read_day_pairs_from_string():
    pairs_string = "t0,t1,lambda1;1,2,50;2,3,80;1,3,10"
    expected_pairs = hardcoded_small_day_pairs()
    read_pairs = wot.io.read_day_pairs(pairs_string)
    assert_pd_frame_equal(read_pairs, expected_pairs)

def test_row_metadata_completion_errors():
    dataset = hardcoded_small_ds()
    for file_param in [ "days", "growth_rates", "covariate" ]:
        kwargs = { file_param: "nonexistent.txt" }
        with pytest.raises(ValueError):
            wot.io.add_row_metadata_to_dataset(dataset, **kwargs)

def test_row_metadata_completion_default_growth_rates():
    dataset = hardcoded_small_ds()
    wot.io.add_row_metadata_to_dataset(dataset)
    assert (dataset.obs['cell_growth_rate'] == 1.).all()

def test_row_metadata_completion():
    dataset = hardcoded_small_ds()
    wot.io.add_row_metadata_to_dataset(dataset,
            days="test/resources/small/days.txt",
            growth_rates="test/resources/small/growth_rates.txt",
            covariate="test/resources/small/covariate.txt")
    expected_dataset = hardcoded_small_ds_with_metadata()
    assert_anndata_equal(dataset, expected_dataset)

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
            [ "file.grp.txt", "grp", "file.grp.txt.grp" ],
            [ "normalcase.loom", "loOm", "normalcase.loom.loOm" ],
            ]
    for filename, extension, result in test_cases:
        assert wot.io.check_file_extension(filename, extension) == result
