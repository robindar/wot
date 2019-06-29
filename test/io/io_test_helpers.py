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
