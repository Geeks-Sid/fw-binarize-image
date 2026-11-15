import os
from types import SimpleNamespace as NS

import nibabel as nib
import numpy as np
import pytest
from flywheel import ApiException

from fw_binarize_image.main import run


class FakeAcquisition:
    """Records uploads; upload_file is as strict as the SDK's unsigned upload (no `name` kwarg)."""

    id = "out-acq-id"

    def __init__(self):
        self.uploads = []

    def reload(self):
        return self

    def upload_file(self, file):
        img = nib.load(file)  # the file must exist and be valid at upload time
        self.uploads.append(
            (os.path.basename(file), img.get_data_dtype(), np.asanyarray(img.dataobj))
        )


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "output").mkdir()  # the gear platform provides ./output

    in_path = str(tmp_path / "sub-01_T1w.nii.gz")
    nib.save(
        nib.Nifti1Image(np.array([[[-1.0, 0.0, 2.0]]], dtype=np.float32), np.eye(4)), in_path
    )

    containers = {
        "acq-id": NS(
            container_type="acquisition",
            label="T1w",
            parents={"group": "grp", "project": "p-id", "subject": "s-id", "session": "ses-id"},
        ),
        "p-id": NS(label="proj"),
        "s-id": NS(label="sub"),
        "ses-id": NS(label="ses"),
    }
    acq = FakeAcquisition()
    client = NS(get=containers.__getitem__, lookup=lambda path: acq)
    ctx = NS(
        client=client,
        destination={"id": "acq-id"},
        config={},
        get_input_path=lambda name: in_path,
    )
    return NS(ctx=ctx, acq=acq, tmp_path=tmp_path)


def test_binarizes_and_uploads_with_default_name(env):
    assert run(env.ctx) == 0

    [(name, dtype, data)] = env.acq.uploads
    assert name == "sub_ses_bin.nii.gz"
    assert dtype == np.uint8
    np.testing.assert_array_equal(data, [[[0, 0, 1]]])


def test_output_filename_config_is_used(env):
    env.ctx.config = {"output-filename": "mask.nii.gz"}
    run(env.ctx)
    assert env.acq.uploads[0][0] == "mask.nii.gz"


def test_empty_output_filename_falls_back_to_default(env):
    env.ctx.config = {"output-filename": ""}
    run(env.ctx)
    assert env.acq.uploads[0][0] == "sub_ses_bin.nii.gz"


def _lookup_with_missing_output(error, session):
    def lookup(path):
        if path.endswith("/processed"):
            raise error
        return session

    return lookup


def test_missing_processed_acquisition_is_created(env):
    created = FakeAcquisition()
    session = NS(add_acquisition=lambda label: created if label == "processed" else None)
    env.ctx.client.lookup = _lookup_with_missing_output(ApiException(status=404), session)

    run(env.ctx)

    assert len(created.uploads) == 1


def test_lookup_errors_other_than_not_found_propagate(env):
    def add_acquisition(label):
        raise AssertionError("must not create an acquisition on a non-404 error")

    session = NS(add_acquisition=add_acquisition)
    env.ctx.client.lookup = _lookup_with_missing_output(ApiException(status=500), session)

    with pytest.raises(ApiException):
        run(env.ctx)
