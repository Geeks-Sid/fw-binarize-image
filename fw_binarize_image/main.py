import logging
import os
import re
import tempfile

import flywheel
from flywheel_gear_toolkit import GearToolkitContext
from .run_level import get_analysis_run_level_and_hierarchy

from .im_functions import binarize_im
import nibabel as nib

log = logging.getLogger(__name__)


def run(gtk_context: GearToolkitContext):
    """Main entrypoint

    Args:
        gtk_context (GearToolkitContext)
    """
    fw = gtk_context.client
    # get the Flywheel hierarchy for the run
    destination_id = gtk_context.destination["id"]
    hierarchy = get_analysis_run_level_and_hierarchy(fw, destination_id)
    acq_label = hierarchy['acquisition_label']
    sub_label = hierarchy['subject_label']
    ses_label = hierarchy['session_label']
    project_label = hierarchy['project_label']
    group_name = hierarchy['group']

    # get the output acqusition container
    output_acq_label = 'processed'
    session_path = f'{group_name}/{project_label}/{sub_label}/{ses_label}'
    try:
        acq = fw.lookup(f'{session_path}/{output_acq_label}')
    except flywheel.ApiException as e:
        if e.status != 404:
            raise
        # if the acquisition does not exist, create it
        session = fw.lookup(session_path)
        acq = session.add_acquisition(label=output_acq_label)
        log.info(f'Created new acquisition: {acq.id}')
    acq = acq.reload()

    # get the input file
    im1_file_path = gtk_context.get_input_path("input-file")

    # default name derives from the input so several inputs in one session don't overwrite each other
    default_fn = re.sub(r"\.nii(\.gz)?$", "", gtk_context.get_input_filename("input-file")) + "_bin.nii.gz"
    out_fn = gtk_context.config.get("output-filename") or default_fn
    if os.path.basename(out_fn) != out_fn or not out_fn.endswith((".nii", ".nii.gz")):
        raise ValueError(
            f"output-filename must be a plain file name ending in .nii or .nii.gz, got {out_fn!r}"
        )

    log.info(f'Processing file: {im1_file_path}')

    out_im = binarize_im(im1_file_path)

    with tempfile.TemporaryDirectory() as tmp_dir:
        out_path = os.path.join(tmp_dir, out_fn)
        nib.save(out_im, out_path)

        # upload to acquisition in the same session (the uploaded name is the file basename)
        acq.upload_file(out_path)
    return 0
