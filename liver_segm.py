# -*- coding: utf-8 -*-
"""
Created on Wed Apr 21 16:19:07 2021

@author: Katarina Milicevic, School of Electrical Engineering

Liver and spleen segmentation
"""
import SimpleITK as sitk
import numpy as np
import os
import scipy.ndimage as ndi


def show_hist(main_dir):
    img = sitk.ReadImage(main_dir + "/data/portal_vein_phase_preprocessed.mha")
    img_array = sitk.GetArrayFromImage(img)
    
    volume_hist = ndi.histogram(img_array, min=0, max=255, bins=256)

    return volume_hist


def main(main_dir, thres_min = 120, thres_max = 126):
    print("Segmentacija zapocela")
    
    img = sitk.ReadImage(main_dir + "/data/portal_vein_phase_preprocessed.mha")
    img_array = sitk.GetArrayFromImage(img)
    
    z_top = 41 # ...
    z_bottom = 294
    
    try:
        heart_sitk = sitk.ReadImage(main_dir + "/segmentation results/heart.mhd")
        heart_array = sitk.GetArrayFromImage(heart_sitk)
        bones_sitk = sitk.ReadImage(main_dir + "/segmentation results/bones.mhd")
        bones_array = sitk.GetArrayFromImage(bones_sitk)
        heart_spine = heart_array | bones_array
        only_liver_and_spleen = np.where(heart_spine==0, img_array, 0)
        
        bin_im = (only_liver_and_spleen<thres_max)*(only_liver_and_spleen>thres_min)
        liver = np.zeros(only_liver_and_spleen.shape, dtype = 'uint8')
        for z in range(z_top, z_bottom+1):
            liver[z,:,:] = bin_im[z,:,:]
        
        liver_sitk = sitk.GetImageFromArray(liver)
        liver_sitk.SetSpacing(img.GetSpacing())
        cleaned_thresh_img = sitk.BinaryOpeningByReconstruction(liver_sitk, [4, 4, 4])
        filter = sitk.BinaryDilateImageFilter()
        dilated = filter.Execute(cleaned_thresh_img)
        liver_sitk = sitk.BinaryClosingByReconstruction(dilated, [3, 3, 3])
        
        segm_dir = os.path.join(main_dir, "segmentation results")
        if not os.path.exists(segm_dir):
            os.makedirs(segm_dir)
         
        sitk.WriteImage(liver_sitk, segm_dir + "/liver_and_spleen.mhd")
        print("Segmentacija zavrsena")
        return 1
    except:
        return 0