import nibabel as nib
import numpy as np
import pytest

from fw_binarize_image.im_functions import binarize_im


def _save(tmp_path, data, name="in.nii.gz", slope_inter=None):
    img = nib.Nifti1Image(data, np.diag([2.0, 2.0, 2.0, 1.0]))
    img.header["cal_max"] = 300
    if slope_inter:
        img.header.set_slope_inter(*slope_inter)
    path = str(tmp_path / name)
    nib.save(img, path)
    return path


@pytest.mark.parametrize("name", ["in.nii", "in.nii.gz"])
def test_values_and_roundtrip_dtype(tmp_path, name):
    data = np.array([[[-3.5, 0.0, 0.1], [np.nan, 250.0, -0.0]]], dtype=np.float32)
    out = binarize_im(_save(tmp_path, data, name))

    out_path = str(tmp_path / ("out_" + name))
    nib.save(out, out_path)
    saved = nib.load(out_path)

    assert saved.get_data_dtype() == np.uint8
    np.testing.assert_array_equal(np.asanyarray(saved.dataobj), [[[0, 0, 1], [0, 1, 0]]])
    np.testing.assert_array_equal(saved.affine, np.diag([2.0, 2.0, 2.0, 1.0]))
    # source display range (300) must not leak into a 0/1 mask
    assert saved.header["cal_max"] == 1


def test_scaled_integer_input_uses_scaled_values(tmp_path):
    # stored ints -5,0,3,7 with slope 0.5 / inter -2 -> real values -4.5,-2,-0.5,1.5
    data = np.array([[[-5, 0, 3, 7]]], dtype=np.int16)
    out = binarize_im(_save(tmp_path, data, slope_inter=(0.5, -2.0)))

    np.testing.assert_array_equal(np.asanyarray(out.dataobj), [[[0, 0, 0, 1]]])
