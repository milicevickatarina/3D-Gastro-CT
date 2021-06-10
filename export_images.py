# -*- coding: utf-8 -*-
"""
Created on Thu Jun 10 17:28:56 2021

@author: Kaca
"""
import vtk
import os

def main(fileName, main_dir):
                                                
    exp_dir = os.path.join(main_dir, "export")
    if not os.path.exists(exp_dir):
        os.makedirs(exp_dir)
    
    colors = vtk.vtkNamedColors()

    organsMap = CreateOrgansMap()
    colorLut = CreateColorLut()

    # Setup render window, renderer, and interactor.
    renderer = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)
    
    appendPolydata = vtk.vtkAppendPolyData() 

    # Use this to ensure that the organs are selected in this order.
    organs = [
    'heart',
    'bones',
    'liver and spleen',
    'kidneys',
    'stone'
]

    for i in range(0, len(organs)):
        actor, normals = CreateOrganActor(fileName, organsMap[organs[i]])
        actor.GetProperty().SetDiffuseColor(colorLut.GetTableValue(organsMap[organs[i]])[:3])
        actor.GetProperty().SetSpecular(.5)
        actor.GetProperty().SetSpecularPower(10)
        renderer.AddActor(actor)
        # Collect data for stl
        appendPolydata.AddInputConnection(normals.GetOutputPort())

    # Save to stl
    stlWriter = vtk.vtkSTLWriter()
    stlWriter.SetInputConnection(appendPolydata.GetOutputPort())
    stlWriter.SetFileName(exp_dir + "/Test_jun.stl")
    stlWriter.Write()

    # renderer.GetActiveCamera().SetViewUp(0, 0, 1)
    # renderer.GetActiveCamera().SetPosition(0, 1, 0)

    # renderer.GetActiveCamera().Azimuth(210)
    renderer.GetActiveCamera().Elevation(-90)
    renderer.ResetCamera()
    renderer.ResetCameraClippingRange()
    # renderer.GetActiveCamera().Dolly(1.5)
    renderer.SetBackground(colors.GetColor3d("white"))

    renderWindow.SetSize(800, 800)
    renderWindow.Render()

    # Save first window view to jpg
    vtk_win_im = vtk.vtkWindowToImageFilter()
    vtk_win_im.SetInput(renderWindow)
    vtk_win_im.Update()
    
    vtk_image = vtk_win_im.GetOutput()
    
    writer = vtk.vtkJPEGWriter()
    writer.SetInputData(vtk_image)
    writer.SetFileName(exp_dir + "/pacijent1.jpg")
    writer.Write()
    
    # renderWindowInteractor.Start()


def get_program_parameters():
    import argparse
    description = 'Kidneys with some other abdominal organs'
    epilogue = '''
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='organs.mhd.')
    args = parser.parse_args()
    return args.filename


def CreateColorLut():
    colors = vtk.vtkNamedColors()

    colorLut = vtk.vtkLookupTable()
    colorLut.SetNumberOfColors(6)
    colorLut.SetTableRange(0, 5)
    colorLut.Build()

    colorLut.SetTableValue(0, 0, 0, 0, 0)
    colorLut.SetTableValue(1, colors.GetColor4d("red"))
    colorLut.SetTableValue(2, colors.GetColor4d("wheat"))
    colorLut.SetTableValue(3, colors.GetColor4d("darkred"))
    colorLut.SetTableValue(4, colors.GetColor4d("cadmium_orange"))
    colorLut.SetTableValue(5, colors.GetColor4d("lightslategray"))

    return colorLut


def CreateOrgansMap():
    organMap = dict()
    organMap["heart"] = 1
    organMap["bones"] = 2
    organMap["liver and spleen"] = 3
    organMap["kidneys"] = 4
    organMap["stone"] = 5

    return organMap


def CreateOrganActor(fileName, organ):
    reader = vtk.vtkMetaImageReader()
    reader.SetFileName(fileName)
    reader.Update()

    selectorgan = vtk.vtkImageThreshold()
    selectorgan.ThresholdBetween(organ, organ)
    selectorgan.SetInValue(255)
    selectorgan.SetOutValue(0)
    selectorgan.SetInputConnection(reader.GetOutputPort())

    gaussianRadius = 1
    gaussianStandardDeviation = 2.0
    gaussian = vtk.vtkImageGaussianSmooth()
    gaussian.SetStandardDeviations(gaussianStandardDeviation, gaussianStandardDeviation, gaussianStandardDeviation)
    gaussian.SetRadiusFactors(gaussianRadius, gaussianRadius, gaussianRadius)
    gaussian.SetInputConnection(selectorgan.GetOutputPort())

    isoValue = 127.5
    mcubes = vtk.vtkMarchingCubes()
    mcubes.SetInputConnection(gaussian.GetOutputPort())
    mcubes.ComputeScalarsOff()
    mcubes.ComputeGradientsOff()
    mcubes.ComputeNormalsOff()
    mcubes.SetValue(0, isoValue)

    smoothingIterations = 5
    passBand = 0.001
    featureAngle = 60.0
    smoother = vtk.vtkWindowedSincPolyDataFilter()
    smoother.SetInputConnection(mcubes.GetOutputPort())
    smoother.SetNumberOfIterations(smoothingIterations)
    smoother.BoundarySmoothingOff()
    smoother.FeatureEdgeSmoothingOff()
    smoother.SetFeatureAngle(featureAngle)
    smoother.SetPassBand(passBand)
    smoother.NonManifoldSmoothingOn()
    smoother.NormalizeCoordinatesOn()
    smoother.Update()

    normals = vtk.vtkPolyDataNormals()
    normals.SetInputConnection(smoother.GetOutputPort())
    normals.SetFeatureAngle(featureAngle)

    stripper = vtk.vtkStripper()
    stripper.SetInputConnection(normals.GetOutputPort())

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(stripper.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    return actor, normals


if __name__ == '__main__':
    main()