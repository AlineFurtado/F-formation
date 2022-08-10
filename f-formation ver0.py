# -*- coding: utf-8 -*-
"""
Created on Wed Aug 10 08:58:10 2022

@author: User-Aline
"""


import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge, Polygon
import numpy as np
import math

import os
import tempfile
from subprocess import check_output
import networkx as nx
from shapely.geometry import Polygon
from shapely.geometry import Point
from shapely.geometry import LineString
from descartes.patch import PolygonPatch


class Person(object):
    
    x = 0
    y = 0
    th = 0
    
    xdot = 0
    ydot = 0
       
    _radius = 0.60 #raio do corpo da pessoa
    personal_space = 0.50 #raio da região de personal_space

        
    """ Public Methods """
    def __init__(self, x=0, y=0, th=0):
        self.x = x
        self.y = y
        self.th = th

    def get_coords(self):
      return [self.x, self.y, self.th]

    def draw(self, ax):
        # define grid.
        npts = 100
        x = np.linspace(self.x-5, self.x+5, npts)
        y = np.linspace(self.y-5, self.y+5, npts)

        X, Y = np.meshgrid(x, y)
            
        # Corpo
        body = Circle((self.x, self.y), radius=self._radius, fill=False)
        ax.add_patch(body)

        # Orientação
        x_aux = self.x + self._radius * np.cos(self.th);
        y_aux = self.y + self._radius * np.sin(self.th);
        heading = plt.Line2D((self.x, x_aux), (self.y, y_aux), lw=3, color='k')
        ax.add_line(heading)
        
        #Personal Space
        space = Circle((self.x, self.y), radius=(self._radius+self.personal_space), fill=False, ls='--', color='r')
        ax.add_patch(space)

class F_formation:
    
    #coordenadas do O-space
    xc = 0
    yc = 0
    rc = 0
    
    """ Public Methods """
    def __init__(self, xc=0, yc=0, thc=0):
        self.xc = xc
        self.yc = yc
        self.thc = thc
        
    def Face_to_face(x1,y1,th1,x2,y2,th2):
        #Segundo proxemics a distância entre p1 e p2 deve ser de pelo menos 1 metro
        
        #Cria um grupo de duas pessoas
        p1 = Person(x1,y1,th1)
        p2 = Person(x2,y2,th2)
        
        #calcula o raio do O-space
        if x2 == x1:
            rc = (y2-y1)/(np.sin(th2)-np.sin(th1))
        else:
            rc = (x2-x1)/(np.cos(th1)-np.cos(th2))
        print('rc:',rc)
        #Calcula as coordenadas do centro do O-space
        if y1 == y2:
            xc = x1 + rc*np.cos(th1)
            yc = y1 + rc*np.sin(th1)
        else:
            if x1 == x2:
                xc = x1 + rc*np.cos(th1)
                yc = y1 - rc*np.sin(th1)
                
            else:
                xc = x1 + (x2-x1)/2
                yc = y1 + (y2-y1)/2
        
        return p1,p2,xc,yc
    
    def approach_samples(xc,yc,p1,p2):
        #definir os targets de cada grupo 
        
        #d = _radius+ personal_space
        d = 1.10
        samples = []
        x1,y1,th1 = p1.get_coords()
        x2,y2,th2 = p2.get_coords()
        if x2 == x1:
            xs1 = xc - d
            samples.append([xs1,yc])
            samples.append([xc,yc])
            xs2 = xc + d
            samples.append([xs2,yc])
        else:
            if y1 == y2:
                ys1 = yc - d
                samples.append([xc,ys1])
                samples.append([xc,yc])
                ys2 = yc + d
                samples.append([xc,ys2])
            else:
                xs1 = xc-1
                ys1 = yc+d
                samples.append([xs1,ys1])
                samples.append([xc,yc])
                xs2 = xc +1
                ys2 = yc -d
                samples.append([xs2,ys2])
        print(samples)
        return samples
    
    def draw_formation(p1,p2,samples):
         
        fig = plt.figure(figsize=(8,5), dpi=100)
        ax = fig.add_subplot(111, aspect='equal')  
        p1.draw(ax)
        p2.draw(ax)
        for sample in samples:
            ax.scatter(sample[0], sample[1])
            
        ax.tick_params(labelsize=12)
        ax.grid(False)
        #ax.set_xlim([-1, 30])
        #ax.set_ylim([-1, 30])
        plt.axis('equal')
        #plt.title('Exemplo teste')
        plt.show()
        #plt.savefig("cena.png",dpi=100)

####################################### Main para testes###################
def main():
    
    #casos de teste
    #caso1 (mesmo x)
    #x1 = 2
    #x2 = 2
    #y1 = 4
    #y2 = 7
    #th1 = np.deg2rad(90)
    #th2 = np.deg2rad(270)
    
    #caso2 (mesmo y)
    #x1 = 2
    #x2 = 5
    #y1 = 4
    #y2 = 4
    #th1 = np.deg2rad(0)
    #th2 = np.deg2rad(180)
    
    #caso3 (x e y diferentes)
    x2 = 5
    x1 = 2
    y1 = 4
    y2 = 7
    th1 = np.deg2rad(45)
    th2 = np.deg2rad(225)
    
    p1,p2,xc,yc = F_formation.Face_to_face(x1,y1,th1,x2,y2,th2)
    samples = F_formation.approach_samples(xc,yc,p1,p2)
    F_formation.draw_formation(p1,p2,samples)
    #DrawCena(p1, p2, samples)
    