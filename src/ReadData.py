#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os,sys

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
        with open(os.path.join(path,"SURFACE.INDAT"),"r") as f:
            f.readline()    #empty line
            self.num_of_node,self.num_of_face=[int(item) for item in f.readline().split()[:2]]
            
            self.node=Node(self.num_of_node)
            for _ in range(self.num_of_node):   #"_": 使わない数字
                line=f.readline().split()
                cod=[np.float64(item) for item in line[1:]]
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

    

def main():
    name=os.path.dirname(os.path.abspath(__file__))
    path=os.path.normpath(os.path.join(name,"../sample"))
    mesh=Mesh(path)
    print("elements:{}".format(mesh.num_of_elem))
    print("nodes:{}".format(mesh.num_of_node))    
    print("faces:{}".format(mesh.num_of_face))

if __name__ == '__main__':
    main()