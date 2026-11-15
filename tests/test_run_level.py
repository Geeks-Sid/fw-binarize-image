from types import SimpleNamespace as NS

from fw_binarize_image.main import run  # noqa: F401  # import must not need a gear config.json
from fw_binarize_image.run_level import get_analysis_run_level_and_hierarchy


def _client(container_type="acquisition"):
    parents = {"group": "grp", "project": "p-id", "subject": "s-id", "session": "ses-id"}
    containers = {
        "acq-id": NS(container_type=container_type, label="acq", parents=parents),
        "p-id": NS(label="proj"),
        "s-id": NS(label="sub"),
        "ses-id": NS(label="ses"),
    }
    return NS(get=containers.__getitem__)


def test_acquisition_hierarchy_labels():
    assert get_analysis_run_level_and_hierarchy(_client(), "acq-id") == {
        "group": "grp",
        "project_label": "proj",
        "subject_label": "sub",
        "session_label": "ses",
        "acquisition_label": "acq",
    }
