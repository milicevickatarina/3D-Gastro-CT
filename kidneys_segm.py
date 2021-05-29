# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 15:22:29 2021

@author: Katarina Milicevic, School of Electrical Engineering

Kidneys segmentation
"""
import SimpleITK as sitk
import numpy as np
import os
import scipy.ndimage as ndi


def show_hist(main_dir, x_left, x_right, y_top, y_bottom, z_top, z_bottom):
    try:
        img = sitk.ReadImage(main_dir + "/data/portal_vein_phase_preprocessed.mha")
        img_array = sitk.GetArrayFromImage(img)
        heart_sitk = sitk.ReadImage(main_dir + "/segmentation results/heart.mhd")
        heart_array = sitk.GetArrayFromImage(heart_sitk)
        bones_sitk = sitk.ReadImage(main_dir + "/segmentation results/bones.mhd")
        bones_array = sitk.GetArrayFromImage(bones_sitk)
        liver_sitk = sitk.ReadImage(main_dir + "/segmentation results/liver_and_spleen.mhd")
        liver_array = sitk.GetArrayFromImage(liver_sitk)
        heart_bones_liver = heart_array | bones_array | liver_array
        only_kidneys = np.where(heart_bones_liver==0, img_array, 0)
        
        only_kidneys_box = only_kidneys[z_top:z_bottom, y_top:y_bottom+1, x_left:x_right+1]
        kidneys_hist = ndi.histogram(only_kidneys_box, min=0, max=255, bins=256)
    
        kidney_box = img_array[z_top:z_bottom+1, y_top:y_bottom+1, x_left:x_right+1]
        status = 1
    except:
        status = 0
    
    return kidney_box, kidneys_hist, status


# Right kidney segmentation (left on pictures) 
def right_kidney(main_dir, Gmin, Gmax, x_left, x_right, y_top, y_bottom, z_top, z_bottom): # vidi hoces podrazumevane
    try:
        img = sitk.ReadImage(main_dir + "/data/portal_vein_phase_preprocessed.mha")
        img_array = sitk.GetArrayFromImage(img)
        
        heart_sitk = sitk.ReadImage(main_dir + "/segmentation results/heart.mhd")
        heart_array = sitk.GetArrayFromImage(heart_sitk)
        bones_sitk = sitk.ReadImage(main_dir + "/segmentation results/bones.mhd")
        bones_array = sitk.GetArrayFromImage(bones_sitk)
        liver_sitk = sitk.ReadImage(main_dir + "/segmentation results/liver_and_spleen.mhd")
        liver_array = sitk.GetArrayFromImage(liver_sitk)
        heart_bones_liver = heart_array | bones_array | liver_array
        only_kidneys = np.where(heart_bones_liver==0, img_array, 0)
        
        bin_im = (only_kidneys<Gmax)*(only_kidneys>Gmin)
        
        kidney = np.zeros(only_kidneys.shape, dtype = 'uint8')
        for z in range(z_top, z_bottom+1):
            kidney[z, y_top:y_bottom+1, x_left:x_right+1] = bin_im[z, y_top:y_bottom+1, x_left:x_right+1]
           
        kidney_sitk = sitk.GetImageFromArray(kidney)
        kidney_sitk.SetSpacing(img.GetSpacing())
        cleaned_thresh_img = sitk.BinaryOpeningByReconstruction(kidney_sitk, [4, 4, 4])
        kidney_sitk = sitk.BinaryClosingByReconstruction(cleaned_thresh_img, [4, 4, 4])
        
        print("Segmentacija je zavrsena")
        
        segm_dir = os.path.join(main_dir, "segmentation results")
        if not os.path.exists(segm_dir):
            os.makedirs(segm_dir)
        
        sitk.WriteImage(kidney_sitk, segm_dir + "/right_kidney.mhd")
        status = 1
    except:
        status = 0
    
    return status
 
    
# Left kidney segmentation (right on pictures)   
def left_kidney(main_dir, Gmin, Gmax, x_left = 155, x_right = 220, y_top = 110, y_bottom = 180, z_top = 80, z_bottom = 290):   
    try:
        img = sitk.ReadImage(main_dir + "/data/portal_vein_phase_preprocessed.mha")
        img_array = sitk.GetArrayFromImage(img)
        
        heart_sitk = sitk.ReadImage(main_dir + "/segmentation results/heart.mhd")
        heart_array = sitk.GetArrayFromImage(heart_sitk)
        bones_sitk = sitk.ReadImage(main_dir + "/segmentation results/bones.mhd")
        bones_array = sitk.GetArrayFromImage(bones_sitk)
        liver_sitk = sitk.ReadImage(main_dir + "/segmentation results/liver_and_spleen.mhd")
        liver_array = sitk.GetArrayFromImage(liver_sitk)
        heart_bones_liver = heart_array | bones_array | liver_array
        only_kidneys = np.where(heart_bones_liver==0, img_array, 0)
    
        bin_im = (only_kidneys<Gmax)*(only_kidneys>Gmin)
        
        kidney2 = np.zeros(only_kidneys.shape, dtype = 'uint8')
        for z in range(z_top, z_bottom+1):
            kidney2[z, y_top:y_bottom+1, x_left:x_right+1] = bin_im[z, y_top:y_bottom+1, x_left:x_right+1]
           
        kidney2_sitk = sitk.GetImageFromArray(kidney2)
        kidney2_sitk.SetSpacing(img.GetSpacing())
        cleaned_thresh_img = sitk.BinaryOpeningByReconstruction(kidney2_sitk, [4, 4, 4])
        kidney2_sitk = sitk.BinaryClosingByReconstruction(cleaned_thresh_img, [4, 4, 4])
        
        print("Segmentacija je zavrsena")
        
        segm_dir = os.path.join(main_dir, "segmentation results")
        if not os.path.exists(segm_dir):
            os.makedirs(segm_dir)
        
        sitk.WriteImage(kidney2_sitk, segm_dir + "/left_kidney.mhd")
        status = 1
    except:
            status = 0
            
    return status