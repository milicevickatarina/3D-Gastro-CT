# -*- coding: utf-8 -*-
"""
Created on Wed Apr 21 12:33:56 2021

@author: Katarina Milicevic, School of Electrical Engineering

Bones segmentation
"""
import SimpleITK as sitk
import os
import scipy.ndimage as ndi
import numpy as np


def show_hist(main_dir):
    img_native = sitk.ReadImage(main_dir + "/data/native_phase_preprocessed.mha")
    img_native_array = sitk.GetArrayFromImage(img_native)

    min_hist = img_native_array.min()
    max_hist = img_native_array.max()
    volume_hist = ndi.histogram(img_native_array, min=min_hist, max=max_hist, bins=max_hist-min_hist+1)

    return volume_hist


def main(main_dir, thres = 118, thres2 = 250):
    img = sitk.ReadImage(main_dir + "/data/portal_vein_phase_preprocessed.mha")
    img_native = sitk.ReadImage(main_dir + "/data/native_phase_preprocessed.mha")
    img_native_array = sitk.GetArrayFromImage(img_native)
    
    bin_im1 = np.array(img_native_array>thres, dtype = 'uint8')
    bin_im2 = np.array(img_native_array<thres2, dtype = 'uint8')
    bones = bin_im1 & bin_im2
    
    bones_sitk = sitk.GetImageFromArray(bones)
    bones_sitk.SetSpacing(img.GetSpacing())
    bones_sitk = sitk.Cast(bones_sitk, sitk.sitkUInt8)
    cleaned_thresh_img = sitk.BinaryOpeningByReconstruction(bones_sitk, [3, 3, 3])
    bones_sitk = sitk.BinaryClosingByReconstruction(cleaned_thresh_img, [3, 3, 3])
    
    segm_dir = os.path.join(main_dir, "segmentation results")
    if not os.path.exists(segm_dir):
        os.makedirs(segm_dir)
    
    sitk.WriteImage(bones_sitk, segm_dir + "/bones.mhd")