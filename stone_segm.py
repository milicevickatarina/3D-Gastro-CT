# -*- coding: utf-8 -*-
"""
Created on Wed Apr 28 10:45:12 2021

@author: Katarina Milicevic, School of Electrical Engineering

Stone segmentation
"""
import SimpleITK as sitk
import numpy as np
import os
from body_box import body_box_boundaries


def main(main_dir, thres=250, thres2=256):
    img = sitk.ReadImage(main_dir + "/data/portal_vein_phase_preprocessed.mha")
    img_array = sitk.GetArrayFromImage(img)
    
    # Define body boundaries (to remove patient bed and other potential background from result)
    x_left, x_right, y_top, y_bottom = body_box_boundaries(img)

    # bin_im = np.array(img_array>thres, dtype = 'uint8')
    bin_im = np.array((img_array<thres2)*(img_array>thres), dtype = 'uint8')
    
    stone = np.zeros(img_array.shape)
    stone[:, y_top:y_bottom+1, x_left:x_right+1] = bin_im[:, y_top:y_bottom+1, x_left:x_right+1]
    
    stone_sitk = sitk.GetImageFromArray(stone)
    stone_sitk.SetSpacing(img.GetSpacing())
    stone_sitk = sitk.Cast(stone_sitk, sitk.sitkUInt8)
    cleaned_thresh_img = sitk.BinaryOpeningByReconstruction(stone_sitk, [3, 3, 3])
    stone_sitk = sitk.BinaryClosingByReconstruction(cleaned_thresh_img, [3, 3, 3])
    
    # Image saving
    segm_dir = os.path.join(main_dir, "segmentation results")
    if not os.path.exists(segm_dir):
        os.makedirs(segm_dir)
    sitk.WriteImage(stone_sitk, segm_dir + "/stone.mhd")