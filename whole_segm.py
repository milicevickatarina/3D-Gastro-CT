# -*- coding: utf-8 -*-
"""
Created on Wed Apr 28 11:37:27 2021

@author: Katarina Milicevic, School of Electrical Engineering

Preparing all for rendering
"""
import SimpleITK as sitk
import numpy as np


def main(main_dir):
    
    img = sitk.ReadImage(main_dir + "/data/portal_vein_phase_preprocessed.mha")
    img_array = sitk.GetArrayFromImage(img)
    # Merging segmentation results
    try:
        heart_sitk = sitk.ReadImage(main_dir + "/segmentation results/heart.mhd")
        heart_array = sitk.GetArrayFromImage(heart_sitk)
    except:
        heart_array = np.zeros(img_array.shape, dtype = np.uint8)    
    try:    
        bones_sitk = sitk.ReadImage(main_dir + "/segmentation results/bones.mhd")
        bones_array = sitk.GetArrayFromImage(bones_sitk)
    except:
        bones_array = np.zeros(img_array.shape, dtype = np.uint8)
    try:
        liver_sitk = sitk.ReadImage(main_dir + "/segmentation results/liver_and_spleen.mhd")
        liver_array = sitk.GetArrayFromImage(liver_sitk)
    except:
        liver_array = np.zeros(img_array.shape, dtype = np.uint8)
    try:   
        kidney_sitk = sitk.ReadImage(main_dir + "/segmentation results/right_kidney.mhd")
        kidney_array = sitk.GetArrayFromImage(kidney_sitk)
    except:
        kidney_array = np.zeros(img_array.shape, dtype = np.uint8)
    try:
        kidney2_sitk = sitk.ReadImage(main_dir + "/segmentation results/left_kidney.mhd")
        kidney2_array = sitk.GetArrayFromImage(kidney2_sitk)
    except:
        kidney2_array = np.zeros(img_array.shape, dtype = np.uint8) 
    try:
        stone_sitk = sitk.ReadImage(main_dir + "/segmentation results/stone.mhd")
        stone_array = sitk.GetArrayFromImage(stone_sitk)
    except:
        stone_array = np.zeros(img_array.shape, dtype = np.uint8) 
   
    whole_segm = heart_array + bones_array*2 + liver_array*3 + (kidney_array +  kidney2_array)*4 + stone_array*5
    
    # Rotation of axial slices around y-axis
    X_for_mirror = np.transpose(whole_segm, (0,2,1))
    X_mirrored = X_for_mirror[::-1]
    whole_segm_mirror = np.transpose(X_mirrored,(0,2,1))
    
    # Image saving
    whole_segm_sitk = sitk.GetImageFromArray(whole_segm_mirror)
    whole_segm_sitk.SetSpacing(heart_sitk.GetSpacing())
    sitk.WriteImage(whole_segm_sitk, main_dir + "/segmentation results/whole_segmentation.mhd")