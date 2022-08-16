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
    
    sd = 1.2 #social distance
    """ Public Methods"""
    def __init__(self, sd = 1.2):
        self.sd = sd
     #   self.xc = xc
      #  self.yc = yc
       # self.thc = thc
        
    def Face_to_face(x1,y1,th1,x2,y2,th2):
        #Segundo proxemics a distância entre p1 e p2 deve ser de pelo menos 1 metro
        
        #Cria um grupo de duas pessoas
        p1 = Person(x1,y1,th1)
        p2 = Person(x2,y2,th2)
        
        #calcula o raio do O-space
        if x2 == x1:
            rc = (y2-y1)/(np.sin(th1)-np.sin(th2))
        else:
            rc = (x2-x1)/(np.cos(th1)-np.cos(th2))
        #print('rc:',rc)
        
        #Calcula as coordenadas do centro do O-space
        if y1 == y2:
            xc = x1 + rc*np.cos(th1)
            yc = y1 + rc*np.sin(th1)
        else:
            if x1 == x2:
                xc = x1 + (x2-x1)/2
                yc = y1 + (y2-y1)/2
                
            else:
                xc = x1 + (x2-x1)/2
                yc = y1 + (y2-y1)/2
        
        return p1,p2,xc,yc,rc
    
    def L_shaped(x1,y1,th1,x2,y2,th2):
        #deve-se satisfazer a condição: x1<x2 e y1>y2, e th1=-90 e th2=180, ou ou th2=90 e th1=0
        
        #Cria um grupo de duas pessoas
        p1 = Person(x1,y1,th1)
        p2 = Person(x2,y2,th2)
        
        #calcula o raio do O-space
        rc = (y1-y2) 
       #print('rc', rc)
        
        #Determina as coordenadas do centro do O-space
        if th1 == np.deg2rad(-90):
            xc = x1
            yc = y2
        else:
            if th2 == np.deg2rad(90):
                xc = x2
                yc = y1
        
        return p1,p2,xc,yc,rc
    
    def Side_by_side(x1,y1,th1,x2,y2,th2):
        #x1<x2; y1=y2; th1=th2=90 ou -90
        
        #Cria um grupo de duas pessoas
        p1 = Person(x1,y1,th1)
        p2 = Person(x2,y2,th2)
        
        #Determina as coordenadas do centro do O-space
        xc = (x2-x1)/2 + x1
        yc = y1 + (xc-x1)*np.tan(np.deg2rad(45))
        
        #calcula o raio do O-space
        rc = (yc - y1)/np.cos(np.deg2rad(45))
        
        return p1,p2,xc,yc,rc
    
    def approach_samples(p1,p2,xc,yc,rc, num=2): #num é o número de approach em cada direção (frente ou costas)
    #relativa ao centro do O-sapce exceto os dois approachs centrais. ]
    #Ou seja Número total de targets = num + 2
    #calcula o raio do P-space r e de R-space R, em seguida define a posição dos approach samples.
    #best approach sample posicionado dentro do R-space com o raio passando pelo ponto (xc,yc) 
    #demais samples entre -45 e +45 ao redor dele
        
        #calculo do P-space (1.10=_radius+personal_space)
        r = rc + 1.10
        
        #Então calcula o raio de approximação r<rapp<R
        #rapp = r + self.sd/2
        rapp = r + 0.6
            
        samples = []
        x1,y1,th1 = p1.get_coords()
        x2,y2,th2 = p2.get_coords()
        thc = th1 +np.deg2rad(90) #para a maioria dos casos, excessões são calculadas ou atribuidas localmente
        
        #calculo das coordenadas do Best approach sample (Máximo ou Mínimo Reward conforme cada caso)
        if y2 == y1:   #face to face horizontal and side by side
            xs1 = xc
            ys1 = rapp + yc
            samples.append([xs1,ys1,thc,10]) #samples[2]=reward
            xs2 = xc
            ys2 = -rapp + yc
            samples.append([xs2,ys2,thc,2])
            
        else:# face to face vertical
            if x1 == x2:
                ys1 = yc
                xs1 = rapp + xc
                samples.append([xs1,ys1,thc,10])
                ys2 = yc
                xs2 = -rapp + xc
                samples.append([xs2,ys2,thc,10])
            else: #se L-shaped
                if (x2>x1) & (y1>y2):
                    thc = np.deg2rad(45)
                    xs1 = xc - rapp * np.sin(thc)
                    ys1 = yc - rapp * np.cos(thc)
                    samples.append([xs1,ys1,thc,10])
                    thc = np.deg2rad(225)
                    xs2 = xc - rapp * np.sin(thc)
                    ys2 = yc - rapp * np.cos(thc)
                    samples.append([xs2,ys2,thc,2])
                
                else: #face to face transversal
                    thc = th1+np.deg2rad(90)
                    xs1 = xc - rapp*np.cos(th1+np.deg2rad(90))
                    ys1 = yc - rapp*np.sin(th1+np.deg2rad(90))
                    samples.append([xs1,ys1,thc,10])
                    xs2 = xc + rapp*np.cos(th1+np.deg2rad(90))
                    ys2 = yc + rapp*np.sin(th1+np.deg2rad(90))
                    samples.append([xs2,ys2,thc,10])
        
                
        #definindo mais approach samples:
        minang=-35
        maxang=35
        angles = np.linspace(np.deg2rad(minang), np.deg2rad(maxang), num)
        for angle in angles: #encontra os approach-points de frente para o centro do O-space
            if (x2>x1) & (y1>y2):
                thc = np.deg2rad(45)
            else:
                if th1==th2:
                    thc = th1
            sx = rapp * np.cos(thc + angle) + xc
            sy = rapp * np.sin(thc + angle) + yc
            samples.append([sx, sy, thc,5])
        
        #Encontra os approach-points simétricos 
        if x1 ==x2:
            for angle in angles:
                thc = np.deg2rad(0)
                sx1 = rapp * np.cos(np.deg2rad(0) + angle) + xc
                sy1 = rapp * np.sin(np.deg2rad(0) + angle) + yc
                samples.append([sx1, sy1,thc,1])
        else:
            if y1 == y2:
                if th1==th2:
                    thc = - th1
                    for angle in angles:
                        sx1 = rapp * np.cos(thc + angle) + xc
                        sy1 = rapp * np.sin(thc + angle) + yc
                        samples.append([sx1, sy1,thc,1])
                else:
                    for angle in angles:
                        sx1 = rapp * np.cos(-thc + angle) + xc
                        sy1 = rapp * np.sin(-thc + angle) + yc
                        samples.append([sx1, sy1, -thc,1])
            else:
                if (x2>x1) & (y1>y2):
                    for angle in angles:
                        thc = np.deg2rad(225)
                        sx1 = rapp * np.cos(thc + angle) + xc
                        sy1 = rapp * np.sin(thc + angle) + yc
                        samples.append([sx1, sy1,thc,1])
                
                else:
                    for angle in angles:
                        thc = th2+np.deg2rad(90)
                        sx1 = rapp * np.cos((th2+np.deg2rad(90)) + angle) + xc
                        sy1 = rapp * np.sin((th2+np.deg2rad(90)) + angle) + yc
                        samples.append([sx1, sy1,thc,1])
            
        #rint(samples)
        return samples
    
    def draw_formation(ax,p1,p2,xc,yc,rc,samples):
         
        fig = plt.figure(figsize=(8,5), dpi=100)
        ax = fig.add_subplot(111, aspect='equal')  
        p1.draw(ax)
        p2.draw(ax)
        
        #P_Space
        pspace = Circle((xc, yc), radius=(rc + 1.10), fill=False, ls='--', color='b')
        ax.add_patch(pspace)
        
        #R_Space
        #calculo do R-space
        R = rc + 2.20 #1.10 + 1.20 #R= r + sd
        Rspace = Circle((xc, yc), radius=R, fill=False, ls='--', color='g')
        ax.add_patch(Rspace)
        
        for sample in samples:
            ax.scatter(sample[0], sample[1])
            
        #ax.tick_params(labelsize=12)
        #ax.grid(False)
        #ax.set_xlim([0, 30])
        #ax.set_ylim([0, 30])
        plt.axis('equal')
        #plt.title('Exemplo teste')
        plt.show()
        #plt.savefig("cena.png",dpi=100)

def DrawCena(): #criação manual de uma cena
    
    fig = plt.figure(figsize=(8,5), dpi=100)
    ax = fig.add_subplot(111, aspect='equal')
    
    #caso1 (mesmo x)
    x1 = 9
    x2 = 9
    y1 = 10
    y2 = 13
    th1 = np.deg2rad(90)
    th2 = np.deg2rad(270)
    
    p1,p2,xc,yc,rc = F_formation.Face_to_face(x1,y1,th1,x2,y2,th2)
    samples = F_formation.approach_samples(p1,p2,xc,yc,rc)
    fig1 = F_formation.draw_formation(ax,p1,p2,xc,yc,rc,samples)
    ax.add_patch(fig1)
    
    #caso2 (mesmo y)
    x3 = 1
    x4 = 4
    y3 = 2
    y4 = 2
    th3 = np.deg2rad(0)
    th4 = np.deg2rad(180)
    
    p3,p4,xc,yc,rc = F_formation.Face_to_face(x3,y3,th3,x4,y4,th4)
    samples = F_formation.approach_samples(p3,p4,xc,yc,rc)
    fig2 = F_formation.draw_formation(ax,p3,p4,xc,yc,rc,samples)
    ax.add_patch(fig2)
    
    #caso3 (x e y diferentes)
    x5 = 14
    x6 = 17
    y5 = 18
    y6 = 21
    th5 = np.deg2rad(45)
    th6 = np.deg2rad(225)
    
    p5,p6,xc,yc,rc = F_formation.Face_to_face(x5,y5,th5,x6,y6,th6)
    samples = F_formation.approach_samples(p5,p6,xc,yc,rc)
    fig3 = F_formation.draw_formation(ax,p5,p6,xc,yc,rc,samples)
    ax.add_patch(fig3)
    
    #caso 4 (L-sheppard)
    x7= 14
    x8= 17
    y7= 5
    y8= 2
    th7 = np.deg2rad(-90)
    th8 = np.deg2rad(180)
    
    p7,p8,xc,yc,rc = F_formation.L_shaped(x7,y7,th7,x8,y8,th8)
    samples = F_formation.approach_samples(p7,p8,xc,yc,rc)
    fig4 = F_formation.draw_formation(ax,p7,p8,xc,yc,rc,samples)
    ax.add_patch(fig4)
    
    #caso5 (sibe_by_side)
    x9 = 1
    x10 = 4
    y9 = 13
    y10 = 13
    th9 = np.deg2rad(90)
    th10 = th1
    
    p9,p10,xc,yc,rc = F_formation.Side_by_side(x9,y9,th9,x10,y10,th10)
    samples = F_formation.approach_samples(p9,p10,xc,yc,rc)
    fig5 = F_formation.draw_formation(ax,p9,p10,xc,yc,rc,samples)
    ax.add_patch(fig5)
    
    ax.tick_params(labelsize=12)
    ax.grid(False)
    ax.set_xlim([0, 30])
    ax.set_ylim([0, 30])
    plt.axis('equal')
    plt.title('Cena inicial')
    plt.show()
    

#Criaçãoo manual dos clusters 
def Create_clusters():
    
    clusters = {}
    
    #caso1 (mesmo x)
    x1 = 9
    x2 = 9
    y1 = 10
    y2 = 13
    th1 = np.deg2rad(90)
    th2 = np.deg2rad(270)
    
    p1,p2,xc,yc,rc = F_formation.Face_to_face(x1,y1,th1,x2,y2,th2)
    samples = F_formation.approach_samples(p1,p2,xc,yc,rc)
    clusters.update({len(clusters):samples})
    
    #caso2 (mesmo y)
    x3 = 1
    x4 = 4
    y3 = 2
    y4 = 2
    th3 = np.deg2rad(0)
    th4 = np.deg2rad(180)
    
    p3,p4,xc,yc,rc = F_formation.Face_to_face(x3,y3,th3,x4,y4,th4)
    samples = F_formation.approach_samples(p3,p4,xc,yc,rc)
    clusters.update({len(clusters):samples})
    
    #caso3 (x e y diferentes)
    x5 = 14
    x6 = 17
    y5 = 18
    y6 = 21
    th5 = np.deg2rad(45)
    th6 = np.deg2rad(225)
    
    p5,p6,xc,yc,rc = F_formation.Face_to_face(x5,y5,th5,x6,y6,th6)
    samples = F_formation.approach_samples(p5,p6,xc,yc,rc)
    clusters.update({len(clusters):samples})
    
    #caso 4 (L-sheppard)
    x7= 14
    x8= 17
    y7= 5
    y8= 2
    th7 = np.deg2rad(-90)
    th8 = np.deg2rad(180)
    
    p7,p8,xc,yc,rc = F_formation.L_shaped(x7,y7,th7,x8,y8,th8)
    samples = F_formation.approach_samples(p7,p8,xc,yc,rc)
    clusters.update({len(clusters):samples})
    
    #caso5 (sibe_by_side)
    x9 = 1
    x10 = 4
    y9 = 13
    y10 = 13
    th9 = np.deg2rad(90)
    th10 = th1
    
    p9,p10,xc,yc,rc = F_formation.Side_by_side(x9,y9,th9,x10,y10,th10)
    samples = F_formation.approach_samples(p9,p10,xc,yc,rc)
    clusters.update({len(clusters):samples})
    
    return clusters
    
    ##### Testes####
        