# SDK gear to binarize an image

This gear creates a binary image of an input image.
Any voxel > 0 is assigned a value of 1.

Saves to a 'processed' acquisition in the same session as the input files.

## Usage

Run at the file-level.

### Inputs

* input-file: Input file to process (nifti)

### Configuration

* __debug__ (boolean, default False): Include debug statements in output.

### Limitations
