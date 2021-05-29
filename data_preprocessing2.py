# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 16:28:55 2021

@author: Katarina Milicevic, School of Electrical Engineering

Native phase preprocessing
"""
import SimpleITK as sitk
import numpy as np
import os


def main(arg, main_dir):
    files = os.listdir(arg)
    try:
        if len(files) == 1: # Whole series in a file
            filePath = os.path.join(arg, files[0])
            img = sitk.ReadImage(filePath)
        else:
            # Series in separated 2D slices
            img1 =[]
            for (dirpath, dirnames, filenames) in os.walk(arg):
                for filename in filenames:
                    image = sitk.ReadImage(arg+'/'+filename)
                    num_slices = image.GetDepth()
                    tile_w = int(np.sqrt(num_slices))
                    tile_h = int(np.ceil(num_slices/tile_w))
                    tile_image = sitk.Tile([image[:,:,i] for i in range(num_slices)], (tile_w, tile_h))
                    img1.append(tile_image)
        
            img = sitk.JoinSeries(img1)
            img.SetSpacing([1, tile_image.GetSpacing()[0], tile_image.GetSpacing()[1]])
    except:
        return 0, 0
      
    # Rescaling intensity
    Hmin = -548
    Hmax = 800
    img_255 = sitk.Cast(sitk.IntensityWindowing(img, windowMinimum=Hmin, windowMaximum=Hmax, 
                                                 outputMinimum=0.0, outputMaximum=255.0), sitk.sitkUInt8)
    
    # Resampling (down_sampling_factor = 2)
    new_x_size = 256
    new_y_size = 256
    new_z_size = img_255.GetSize()[2]
    new_size = [new_x_size, new_y_size, new_z_size]
    new_spacing = [old_sz*old_spc/new_sz  for old_sz, old_spc, new_sz in zip(img_255.GetSize(), img_255.GetSpacing(), new_size)]
    interpolator_type = sitk.sitkLinear
    new_img = sitk.Resample(img_255, new_size, sitk.Transform(), interpolator_type, img_255.GetOrigin(), new_spacing, img_255.GetDirection(), 0.0, img_255.GetPixelIDValue())
    
    # Median filtering
    med_filt = sitk.MedianImageFilter()
    med_filt.SetRadius(1)
    filt_img = med_filt.Execute(new_img)
    
    fixed_image_path = os.path.join(main_dir, 'data/portal_vein_phase_preprocessed.mha')
    fixed_image =  sitk.ReadImage(fixed_image_path, sitk.sitkFloat32)
    
    if (filt_img.GetSize() == fixed_image.GetSize()): # Checking if there is need for corregistration
        # Image saving
        sitk.WriteImage(filt_img, os.path.join(main_dir, "data/native_phase_preprocessed.mha"))
        img_array = sitk.GetArrayFromImage(filt_img)
        
    else:
        # Corregistration
        moving_image = sitk.Cast(filt_img, sitk.sitkFloat32)
        initial_transform = sitk.CenteredTransformInitializer(fixed_image, 
                                                              moving_image, 
                                                              sitk.Euler3DTransform(), 
                                                              sitk.CenteredTransformInitializerFilter.GEOMETRY)
        moving_resampled = sitk.Resample(moving_image, fixed_image, initial_transform, sitk.sitkLinear, 0.0, moving_image.GetPixelID())
        registration_method = sitk.ImageRegistrationMethod()
        
        # Similarity metric settings
        registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins=50)
        registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
        registration_method.SetMetricSamplingPercentage(0.01)
        registration_method.SetInterpolator(sitk.sitkLinear)
        
        # Optimizer settings
        registration_method.SetOptimizerAsGradientDescent(learningRate=1.0, numberOfIterations=100, convergenceMinimumValue=1e-6, convergenceWindowSize=10)
        registration_method.SetOptimizerScalesFromPhysicalShift()
        
        # Setup for the multi-resolution framework         
        registration_method.SetShrinkFactorsPerLevel(shrinkFactors = [4,2,1])
        registration_method.SetSmoothingSigmasPerLevel(smoothingSigmas=[2,1,0])
        registration_method.SmoothingSigmasAreSpecifiedInPhysicalUnitsOn()
        registration_method.SetInitialTransform(initial_transform, inPlace=False)
        
        final_transform = registration_method.Execute(sitk.Cast(fixed_image, sitk.sitkFloat32), 
                                                        sitk.Cast(moving_image, sitk.sitkFloat32))
        moving_resampled = sitk.Resample(moving_image, fixed_image, final_transform, sitk.sitkLinear, 0.0, moving_image.GetPixelID())
        casted = sitk.Cast(moving_resampled, sitk.sitkInt16)
        
        # Image saving
        sitk.WriteImage(casted, os.path.join(main_dir, "data/native_phase_preprocessed.mha"))
        img_array = sitk.GetArrayFromImage(casted)
        
    return img_array, 1