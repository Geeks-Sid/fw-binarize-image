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
    
    return binary_img
