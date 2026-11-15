import logging
import shutil
import json

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
    try:
        acq = fw.lookup(f'{group_name}/{project_label}/{sub_label}/{ses_label}/{output_acq_label}')
        acq = acq.reload()
    except:
        # if the acquisition does not exist, create it
        session = fw.lookup(f'{group_name}/{project_label}/{sub_label}/{ses_label}')
        acq = session.add_acquisition(label=output_acq_label)
        acq = acq.reload()
        log.info(f'Created new acquisition: {acq.id}')

    # get the input file
    CONFIG_FILE_PATH = '/flywheel/v0/config.json'
    with open(CONFIG_FILE_PATH) as config_file:
        config = json.load(config_file)

    im1_file_path = config['inputs']['input-file']['location']['path'] # input path in the gear container

    print(f'Processing file: {im1_file_path}')

    out_im = binarize_im(im1_file_path)

    try:
        out_fn = config['config']['output-filename']
    except:
        out_fn = f'{sub_label}_{ses_label}_bin.nii.gz'
    out_path = f'output/{out_fn}'
    nib.save(out_im, out_path)

    # upload to acquisition in the same session
    acq.upload_file(out_path, name=out_fn)

    # remove temp files
    shutil.rmtree('output', ignore_errors=True)
    return 0
