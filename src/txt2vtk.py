#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vtk
from vtk.util import numpy_support as nps
import os, sys
from ReadData import Mesh
import numpy as np
import glob
import tkinter, tkinter.filedialog, tkinter.messagebox

def main():
    foldername="fai4x6"
    mesh=Mesh(GetPath(foldername))

    colors = vtk.vtkNamedColors()

    # create polyhedron (voronoi mesh)
    points = vtk.vtkPoints()

    for i in range(mesh.num_of_node):
        points.InsertNextPoint(mesh.face.node.cod[i]) #codは0startにしているので0-num_of_node-1でOK

    ugrid = vtk.vtkUnstructuredGrid()
    ugrid.SetPoints(points)

    for i in range(mesh.num_of_elem):
        #todo: nodeID, ifaceをそもそも-1しておいていいかも(ReadData.pyで)
        faces=[]
        for iface in mesh.elem.faceID[i]:
            if iface not in mesh.face.zero_face:
                faces.append( mesh.face.nodeID[iface] )
        # faces=[ [nodeID for nodeID in mesh.face.nodeID[iface]] for iface in mesh.elem.faceID[i] ] #nodeID,ifaceは1start(fortranのまま)なので修正
        # faces=[mesh.face.nodeID[iface] if iface not in mesh.face.zero_face for iface in mesh.elem.faceID[i]]
        faceId = vtk.vtkIdList()
        faceId.InsertNextId(len(faces)) #
        
        for face in faces:
            faceId.InsertNextId(len(face))  # The number of points in the face.
            [faceId.InsertNextId(i) for i in face]

        ugrid.InsertNextCell(vtk.VTK_POLYHEDRON, faceId)
    
    #CellDataの入力
    sgm_type=("min","max","Y")  #出力したい応力を入力する
    mesh.GetSgmData(sgm_type)

    #MatIDの入力
    matID=nps.numpy_to_vtk(num_array=np.array(mesh.elem.matID),deep=True,array_type=vtk.VTK_INT)
    matID.SetName("matID")
    ugrid.GetCellData().AddArray(matID)

    if mesh.sgm_paths:  #pathがあるとき(空のリストでないとき)
        for idx,sgm in enumerate(mesh.sgm_steps):
            for s_type in range(sgm.shape[1]): #列(SgmType)の分だけloop回す
                scalar=nps.numpy_to_vtk(num_array=sgm[:,s_type],deep=True,array_type=vtk.VTK_FLOAT)
                scalar.SetName(sgm_type[s_type])
                ugrid.GetCellData().AddArray(scalar)    #SetScalarだと過去のデータを削除してしまうので注意
            WriteVtkFile(os.path.basename(mesh.sgm_paths[idx]).split(".")[0],ugrid)
            DelVtkArray(ugrid,sgm_type)
    else:
        WriteVtkFile(foldername,ugrid)

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
    if foldername=="sample":
        return os.path.normpath(os.path.join(name,"../",foldername))
    else:
        return os.path.normpath(os.path.join(name,"elements/",foldername))

def DelVtkArray(vtk_obj,arr_names):
    for name in arr_names:
        vtk_obj.GetCellData().RemoveArray(name)

def WriteVtkFile(name,vtk_obj):
    # Here we write out the cube.
    writer = vtk.vtkXMLUnstructuredGridWriter()
    if vtk.VTK_MAJOR_VERSION <= 5:
        writer.SetInput(vtk_obj)
    else:
        writer.SetInputData(vtk_obj)
    writer.SetFileName(name+".vtu")
    writer.SetDataModeToAscii()
    writer.Update()

def SelectFolderGUI():
    root = tkinter.Tk()
    root.withdraw()
    fTyp = [("","*")]
    iDir = os.path.abspath(os.path.dirname(__file__))
    tkinter.messagebox.showinfo('txt2vtk','Select input folder！')
    folder_path = tkinter.filedialog.askopenfilename(filetypes = fTyp,initialdir = iDir)
    return folder_path

if __name__ == '__main__':
    main()