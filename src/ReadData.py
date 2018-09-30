#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os,sys
import glob

class Elem:
    def __init__(self,num_of_elem):
        self.matID=[]
        self.faceID=[]
    def InsertElem(self,matID,faceIDs):
        self.matID.append(matID)
        self.faceID.append(faceIDs)

class Node:
    def __init__(self,num_of_node):
        self.num_of_node=num_of_node
        self.cod=np.zeros((self.num_of_node,3))
    
    def InsertNode(self,nodeID,cod):
        self.cod[nodeID-1]=np.array(cod) #nodeID-1: 他のリストと合わせるため

class Surface:
    def __init__(self,num_of_face):
        self.nodeID=[]
        self.FaceType=[]

    def InsertFace(self,typeID,NodesList):
        self.FaceType.append(typeID)
        self.nodeID.append(NodesList)

class Mesh:
    def __init__(self,path):
        self.path=path
        with open(os.path.join(path,"SURFACE.INDAT"),"r") as f:
            f.readline()    #empty line
            self.num_of_node,self.num_of_face=[int(item) for item in f.readline().split()[:2]]
            
            self.node=Node(self.num_of_node)
            for _ in range(self.num_of_node):   #"_": 使わない数字
                line=f.readline().split()
                cod=[float(item) for item in line[1:]]
                self.node.InsertNode(int(line[0]),cod) #id: int(line[0])

            f.readline()    #empty line
            
            self.face=Surface(self.num_of_face)
            for _ in range(self.num_of_face):
                line=f.readline().split()
                ids=[int(item) for item in line[5:]]
                self.face.InsertFace(int(line[3]),ids)   #facetype: int(line[3])
        
        with open(os.path.join(path,"ELEMENT.INDAT"),"r") as f:
            f.readline()    #empty line
            self.num_of_elem=int(f.readline().split()[0])

            self.elem=Elem(self.num_of_elem)
            for _ in range(self.num_of_elem):
                line=f.readline().split()
                faceID=[int(item) for item in line[6:]]
                self.elem.InsertElem(int(line[1]),faceID)    #matID: int(line[1])

    #def Defrom(self):
    #def InputVTK(self):

    def GetSgmData(self,types):
        self.sgm_types=types
        self.sgm_paths=self.GetSgmPaths()
        
        if not self.sgm_paths:
            print("There is no PrincipalSgm4Paraview... .txt!! Path:{}".format(self.path))
            return

        self.sgm_steps=[]
        for path in self.sgm_paths:
            s=Stress(path,self.num_of_elem,types)
            self.sgm_steps.append(s.sgms)
        del s

    def GetSgmPaths(self):
        p_list=glob.glob(os.path.join(self.path,"PrincipalSgm4Paraview*.txt"))

        print("Num of Paths:{}".format(len(p_list)))
        print( [os.path.basename(n) for n in p_list] )
        return p_list

class Stress:
    def __init__(self,path,nelm,types):
        self.path=path
        self.num_of_elem=nelm
        self.types=types
        self.GetSgm()

    sgm_dict={"min":1,"max":2,"x":3,"y":4,"z":5}    #0行目は要素番号なので1スタートで

    def GetSgm(self):
        num_lines=sum(1 for line in open(self.path))-1
        if num_lines != self.num_of_elem:
            raise ValueError("InputError: Check the consistent between Element.INDAT & {}".format(self.path))

        self.sgms=np.loadtxt(self.path,delimiter="\t",skiprows=1,usecols=[self.sgm_dict[key.lower()] for key in self.types])
    
    def GetSgmPaths(self):
        self.sgm_paths=glob.glob(os.path.join(self.path,"PrincipalSgm4Paraview"))
        
        print("Num of Paths:{}".format(len(self.sgm_paths)))
        print( [os.path.basename(n) for n in self.sgm_paths] )

def main():
    name=os.path.dirname(os.path.abspath(__file__))
    path=os.path.normpath(os.path.join(name,"../sample"))
    mesh=Mesh(path)
    print("elements:{}".format(mesh.num_of_elem))
    print("nodes:{}".format(mesh.num_of_node))    
    print("faces:{}".format(mesh.num_of_face))

if __name__ == '__main__':
    main()