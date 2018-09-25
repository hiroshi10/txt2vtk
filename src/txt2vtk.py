#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vtk
import os, sys
from ReadData import Mesh
import numpy as np

def main():
    foldername="sample"
    mesh=Mesh(GetPath(foldername))

    colors = vtk.vtkNamedColors()

    # create polyhedron (voronoi mesh)
    points = vtk.vtkPoints()

    for i in range(mesh.num_of_node):
        points.InsertNextPoint(mesh.node.cod[i]) #codは0startにしているので0-num_of_node-1でOK

    ugrid = vtk.vtkUnstructuredGrid()
    ugrid.SetPoints(points)

    for i in range(mesh.num_of_elem):
        #todo: nodeID, ifaceをそもそも-1しておいていいかも(ReadData.pyで)
        faces=[ [nodeID-1 for nodeID in mesh.face.nodeID[iface-1]] for iface in mesh.elem.faceID[i] ] #nodeID,ifaceは1start(fortranのまま)なので修正
        faceId = vtk.vtkIdList()
        faceId.InsertNextId(len(mesh.elem.faceID[i]))
        
        for face in faces:
            faceId.InsertNextId(len(face))  # The number of points in the face.
            [faceId.InsertNextId(i) for i in face]

        ugrid.InsertNextCell(vtk.VTK_POLYHEDRON, faceId)
    
    #Test
    scalars=vtk.vtkFloatArray()
    for i in range(mesh.num_of_elem):
        scalars.InsertNextValue(i)
    ugrid.GetCellData().SetScalars(scalars)

    # Here we write out the cube.
    writer = vtk.vtkXMLUnstructuredGridWriter()
    if vtk.VTK_MAJOR_VERSION <= 5:
        writer.SetInput(ugrid)
    else:
        writer.SetInputData(ugrid)
    writer.SetFileName(foldername+".vtu")
    writer.SetDataModeToAscii()
    writer.Update()

    # Create a mapper and actor
    mapper = vtk.vtkDataSetMapper()
    if vtk.VTK_MAJOR_VERSION <= 5:
        mapper.SetInput(ugrid)
    else:
        mapper.SetInputData(ugrid)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(
        colors.GetColor3d("Silver"))

    # Visualize
    renderer = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.SetWindowName("Polyhedron")
    renderWindow.AddRenderer(renderer)
    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)

    renderer.AddActor(actor)
    renderer.SetBackground(colors.GetColor3d("Salmon"))
    renderer.ResetCamera()
    renderer.GetActiveCamera().Azimuth(30)
    renderer.GetActiveCamera().Elevation(30)
    renderWindow.Render()
    renderWindowInteractor.Start()

def GetPath(foldername="sample"):
    name=os.path.dirname(os.path.abspath(__file__))
    path=os.path.normpath(os.path.join(name,"../",foldername))
    return path

if __name__ == '__main__':
    main()