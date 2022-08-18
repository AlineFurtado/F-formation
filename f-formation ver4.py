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
    
    def v_shaped(x1,y1,th1,x2,y2,th2):
        # x1=x2; y2>y1; th1 = 135 e th2 = 225
        
        #Cria um grupo de duas pessoas
        p1 = Person(x1,y1,th1)
        p2 = Person(x2,y2,th2)
        
        #Determina as coordenadas do centro do O-space
        xc = x1 + (x2-x1)/2
        yc = y1 + (y2-y1)/2
        
        #calcula o raio do O-space
        rc = (yc-y1)
        
        return p1,p2,xc,yc,rc
    
    def triangular(x1,y1,th1,x2,y2,th2,x3,y3,th3):
        #grupo com 3 pessoas formato triangular
        #x1<x2=x3; y2<y1<y3 th1=0, th2=110, th3=255
        
        #Cria um grupo de três pessoas
        p1 = Person(x1,y1,th1)
        p2 = Person(x2,y2,th2)
        p3 = Person(x3,y3,th3)
        
        #Determina as coordenadas do centro do O-space
        #baricentro
        xc = (x1 + x2 + x3)/3
        yc = (y1 + y2 + y3)/3
        
        #calcula o raio do O-space
        #usando propriedades do triangulo isosceles
        rc = math.sqrt(((xc-x2)**2+(yc-y2)**2))
        
        return p1,p2,p3,xc,yc,rc
    
    def semi_circle(xc,yc,rc):
        #people have the same point of observation
        x1 = xc-rc
        y1 = yc
        th1 = np.deg2rad(0)
        
        x2 = xc
        y2 = yc+rc
        th2 = np.deg2rad(-90)
        
        x3 = xc+rc
        y3 = yc
        th3 = np.deg2rad(180)
        
        #Cria um grupo de três pessoas
        p1 = Person(x1,y1,th1)
        p2 = Person(x2,y2,th2)
        p3 = Person(x3,y3,th3)
        
        return p1,p2,p3,xc,yc,rc
    
    def retangular(x1,y1,th1,x2,y2,th2,x3,y3,th3,x4,y4,th4):
        #formation for 4 people
        
        #Cria um grupo de duas pessoas
        p1 = Person(x1,y1,th1)
        p2 = Person(x2,y2,th2)
        p3 = Person(x3,y3,th3)
        p4 = Person(x4,y4,th4)
        
        #Determina as coordenadas do centro do O-space
        xc = x2 = x4
        yc = y1 = y3
        
        #calcula o raio do O-space
        d = math.sqrt(((yc-y2)**2+(x2-x1)**2)) #diâmetro
        rc = d/2 + 1
        
        return p1,p2,p3,p4,xc,yc,rc
    
    def Circular(xc,yc,rc):
        
        x1 = xc
        y1 = yc+rc
        th1 = np.deg2rad(-90)
        
        x2 = -xc +0.5
        y2 = yc
        th2 = np.deg2rad(0)
        
        x3 = xc -1.5
        y3 = -yc +0.9
        th3 = np.deg2rad(60)
        
        x4 = xc+rc
        y4 = yc
        th4 = np.deg2rad(180)
        
        x5 = xc + 1.5
        y5 = -yc + 0.9
        th5 = np.deg2rad(120)
        
                
        #Cria um grupo de cinco pessoas
        p1 = Person(x1,y1,th1)
        p2 = Person(x2,y2,th2)
        p3 = Person(x3,y3,th3)
        p4 = Person(x4,y4,th4)
        p5 = Person(x5,y5,th5)
        
        return p1,p2,p3,p4,p5,xc,yc,rc

    def approach_samples(p1,p2,xc,yc,rc, num=2): #num é o número de approach em frente 
    #relativa ao centro do O-sapce exceto o approach central. ]
    #Ou seja Número total de targets = num + 2 #Vou fixar em 3 targets por grupo
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
            samples.append([xs1,ys1]) #samples[2]=reward
        else:# face to face vertical ou v_shaped
            if x1 == x2:
                ys1 = yc
                xs1 = xc - rapp
                samples.append([xs1,ys1])
                
            else: #se L-shaped
                if (x2>x1) & (y1>y2):
                    thc = np.deg2rad(45)
                    xs1 = xc - rapp * np.sin(thc)
                    ys1 = yc - rapp * np.cos(thc)
                    samples.append([xs1,ys1])
                    
                else: #face to face transversal
                    thc = th1+np.deg2rad(90)
                    xs1 = xc - rapp*np.cos(th1+np.deg2rad(90))
                    ys1 = yc - rapp*np.sin(th1+np.deg2rad(90))
                    samples.append([xs1,ys1])
                    
                
        #definindo mais approach samples:
        minang=-35
        maxang=35
        angles = np.linspace(np.deg2rad(minang), np.deg2rad(maxang), num)
        for angle in angles: #encontra os approach-points de frente para o centro do O-space
            if (x2>x1) & (y1>y2):
                thc = np.deg2rad(225)
            else:
                if th1==th2:
                    thc = th1
                else:
                    if (th2-th1) == np.deg2rad(90):
                        thc = np.deg2rad(180)
                    else:
                        if (y2>y1) and (th1==np.deg2rad(45)) :
                            thc = np.deg2rad(315)
                            
            sx = rapp * np.cos(thc + angle) + xc
            sy = rapp * np.sin(thc + angle) + yc
            samples.append([sx, sy])
        
        #print(samples)
        return samples

    #para grupos de 3 ou mais pessoas, informar o qtd = n. de pessoas
    def approach_samples_three(p1,p2,p3,xc,yc,rc):
        
        #calculo do P-space (1.10=_radius+personal_space)
        r = rc + 1.10
        #Então calcula o raio de approximação r<rapp<R
        #rapp = r + self.sd/2
        rapp = r + 0.6
            
        samples = []
        x1,y1,th1 = p1.get_coords()
        x2,y2,th2 = p2.get_coords()
        x3,y3,th3 = p3.get_coords()
        
        #Caso F-formatio semi_circle
        if th2==np.deg2rad(-90):
            xs1 = xc
            ys1 = yc - rapp
            samples.append([xs1,ys1])
            xs2 = rapp*np.cos(np.deg2rad(-90)-np.deg2rad(30))+xc
            ys2 = rapp*np.sin(np.deg2rad(-90)-np.deg2rad(30))+yc
            samples.append([xs2,ys2])
            xs3 = rapp*np.cos(np.deg2rad(-90)+np.deg2rad(30))+xc
            ys3 = rapp*np.sin(np.deg2rad(-90)+np.deg2rad(30))+yc
            samples.append([xs3,ys3])
        else:
        #caso F-formation triangular
            xs1 = xc + rapp
            ys1 = yc
            samples.append([xs1,ys1])
            xs2 = rapp * np.cos(th2) + xc
            ys2 = rapp * np.sin(th2) + yc
            samples.append([xs2,ys2])
            xs3 = rapp * np.cos(th3) + xc
            ys3 = rapp * np.sin(th3) + yc
            samples.append([xs3,ys3])
        
        return samples
        
    def approach_samples_four(p1,p2,p3,p4,xc,yc,rc):
        
        #calculo do P-space (1.10=_radius+personal_space)
        r = rc + 1.10
        #Então calcula o raio de approximação r<rapp<R
        #rapp = r + self.sd/2
        rapp = r + 0.6
            
        samples = []
        x1,y1,th1 = p1.get_coords()
        x2,y2,th2 = p2.get_coords()
        x3,y3,th3 = p3.get_coords()
        x4,y4,th4 = p4.get_coords()
        
        xs1 = rapp*np.cos(np.deg2rad(45)) + xc
        ys1 = rapp*np.sin(np.deg2rad(45)) + yc
        samples.append([xs1,ys1])
        xs2 = rapp * np.cos(np.deg2rad(135)) + xc
        ys2 = rapp * np.sin(np.deg2rad(135)) + yc
        samples.append([xs2,ys2])
        xs3 = rapp * np.cos(np.deg2rad(225)) + xc
        ys3 = rapp * np.sin(np.deg2rad(225)) + yc
        samples.append([xs3,ys3])
        xs4 = rapp * np.cos(np.deg2rad(315)) + xc
        ys4 = rapp * np.sin(np.deg2rad(315)) + yc
        samples.append([xs4,ys4])
        
        return samples
    
    def approach_samples_five(p1,p2,p3,p4,p5,xc,yc,rc):
        
        #calculo do P-space (1.10=_radius+personal_space)
        r = rc + 1.10
        #Então calcula o raio de approximação r<rapp<R
        #rapp = r + self.sd/2
        rapp = r + 0.6
            
        samples = []
        x1,y1,th1 = p1.get_coords()
        x2,y2,th2 = p2.get_coords()
        x3,y3,th3 = p3.get_coords()
        x4,y4,th4 = p4.get_coords()
        x5,y5,th5 = p5.get_coords()
        
        xs1 = rapp*np.cos(np.deg2rad(45)) + xc
        ys1 = rapp*np.sin(np.deg2rad(45)) + yc
        samples.append([xs1,ys1])
        xs2 = rapp * np.cos(np.deg2rad(135)) + xc
        ys2 = rapp * np.sin(np.deg2rad(135)) + yc
        samples.append([xs2,ys2])
        xs3 = rapp * np.cos(np.deg2rad(210)) + xc
        ys3 = rapp * np.sin(np.deg2rad(210)) + yc
        samples.append([xs3,ys3])
        xs4 = rapp * np.cos(np.deg2rad(325)) + xc
        ys4 = rapp * np.sin(np.deg2rad(325)) + yc
        samples.append([xs4,ys4])
        
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
        #ax.set_xlim([0, 10])
        #ax.set_ylim([0, 10])
        plt.axis('equal')
        #plt.title('Exemplo teste')
        plt.show()
        #plt.savefig("cena.png",dpi=100)
        
    def draw_formation_3(ax,p1,p2,p3,xc,yc,rc,samples):
         
        fig = plt.figure(figsize=(8,5), dpi=100)
        ax = fig.add_subplot(111, aspect='equal')  
        p1.draw(ax)
        p2.draw(ax)
        p3.draw(ax)
        
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
        #ax.set_xlim([0, 10])
        #ax.set_ylim([0, 10])
        plt.axis('equal')
        #plt.title('Exemplo teste')
        plt.show()

    def draw_formation_4(ax,p1,p2,p3,p4,xc,yc,rc,samples):
         
        fig = plt.figure(figsize=(8,5), dpi=100)
        ax = fig.add_subplot(111, aspect='equal')  
        p1.draw(ax)
        p2.draw(ax)
        p3.draw(ax)
        p4.draw(ax)
        
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
        #ax.set_xlim([0, 10])
        #ax.set_ylim([0, 10])
        plt.axis('equal')
        #plt.title('Exemplo teste')
        plt.show()

    def draw_formation_5(ax,p1,p2,p3,p4,p5,xc,yc,rc,samples):
        
        fig = plt.figure(figsize=(8,5), dpi=100)
        ax = fig.add_subplot(111, aspect='equal')  
        p1.draw(ax)
        p2.draw(ax)
        p3.draw(ax)
        p4.draw(ax)
        p5.draw(ax)
        
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
        #ax.set_xlim([0, 10])
        #ax.set_ylim([0, 10])
        plt.axis('equal')
        #plt.title('Exemplo teste')
        plt.show()
        

def Create_clusters(): #criação manual de uma cena
    
    #criando as representações manualmente!
    
    #caso1 (mesmo x) - face to face
    x1 = 9
    x2 = 9
    y1 = 10
    y2 = 13
    th1 = np.deg2rad(90)
    th2 = np.deg2rad(270)
    p1,p2,xc1,yc1,rc1 = F_formation.Face_to_face(x1,y1,th1,x2,y2,th2)
    samples1 = F_formation.approach_samples(p1,p2,xc1,yc1,rc1)
    
    #caso2 (mesmo y)
    x3 = 1
    x4 = 4
    y3 = 2
    y4 = 2
    th3 = np.deg2rad(0)
    th4 = np.deg2rad(180)
    p3,p4,xc2,yc2,rc2 = F_formation.Face_to_face(x3,y3,th3,x4,y4,th4)
    samples2 = F_formation.approach_samples(p3,p4,xc2,yc2,rc2)
    
    #caso3 (x e y diferentes)
    x5 = 14
    x6 = 17
    y5 = 18
    y6 = 21
    th5 = np.deg2rad(45)
    th6 = np.deg2rad(225)
    p5,p6,xc3,yc3,rc3 = F_formation.Face_to_face(x5,y5,th5,x6,y6,th6)
    samples3 = F_formation.approach_samples(p5,p6,xc3,yc3,rc3)
    
    #caso 4 (L-sheppard)
    x7= 14
    x8= 17
    y7= 5
    y8= 2
    th7 = np.deg2rad(-90)
    th8 = np.deg2rad(180)
    p7,p8,xc4,yc4,rc4 = F_formation.L_shaped(x7,y7,th7,x8,y8,th8)
    samples4 = F_formation.approach_samples(p7,p8,xc4,yc4,rc4)
    
    #caso5 (sibe_by_side)
    x9 = 1
    x10 = 4
    y9 = 13
    y10 = 13
    th9 = np.deg2rad(90)
    th10 = th1
    p9,p10,xc5,yc5,rc5 = F_formation.Side_by_side(x9,y9,th9,x10,y10,th10)
    samples5 = F_formation.approach_samples(p9,p10,xc5,yc5,rc5)
    
    #caso6 (v-shapped)
    x11 = 9
    x12 = 9
    y11 = 2
    y12 = 5
    th11 = np.deg2rad(135)
    th12 = np.deg2rad(225)
    p11,p12,xc6,yc6,rc6 = F_formation.v_shaped(x11,y11,th11,x12,y12,th12)
    samples6 = F_formation.approach_samples(p11,p12,xc6,yc6,rc6)
    
    #caso7 (triangular _3 peoples) '''triangulo isosceles'''
    x13 =3.8
    x14 = 9
    x15 = 9
    y13 = 21
    y14 = 18
    y15 = 24
    th13 = np.deg2rad(0)
    th14 = np.deg2rad(110)
    th15 = np.deg2rad(255)
    p13,p14,p15,xc7,yc7,rc7 = F_formation.triangular(x13,y13,th13,x14,y14,th14,x15,y15,th15)
    samples7 = F_formation.approach_samples_three(p13,p14,p15,xc7,yc7,rc7)
    
    #caso 8 (semi_cicle 3 pessoas)
    xc8 = 3.5
    yc8 = 27
    rc8 = 4
    p16,p17,p18,xc8,yc8,rc8 = F_formation.semi_circle(xc8,yc8,rc8)
    samples8 = F_formation.approach_samples_three(p16,p17,p18,xc8,yc8,rc8)
    
    #caso 9 (retangular 4 peoples)
    x19 = 14
    x20 = 17
    x21 = 20
    x22 = 17
    y19 = 24
    y20 = 21
    y21 = 24
    y22 = 27
    th19 = np.deg2rad(0)
    th20 = np.deg2rad(90)
    th21 = np.deg2rad(180)
    th22 = np.deg2rad(-90)
    p19,p20,p21,p22,xc9,yc9,rc9 = F_formation.retangular(x19,y19,th19,x20,y20,th20,x21,y21,th21,x22,y22,th22)
    samples9 = F_formation.approach_samples_four(p19,p20,p21,p22,xc9,yc9,rc9)
    
    #caso 10 (circuloar 5 peoples)
    xc10 =2
    yc10 =2
    rc10 = 3.5
    p23,p24,p25,p26,p27,xc,yc,rc = F_formation.Circular(xc10,yc10,rc10)
    samples10 = F_formation.approach_samples_five(p23,p24,p25,p26,p27,xc10,yc10,rc10)
    ################################################################
    
    return (p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15,p16,p17,p18,p19,p20,p21,p22,p23,p24,p25,p26,p27,
             xc1,xc2,xc3,xc4,xc5,xc6,xc7,xc8,xc9,xc10,yc1,yc2,yc3,yc4,yc5,yc6,yc7,yc8,yc9,yc10,rc1,rc2,rc3,rc4,
             rc5,rc6,rc7,rc8,rc9,rc10,samples1,samples2,samples3,samples4,samples5,samples6,samples7,samples8,
             samples9,samples10)
    

def DrawCena(p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15,p16,p17,p18,p19,p20,p21,p22,p23,p24,p25,p26,p27,
             xc1,xc2,xc3,xc4,xc5,xc6,xc7,xc8,xc9,xc10,yc1,yc2,yc3,yc4,yc5,yc6,yc7,yc8,yc9,yc10,rc1,rc2,rc3,rc4,
             rc5,rc6,rc7,rc8,rc9,rc10,samples1,samples2,samples3,samples4,samples5,samples6,samples7,samples8,
             samples9,samples10):
    '''plotagem da cena'''
    fig = plt.figure(figsize=(8,5), dpi=100)
    ax = fig.add_subplot(111, aspect='equal')
    
    F_formation.draw_formation(ax,p1,p2,xc1,yc1,rc1,samples1)
    F_formation.draw_formation(ax,p3,p4,xc2,yc2,rc2,samples2)
    F_formation.draw_formation(ax,p5,p6,xc3,yc3,rc3,samples3)
    F_formation.draw_formation(ax,p7,p8,xc4,yc4,rc4,samples4)
    F_formation.draw_formation(ax,p9,p10,xc5,yc5,rc5,samples5)
    F_formation.draw_formation(ax,p11,p12,xc6,yc6,rc6,samples6)
    F_formation.draw_formation_3(ax,p13,p14,p15,xc7,yc7,rc7,samples7)
    F_formation.draw_formation_3(ax,p16,p17,p18,xc8,yc8,rc8,samples8)
    F_formation.draw_formation_4(ax,p19,p20,p21,p22,xc9,yc9,rc9,samples9)
    F_formation.draw_formation_5(ax,p23,p24,p25,p26,p27,xc10,yc10,rc10,samples10)
    
    ax.tick_params(labelsize=6)
    ax.grid(False)
    ax.set_xlim([0, 200])
    ax.set_ylim([0, 200])
    #plt.axis('equal')
    plt.title('Cena inicial')
    plt.show()


#Criação das instâncias para o SOP:
def Instances(samples1,samples2, samples3,samples4,samples5,samples6,samples7,samples8,samples9,samples10,
              xc1,xc2,xc3,xc4,xc5,xc6,xc7,xc8,xc9,xc10,yc1,yc2,yc3,yc4,yc5,yc6,yc7,yc8,yc9,yc10):
    #preciso retornar: (no_id,x,y) de cada sample; (set_id,set_profit,id_vertex_list) para cada cluster
    #os primeiros clusters deves ser o start_point  !!!!!start = end-point!!!!
    #(set_id,xc,yc) para cada cluster
    
    vertex_list = [] # [vertex_id,xv,yv]
    cluster_list = [] # [set_id,set_profit,id_vertex_list]
    central_coords_cluster_list = [] #[set_id,xc,yc]
    
    no_id = 0
    
    #criar start point e and point #cluster0 e cluster1
    xo = -7.5
    yo = 15
    vertex_list.append([no_id,xo,yo])
    set_id = 0
    set_profit = 0
    cluster_list.append([set_id,set_profit,no_id])
    central_coords_cluster_list.append([set_id,xo,yo])
    set_id = set_id +1
    cluster_list.append([set_id,set_profit,no_id])
    central_coords_cluster_list.append([set_id,xo,yo])
    
    id_vertex_list1 = []
    for sample in samples1: #cluster1
        no_id = no_id +1
        vertex_list.append([no_id,sample[0],sample[1]])
        id_vertex_list1.append(no_id)
    set_id = set_id +1
    set_profit = 2 #2 peoples
    cluster_list.append([set_id,set_profit,id_vertex_list1])
    central_coords_cluster_list.append([set_id,xc1,yc1])
    
    id_vertex_list2 = []
    for sample in samples2: #cluster2
        no_id = no_id +1
        vertex_list.append([no_id,sample[0],sample[1]])
        id_vertex_list2.append(no_id)
    set_id = set_id +1
    set_profit = 2
    cluster_list.append([set_id,set_profit,id_vertex_list2])
    central_coords_cluster_list.append([set_id,xc2,yc2])
    
    id_vertex_list3 = []
    for sample in samples3:
        no_id = no_id +1
        vertex_list.append([no_id,sample[0],sample[1]])
        id_vertex_list3.append(no_id)
    set_id = set_id +1
    set_profit = 2
    cluster_list.append([set_id,set_profit,id_vertex_list3])
    central_coords_cluster_list.append([set_id,xc3,yc3])
    
    id_vertex_list4 = []
    for sample in samples4:
        no_id = no_id +1
        vertex_list.append([no_id,sample[0],sample[1]])
        id_vertex_list4.append(no_id)
    set_id = set_id +1
    set_profit = 2
    cluster_list.append([set_id,set_profit,id_vertex_list4])
    central_coords_cluster_list.append([set_id,xc4,yc4])
        
    id_vertex_list5 = []
    for sample in samples5:
        no_id = no_id +1
        vertex_list.append([no_id,sample[0],sample[1]])
        id_vertex_list5.append(no_id)
    set_id = set_id +1
    set_profit = 2
    cluster_list.append([set_id,set_profit,id_vertex_list5])
    central_coords_cluster_list.append([set_id,xc5,yc5])
        
    id_vertex_list6 = []
    for sample in samples6:
        no_id = no_id +1
        vertex_list.append([no_id,sample[0],sample[1]])
        id_vertex_list6.append(no_id)
    set_id = set_id +1
    set_profit = 2
    cluster_list.append([set_id,set_profit,id_vertex_list6])
    central_coords_cluster_list.append([set_id,xc6,yc6])
    
    id_vertex_list7 = []
    for sample in samples7:
        no_id = no_id +1
        vertex_list.append([no_id,sample[0],sample[1]])
        id_vertex_list7.append(no_id)
    set_id = set_id +1
    set_profit = 3 #3 peoples
    cluster_list.append([set_id,set_profit,id_vertex_list7])
    central_coords_cluster_list.append([set_id,xc7,yc7])
    
    id_vertex_list8 = []
    for sample in samples8:
        no_id = no_id +1
        vertex_list.append([no_id,sample[0],sample[1]])
        id_vertex_list8.append(no_id)
    set_id = set_id +1
    set_profit = 3 #3 peoples
    cluster_list.append([set_id,set_profit,id_vertex_list8])
    central_coords_cluster_list.append([set_id,xc8,yc8])
    
    id_vertex_list9 = []
    for sample in samples9:
        no_id = no_id +1
        vertex_list.append([no_id,sample[0],sample[1]])
        id_vertex_list9.append(no_id)
    set_id = set_id +1
    set_profit = 4 #4 peoples
    cluster_list.append([set_id,set_profit,id_vertex_list9])
    central_coords_cluster_list.append([set_id,xc9,yc9])
    
    id_vertex_list10 = []
    for sample in samples10:
        no_id = no_id +1
        vertex_list.append([no_id,sample[0],sample[1]])
        id_vertex_list10.append(no_id)
    set_id = set_id +1
    set_profit = 5 #5 peoples
    cluster_list.append([set_id,set_profit,id_vertex_list10])
    central_coords_cluster_list.append([set_id,xc10,yc10])
    
    return vertex_list, cluster_list, central_coords_cluster_list
    

####################################### Testes#######################################################
def main():
    
    (p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15,p16,p17,p18,p19,p20,p21,p22,p23,p24,p25,p26,p27,
xc1,xc2,xc3,xc4,xc5,xc6,xc7,xc8,xc9,xc10,yc1,yc2,yc3,yc4,yc5,yc6,yc7,yc8,yc9,yc10,rc1,rc2,rc3,rc4,
rc5,rc6,rc7,rc8,rc9,rc10,samples1,samples2,samples3,samples4,samples5,samples6,samples7,samples8,
samples9,samples10) = Create_clusters()

    DrawCena(p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15,p16,p17,p18,p19,p20,p21,p22,p23,p24,p25,p26,p27,
    xc1,xc2,xc3,xc4,xc5,xc6,xc7,xc8,xc9,xc10,yc1,yc2,yc3,yc4,yc5,yc6,yc7,yc8,yc9,yc10,rc1,rc2,rc3,rc4,
    rc5,rc6,rc7,rc8,rc9,rc10,samples1,samples2,samples3,samples4,samples5,samples6,samples7,samples8,samples9,samples10)
    
    vertex_list, cluster_list, central_coords_cluster_list = Instances(samples1,samples2,samples3,samples4,samples5,samples6,samples7,samples8,samples9,samples10,
                                          xc1,xc2,xc3,xc4,xc5,xc6,xc7,xc8,xc9,xc10,yc1,yc2,yc3,yc4,yc5,yc6,yc7,yc8,yc9,yc10)
    
    print('vertex_list:[vertex_id,xv,yv]',vertex_list)
    print('cluster_list:[set_id,set_profit,id_vertex_list]',cluster_list)
    print('central_coords_cluster_list:(set_id,xc,yc)', central_coords_cluster_list)