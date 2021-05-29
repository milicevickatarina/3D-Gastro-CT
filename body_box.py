# -*- coding: utf-8 -*-
"""
Created on Sat Sep 12 20:34:28 2020

@author: Katarina Milicevic, School of Electrical Engineering

function for determining body boundaries based on gray level
"""
import SimpleITK as sitk


def body_box_boundaries(image):
    binary_image = image > -1500
    filter = sitk.ConnectedComponentImageFilter()
    objects = filter.Execute(binary_image)
    sorting = sitk.RelabelComponentImageFilter()
    sorted = sorting.Execute(objects)
    body_region = sorted == 1
    count_distance = sitk.ApproximateSignedDistanceMapImageFilter()
    distance = count_distance.Execute(body_region)
    
    distances = sitk.GetArrayFromImage(distance)
    distances = abs(distances)
    distances = distances.astype('uint8')
    z, x, y = distances.shape
    x1 = distances[:,:,0].min()
    x2 = x - distances[:,:,x-1].min()
    y1 = distances[:,0,:].min()
    y2 = y - distances[:,y-1,:].min()
    
    return x1, x2, y1, y2