# -*- coding: utf-8 -*-
"""
Created on Mon Apr 19 16:07:38 2021

@author: Katarina Milicevic, School of Electrical Engineering

Heart segmentation
"""
import SimpleITK as sitk
import numpy as np
import os
import matplotlib.pyplot as plt
import scipy.ndimage as ndi


def first_slice_segm(main_dir, x_left=105, x_right=170, y_top=64, y_bottom=136):
    img = sitk.ReadImage(main_dir + "/data/portal_vein_phase_preprocessed.mha")
    
    first_slice = img[:,:,0]

    gaussian = sitk.SmoothingRecursiveGaussianImageFilter()
    gaussian.SetSigma(2.0)
    filt_slice = gaussian.Execute(first_slice)
    filt_slice_array = sitk.GetArrayFromImage(filt_slice)
    
    hist = ndi.histogram(filt_slice_array, min=0, max=255, bins=256)
    sum = hist.sum()
    per10 = round(sum/10)
    num = 0
    for i in range(len(hist)-1,-1,-1):
        num = num + hist[i]
        if num >= per10:
            th = i
            break
        
    first_slice_segm = np.zeros(filt_slice_array.shape)
    first_slice_segm[y_top:y_bottom+1, x_left:x_right+1] = (filt_slice_array>th)[y_top:y_bottom+1, x_left:x_right+1]
    
    # Fill holes
    fill_objects = ndi.binary_fill_holes(first_slice_segm)
    # Remove small objects
    label_objects, nb_labels = ndi.label(fill_objects)
    sizes = np.bincount(label_objects.ravel())
    mask_sizes = sizes > 20
    mask_sizes[0] = 0
    first_slice_segm = mask_sizes[label_objects]
    
    fig, ax = plt.subplots(1, 1)
    fig.canvas.set_window_title('Figure')
    ax.imshow(first_slice_segm, cmap='gray')
    ax.set_title('First slice segmentation')
  
    
def show_heart_box(main_dir, x_left, x_right, y_top, y_bottom, z_bottom):
    img = sitk.ReadImage(main_dir + "/data/portal_vein_phase_preprocessed.mha")
    img_array = sitk.GetArrayFromImage(img)
    
    heart_box = img_array[0:z_bottom, y_top:y_bottom+1, x_left:x_right+1]
    
    return heart_box


def main(main_dir, x_left=105, x_right=170, y_top=64, y_bottom=136, bl=70, br=190, bt=10, bb=190, bz=95):
    img = sitk.ReadImage(main_dir + "/data/portal_vein_phase_preprocessed.mha")
    dims = img.GetSize()
    first_slice = img[:,:,0]
    first_slice_array = sitk.GetArrayFromImage(first_slice)
    heart_box = first_slice_array[y_top:y_bottom+1, x_left:x_right+1]
    
    gaussian = sitk.SmoothingRecursiveGaussianImageFilter()
    gaussian.SetSigma(2.0)
    filt_slice = gaussian.Execute(first_slice)
    filt_slice_array = sitk.GetArrayFromImage(filt_slice)

    hist = ndi.histogram(filt_slice_array, min=0, max=255, bins=256)
    sum = hist.sum()
    per10 = round(sum/10)
    num = 0
    for i in range(len(hist)-1,-1,-1):
        num = num + hist[i]
        if num >= per10:
            th = i
            break
        
    first_slice_segm = np.zeros(filt_slice_array.shape)
    first_slice_segm[y_top:y_bottom+1, x_left:x_right+1] = (filt_slice_array>th)[y_top:y_bottom+1, x_left:x_right+1]
    
    # Fill holes
    fill_objects = ndi.binary_fill_holes(first_slice_segm)
    # Remove small objects
    label_objects, nb_labels = ndi.label(fill_objects)
    sizes = np.bincount(label_objects.ravel())
    mask_sizes = sizes > 20
    mask_sizes[0] = 0
    first_slice_segm = mask_sizes[label_objects]
 
    z_bottom = bz
    x_left =bl
    x_right = br
    y_top = bt
    y_bottom = bb
    
    heart_box = np.zeros(first_slice_array.shape, np.uint8)
    heart_box[y_top:y_bottom+1, x_left:x_right+1] = np.ones((y_bottom-y_top+1, x_right-x_left+1))
    
    def slice_process(slice, prev):
        filt_slice = gaussian.Execute(slice)
        filt_slice_array = sitk.GetArrayFromImage(filt_slice)
        hist = ndi.histogram(filt_slice_array, min=0, max=255, bins=256)
        sum = hist.sum()
        per10 = round(sum/10)
        num = 0
        for i in range(len(hist)-1,-1,-1):
            num = num + hist[i]
            if num >= per10:
                th = i
                break
        slice = np.zeros(filt_slice_array.shape)
        slice = (filt_slice_array>th)*prev*heart_box
        # Fill holes
        fill_objects = ndi.binary_fill_holes(slice)
        # Remove small objects
        label_objects, nb_labels = ndi.label(fill_objects)
        sizes = np.bincount(label_objects.ravel())
        mask_sizes = sizes > 20
        mask_sizes[0] = 0
        slice = mask_sizes[label_objects]
        if slice.sum() < 0.3*prev.sum():
            return slice, 1
        return slice, 0
    
    heart = np.zeros((dims[2], dims[1], dims[0]), dtype='uint8')
    heart[0,:,:] = first_slice_segm
    prev_slice = ndi.binary_dilation(first_slice_segm)
    for z in range(1, z_bottom+1):
        cur_slice, f = slice_process(img[:,:,z], prev_slice)
        heart[z,:,:] = cur_slice
        if f:
            break
        if z < int(z_bottom*4/5):
            prev_slice = ndi.binary_dilation(cur_slice,iterations=1)
        else:
            prev_slice = cur_slice
            
    heart_sitk = sitk.GetImageFromArray(heart)
    heart_sitk.SetSpacing(img.GetSpacing())
    cleaned_thresh_img = sitk.BinaryOpeningByReconstruction(heart_sitk, [10, 10, 10])
    heart_sitk = sitk.BinaryClosingByReconstruction(cleaned_thresh_img, [10, 10, 10])
    
    # Image saving
    segm_dir = os.path.join(main_dir, "segmentation results")
    if not os.path.exists(segm_dir):
        os.makedirs(segm_dir)
    sitk.WriteImage(heart_sitk, segm_dir + "/heart.mhd")