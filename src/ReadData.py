#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os,sys
import glob

class Elem:
    def __init__(self,path):
        self.matID=[]
        self.faceID=[]

        with open(os.path.join(path,"ELEMENT.INDAT"),"r") as f:
            f.readline()    #empty line
            self.num_of_elem=int(f.readline().split()[0])

            for _ in range(self.num_of_elem):
                line=f.readline().split()
                faceID=[int(item)-1 for item in line[6:]] #ここから面積0のものを除く
                self.InsertElem(int(line[1]),faceID)    #matID: int(line[1])

    def InsertElem(self,matID,faceIDs):
        self.matID.append(matID)
        self.faceID.append(faceIDs)

class Node:
    def __init__(self,path):
        with open(os.path.join(path,"SURFACE.INDAT"),"r") as f:
            f.readline()    #empty line
            # self.num_of_node, _=[int(item) for item in f.readline().split()[:2]]
            self.num_of_node = int(f.readline().split()[0])

            self.cod=np.zeros((self.num_of_node,3))
            
            for _ in range(self.num_of_node):   #"_": 使わない数字
                line=f.readline().split()   #.split(): 空白かタブで文字を区切る
                cod=[float(item) for item in line[1:]]
                self.InsertNode(int(line[0]),cod) #node id: int(line[0])

    def InsertNode(self,nodeID,cod):
        self.cod[nodeID-1]=np.array(cod) #nodeID-1: 他のリストと合わせるため

class Surface:
    def __init__(self,path):
        self.nodeID=[]
        self.FaceType=[]
        self.zero_face=[]

        self.node=Node(path)

        with open(os.path.join(path,"SURFACE.INDAT"),"r") as f:
            f.readline()    #empty line
            # nnode, self.num_of_face=[int(item) for item in f.readline().split()[:2]]
            self.num_of_face=int(f.readline().split()[1])
            
            for _ in range(self.node.num_of_node+1):   #"_": 使わない数字
                f.readline()
            
            for _ in range(self.num_of_face):
                line=f.readline().split()
                ids=[int(item)-1 for item in line[5:]]    #line[5:]: face ids
                self.InsertFace(int(line[3]),ids)   #int(line[3]): facetype 

    def InsertFace(self,typeID,NodesList):
        self.FaceType.append(typeID)
        self.nodeID.append(NodesList)

    def FindZeroAreaFace(self):
        for i in range(self.num_of_face):
            if len(self.nodeID[i]) < 3:
                self.zero_face.append(i)
            elif FaceArea( np.array([self.node.cod[idx] for idx in self.nodeID[i]]) )  < 1.e-8:
                self.zero_face.append(i)
                
        print(self.zero_face)

class Mesh:
    def __init__(self,path,rm_zero=False):
        self.path=path

        self.elem=Elem(self.path)
        self.num_of_elem=self.elem.num_of_elem
        
        self.face=Surface(self.path)
        self.num_of_face=self.face.num_of_face
        self.num_of_node=self.face.node.num_of_node
        
        if rm_zero:
            self.face.FindZeroAreaFace()

    #def Defrom(self):
    #def InputVTK(self):

    def GetSgmData(self,types):
        self.sgm_types=types
        self.sgm_paths=self.GetSgmPaths()
        
        if not self.sgm_paths:
            print("[WARNING] There is no PrincipalSgm4Paraview... .txt!!  Path:{}".format(self.path))
            return

        self.sgm_steps=[]
        for path in self.sgm_paths:
            s=Stress(path,self.num_of_elem,types)
            self.sgm_steps.append(s.sgms)
        del s

    def GetSgmPaths(self):
        p_list=glob.glob(os.path.join(self.path,"PrincipalSgm4Paraview*.txt"))

        if p_list:  #リストに値がある時出力
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