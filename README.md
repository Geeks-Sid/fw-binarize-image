# SDK gear to binarize an image

This gear creates a binary image of an input image.
Any voxel > 0 is assigned a value of 1. The output is a `uint8` NIfTI.

Saves to a 'processed' acquisition in the same session as the input files
(created if it does not exist).

## Usage

Run at the file-level, on a file in an acquisition.

### Inputs

* input-file: Input file to process (nifti)

### Configuration

* __output-filename__ (string, optional): Name of the output file. Must be a
  plain file name ending in `.nii` or `.nii.gz`. Default: the input file name
  with `.nii`/`.nii.gz` replaced by `_bin.nii.gz`. A file with the same name in
  'processed' is replaced, so set this if inputs from different acquisitions
  of one session share a file name.
* __debug__ (boolean, default False): Include debug statements in output.

### Limitations

* The gear must run on an acquisition; any other destination fails.

## Development

```
pip install -r requirements-dev.txt
pytest
```
