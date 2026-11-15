import nibabel as nib
import numpy as np

def binarize_im(im):
    """
    Binarize a NIfTI image.
    
    Parameters:
    im (str): Path to the NIfTI image.
    
    Returns:
    nib.Nifti1Image: Binarized image.
    """
    img = nib.load(im)
    data = img.get_fdata()
    
    # Binarize the data
    binary_data = (data > 0).astype(np.uint8)
    
    # Create a new NIfTI image with the binary data
    binary_img = nib.Nifti1Image(binary_data, img.affine, img.header)
    # the copied header still describes the source data: force uint8 and its 0..1 display range
    binary_img.set_data_dtype(np.uint8)
    binary_img.header["cal_min"] = 0
    binary_img.header["cal_max"] = 1
    
    return binary_img
