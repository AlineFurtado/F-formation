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
    
    def approach_samples(p1,p2,xc,yc,rc, num=4): #por enquanto para f-formation face to face
    #calcula o raio do P-space r e de R-space R, em seguida define a posição dos approach samples.
    #best approach sample posicionado dentro do R-space com o raio passando pelo ponto (xc,yc) 
    #demais samples entre -45 e +45 ao redor dele
        print('xc',xc)
        print('yc',yc)
        print('rc',rc)
        #calculo do P-space (1.10=_radius+personal_space)
        r = rc + 1.10
        
        #Então calcula o raio de approximação r<rapp<R
        #rapp = r + self.sd/2
        rapp = r + 0.6
            
        samples = []
        x1,y1,th1 = p1.get_coords()
        x2,y2,th2 = p2.get_coords()
        thc = th1 +np.deg2rad(90)
        
        #calculo das coordenadas do Best approach sample
        if y2 == y1:   #face to face horizontal
            xs1 = xc
            ys1 = rapp + yc
            samples.append([xs1,ys1])
            xs2 = xc
            ys2 = -rapp + yc
            samples.append([xs2,ys2])
            
        else:
            if x1 == x2:
                ys1 = yc
                xs1 = rapp + xc
                samples.append([xs1,ys1])
                ys2 = yc
                xs2 = -rapp + xc
                samples.append([xs2,ys2])
            else:
                xs1 = xc - rapp*np.cos(th1+np.deg2rad(90))
                ys1 = yc - rapp*np.sin(th1+np.deg2rad(90))
                samples.append([xs1,ys1])
                xs2 = xc + rapp*np.cos(th1+np.deg2rad(90))
                ys2 = yc + rapp*np.sin(th1+np.deg2rad(90))
                samples.append([xs2,ys2])
                
        #definindo mais approach samples:
        minang=-40
        maxang=40
        angles = np.linspace(np.deg2rad(minang), np.deg2rad(maxang), num)
        sx = rapp * np.cos(thc + angles) + xc
        sy = rapp * np.sin(thc + angles) + yc
        samples.append([sx, sy])
        
        if x1 ==x2:
            sx1 = rapp * np.cos(np.deg2rad(0) + angles) + xc
            sy1 = rapp * np.sin(np.deg2rad(0) + angles) + yc
            samples.append([sx1, sy1])
        else:
            if y1 == y2:
                sx1 = rapp * np.cos(-thc + angles) + xc
                sy1 = rapp * np.sin(-thc + angles) + yc
                samples.append([sx1, sy1])
            else:
                sx1 = rapp * np.cos((th2+np.deg2rad(90)) + angles) + xc
                sy1 = rapp * np.sin((th2+np.deg2rad(90)) + angles) + yc
                samples.append([sx1, sy1])
            
        print(samples)
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
#######################Criando os clusters###############

# Cada instância do meu problema vai conter as coordenadas x, y e o respectivo reward rw,
# ou seja, cada instância é um target que pode ser visitado pelo robô, um node do meu OP
def Clusters():
    clusters = {}
    instances1 = {}
    instances2 = {}
    instances3 = {}
    
        
    #Por exemplo vou criar uma cena com 3 clusters e 2 instâncias para cada cluster
    #caso1 (mesmo x)
    x1 = 2
    x2 = 2
    y1 = 4
    y2 = 7
    th1 = np.deg2rad(90)
    th2 = np.deg2rad(270)
    
    p1,p2,xc,yc,rc = F_formation.Face_to_face(x1,y1,th1,x2,y2,th2)
    samples = F_formation.approach_samples(p1,p2,xc,yc,rc)
    #vou considerar por simplicidade que abordar os grupos pela direita ou por cima seja o melhor, para atribuir os rewards
    rw = [+10,+5]
    for sample in samples:
        if sample[0]>xc:
            instances1.update({len(instances1):(sample,rw[0])})
        else:
            instances1.update({len(instances1):(sample,rw[1])})
    clusters.update({len(clusters):(p1,p2,xc,yc,rc,instances1)})
    #F_formation.draw_formation(ax,p1,p2,xc,yc,rc,samples)
    
    #caso2 (mesmo y)
    x1 = 8
    x2 = 12
    y1 = 4
    y2 = 4
    th1 = np.deg2rad(0)
    th2 = np.deg2rad(180)
    
    p1,p2,xc,yc,rc = F_formation.Face_to_face(x1,y1,th1,x2,y2,th2)
    samples = F_formation.approach_samples(p1,p2,xc,yc,rc)
    #F_formation.draw_formation(ax,p1,p2,xc,yc,rc,samples)
    rw = [+10,+5]
    for sample in samples:
        if sample[1]>yc:
            instances2.update({len(instances2):(sample,rw[0])})
        else:
            instances2.update({len(instances2):(sample,rw[1])})
    clusters.update({len(clusters):(p1,p2,xc,yc,rc,instances2)})
    
    #caso3 (x e y diferentes)
    x2 = 5
    x1 = 2
    y1 = 10
    y2 = 13
    th1 = np.deg2rad(45)
    th2 = np.deg2rad(225)
    
    p1,p2,xc,yc,rc = F_formation.Face_to_face(x1,y1,th1,x2,y2,th2)
    samples = F_formation.approach_samples(p1,p2,xc,yc,rc)
    #F_formation.draw_formation(ax,p1,p2,xc,yc,rc,samples)
    rw = [+10,+5]
    for sample in samples:
        if sample[1]>yc:
            instances3.update({len(instances3):(sample,rw[0])})
        else:
            instances3.update({len(instances3):(sample,rw[1])})
    clusters.update({len(clusters):(p1,p2,xc,yc,rc,instances3)})
    
    return clusters

def DrawCena(clusters):
    
    plt.close('all')
    #matplotlib.style.use('classic')
    
    fig = plt.figure(figsize=(8,5), dpi=100)
    ax = fig.add_subplot(111, aspect='equal')
    
    aux = []
    vetor = []
    samples = []
    for i in clusters.keys():
        temp = clusters.get(i)
        vetor.append(temp)
    print(vetor)
    for cluster in vetor:
        print('cluster')
        for i in cluster:
            ajuda = i
            aux.append(ajuda)
        p1 = aux[0]
        p2 = aux[1]
        xc = aux[2]
        yc = aux[3]
        rc = aux[4]
        dic = aux[5]
        for j in dic.keys():
            tupla = dic.get(j)
            samples.append(tupla[0])
        #F_formation.draw_formation(ax,p1,p2,xc,yc,rc,samples)
        p1.draw(ax)
        p2.draw(ax)
        #P_Space
        pspace = Circle((xc, yc), radius=(rc + 1.10), fill=False, ls='--', color='b')
        ax.add_patch(pspace)
        #R_Space
        #calculo do R-space
        R = rc + 1.10 + 1.2 #R= r + sd
        Rspace = Circle((xc, yc), radius=R, fill=False, ls='--', color='g')
        ax.add_patch(Rspace)
        for sample in samples:
            ax.scatter(sample[0], sample[1])
        
        
    ax.tick_params(labelsize=12)
    ax.grid(False)
    ax.set_xlim([0, 30])
    ax.set_ylim([0, 30])
    plt.axis('equal')
    plt.title('Cena inicial')
    plt.show()
####################Testes de implementação#################
def main():
    
    #caso1 (mesmo x)
    x1 = 2
    x2 = 2
    y1 = 4
    y2 = 7
    th1 = np.deg2rad(90)
    th2 = np.deg2rad(270)
    
    p1,p2,xc,yc,rc = F_formation.Face_to_face(x1,y1,th1,x2,y2,th2)
    samples = F_formation.approach_samples(p1,p2,xc,yc,rc)
    fig = plt.figure(figsize=(8,5), dpi=100)
    ax = fig.add_subplot(111, aspect='equal')
    F_formation.draw_formation(ax,p1,p2,xc,yc,rc,samples)
    
    #caso2 (mesmo y)
    x1 = 8
    x2 = 12
    y1 = 4
    y2 = 4
    th1 = np.deg2rad(0)
    th2 = np.deg2rad(180)
    
    p1,p2,xc,yc,rc = F_formation.Face_to_face(x1,y1,th1,x2,y2,th2)
    samples = F_formation.approach_samples(p1,p2,xc,yc,rc)
    fig = plt.figure(figsize=(8,5), dpi=100)
    ax = fig.add_subplot(111, aspect='equal')
    F_formation.draw_formation(ax,p1,p2,xc,yc,rc,samples)
    
    #caso3 (x e y diferentes)
    x2 = 5
    x1 = 2
    y1 = 10
    y2 = 13
    th1 = np.deg2rad(45)
    th2 = np.deg2rad(225)
    
    p1,p2,xc,yc,rc = F_formation.Face_to_face(x1,y1,th1,x2,y2,th2)
    samples = F_formation.approach_samples(p1,p2,xc,yc,rc)
    fig = plt.figure(figsize=(8,5), dpi=100)
    ax = fig.add_subplot(111, aspect='equal')
    F_formation.draw_formation(ax,p1,p2,xc,yc,rc,samples)
    
    
