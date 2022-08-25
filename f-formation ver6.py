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

    _radius = 0.60  # raio do corpo da pessoa
    personal_space = 0.50  # raio da região de personal_space

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
        x_aux = self.x + self._radius * np.cos(self.th)
        y_aux = self.y + self._radius * np.sin(self.th)
        heading = plt.Line2D((self.x, x_aux), (self.y, y_aux), lw=3, color='k')
        ax.add_line(heading)

        # Personal Space
        space = Circle((self.x, self.y), radius=(
            self._radius+self.personal_space), fill=False, ls='--', color='r')
        #ax.add_patch(space)


class F_formation:

    # coordenadas do O-space
    xc = 0
    yc = 0
    rc = 0

    sd = 1.2  # social distance
    """ Public Methods"""

    def __init__(self, sd=1.2):
        self.sd = sd
     #   self.xc = xc
        #  self.yc = yc
       # self.thc = thc

    def Face_to_face(x1, y1, th1, x2, y2, th2):
        # Segundo proxemics a distância entre p1 e p2 deve ser de pelo menos 1 metro

        # Cria um grupo de duas pessoas
        p1 = Person(x1, y1, th1)
        p2 = Person(x2, y2, th2)

        # calcula o raio do O-space
        if x2 == x1:
            rc = (y2-y1)/(np.sin(th1)-np.sin(th2))
        else:
            rc = (x2-x1)/(np.cos(th1)-np.cos(th2))
        # print('rc:',rc)

        # Calcula as coordenadas do centro do O-space
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

        return p1, p2, xc, yc, rc

    def L_shaped(x1, y1, th1, x2, y2, th2):
        # deve-se satisfazer a condição: x1<x2 e y1>y2, e th1=-90 e th2=180, ou ou th2=90 e th1=0

        # Cria um grupo de duas pessoas
        p1 = Person(x1, y1, th1)
        p2 = Person(x2, y2, th2)

        # calcula o raio do O-space
        rc = (y1-y2)
       #print('rc', rc)

        # Determina as coordenadas do centro do O-space
        if th1 == np.deg2rad(-90):
            xc = x1
            yc = y2
        else:
            if th2 == np.deg2rad(90):
                xc = x2
                yc = y1

        return p1, p2, xc, yc, rc

    def Side_by_side(x1, y1, th1, x2, y2, th2):
        # x1<x2; y1=y2; th1=th2=90 ou -90

        # Cria um grupo de duas pessoas
        p1 = Person(x1, y1, th1)
        p2 = Person(x2, y2, th2)

        # Determina as coordenadas do centro do O-space
        xc = (x2-x1)/2 + x1
        yc = y1 + (xc-x1)*np.tan(np.deg2rad(45))

        # calcula o raio do O-space
        rc = (yc - y1)/np.cos(np.deg2rad(45))

        return p1, p2, xc, yc, rc

    def v_shaped(x1, y1, th1, x2, y2, th2):
        # x1=x2; y2>y1; th1 = 135 e th2 = 225

        # Cria um grupo de duas pessoas
        p1 = Person(x1, y1, th1)
        p2 = Person(x2, y2, th2)

        # Determina as coordenadas do centro do O-space
        xc = x1 + (x2-x1)/2
        yc = y1 + (y2-y1)/2

        # calcula o raio do O-space
        rc = (yc-y1)

        return p1, p2, xc, yc, rc

    def triangular(x1, y1, th1, x2, y2, th2, x3, y3, th3):
        # grupo com 3 pessoas formato triangular
        # x1<x2=x3; y2<y1<y3 th1=0, th2=110, th3=255

        # Cria um grupo de três pessoas
        p1 = Person(x1, y1, th1)
        p2 = Person(x2, y2, th2)
        p3 = Person(x3, y3, th3)

        # Determina as coordenadas do centro do O-space
        # baricentro
        xc = (x1 + x2 + x3)/3
        yc = (y1 + y2 + y3)/3

        # calcula o raio do O-space
        # usando propriedades do triangulo isosceles
        rc = math.sqrt(((xc-x1)**2+(yc-y1)**2))

        return p1, p2, p3, xc, yc, rc
    
    def triang_eq(x1, y1, th1, x2, y2, th2, x3, y3, th3):
        
        # Cria um grupo de três pessoas
        p1 = Person(x1, y1, th1)
        p2 = Person(x2, y2, th2)
        p3 = Person(x3, y3, th3)
        
        # Determina as coordenadas do centro do O-space
        xc = x3
        yc = (y3-y1)/3 + y1
        
        # calcula o raio do O-space
        rc = (2*(y3-y1))/3
        
        return p1, p2, p3, xc, yc, rc

    def semi_circle(xc, yc, rc):
        # people have the same point of observation
        num=3
        ps = []
        temp=[]
        angles = np.linspace(np.deg2rad(0), np.deg2rad(180), num)
        #print(angles)
        for angle in angles:
            sx = rc * np.cos(angle) + xc
            sy = rc * np.sin(angle) + yc
            ps.append([sx,sy,(np.deg2rad(180)+angle)])
        
        for coords in ps:
            coord=coords
            temp.append(coord)
        #print(temp)
        pe1 = temp[0]
        p1 = Person(pe1[0],pe1[1],pe1[2])
        pe2 = temp[1]
        p2 = Person(pe2[0],pe2[1],pe2[2])
        pe3 = temp[2]
        p3 = Person(pe3[0],pe3[1],pe3[2])

        return p1, p2, p3, xc, yc, rc

    def retangular(x1, y1, th1, x2, y2, th2, x3, y3, th3, x4, y4, th4):
        # formation for 4 people

        # Cria um grupo de duas pessoas
        p1 = Person(x1, y1, th1)
        p2 = Person(x2, y2, th2)
        p3 = Person(x3, y3, th3)
        p4 = Person(x4, y4, th4)

        # Determina as coordenadas do centro do O-space
        xc = x2 = x4
        yc = y1 = y3

        # calcula o raio do O-space
        rc = xc-x1

        return p1, p2, p3, p4, xc, yc, rc
    
    def Circular(xc, yc, rc):

        num=5
        ps = []
        temp=[]
        angles = np.linspace(np.deg2rad(0), np.deg2rad(300), num)
        #print(angles)
        for angle in angles:
            sx = rc * np.cos(angle) + xc
            sy = rc * np.sin(angle) + yc
            ps.append([sx,sy,(np.deg2rad(180)+angle)])
        
        for coords in ps:
            coord=coords
            temp.append(coord)
        #print(temp)
        pe1 = temp[0]
        p1 = Person(pe1[0],pe1[1],pe1[2])
        pe2 = temp[1]
        p2 = Person(pe2[0],pe2[1],pe2[2])
        pe3 = temp[2]
        p3 = Person(pe3[0],pe3[1],pe3[2])
        pe4 = temp[3]
        p4 = Person(pe4[0],pe4[1],pe4[2])
        pe5 = temp[4]
        p5 = Person(pe5[0],pe5[1],pe5[2])
        
        
        
        return  p1, p2, p3, p4, p5, xc, yc, rc

    # num é o número de approach em frente
    def approach_samples(p1, p2, xc, yc, rc, num=2):
        # relativa ao centro do O-sapce exceto o approach central. ]
        # Ou seja Número total de targets = num + 2 #Vou fixar em 3 targets por grupo
        # calcula o raio do P-space r e de R-space R, em seguida define a posição dos approach samples.
        # best approach sample posicionado dentro do R-space com o raio passando pelo ponto (xc,yc)
        # demais samples entre -45 e +45 ao redor dele

        # calculo do P-space (1.10=_radius+personal_space)
        r = rc + 1.10

        # Então calcula o raio de approximação r<rapp<R
        #rapp = r + self.sd/2
        rapp = r + 0.6

        samples = []
        x1, y1, th1 = p1.get_coords()
        x2, y2, th2 = p2.get_coords()
        # para a maioria dos casos, excessões são calculadas ou atribuidas localmente
        thc = th1 + np.deg2rad(90)

        # calculo das coordenadas do Best approach sample (Máximo ou Mínimo Reward conforme cada caso)
        if y2 == y1:  #  side by side
            if th1==th2:
                xs1 = xc
                ys1 = rapp + yc
                samples.append([xs1, ys1])
            else: #face to face horizontal
                xs1 = xc
                ys1 = rapp + yc
                samples.append([xs1, ys1])
                minang = -35
                maxang = 35
                num = 3
                angles = np.linspace(np.deg2rad(minang), np.deg2rad(maxang), num)
                for angle in angles:
                    sx = rapp * np.cos(np.deg2rad(-90) + angle) + xc
                    sy = rapp * np.sin(np.deg2rad(-90) + angle) + yc
                    samples.append([sx, sy])
        else:  #  face to face vertical
            if x1 == x2:
                if th1==np.deg2rad(90):
                    ys1 = yc
                    xs1 = xc - rapp
                    samples.append([xs1, ys1])
                    minang = -35
                    maxang = 35
                    num = 3
                    angles = np.linspace(np.deg2rad(minang), np.deg2rad(maxang), num)
                    for angle in angles:
                        sx = rapp * np.cos(np.deg2rad(0) + angle) + xc
                        sy = rapp * np.sin(np.deg2rad(0) + angle) + yc
                        samples.append([sx, sy])
                else: #v-sheppard
                    ys1 = yc
                    xs1 = xc - rapp
                    samples.append([xs1, ys1])
            else:  # se L-shaped
                if (x2 > x1) & (y1 > y2):
                    thc = np.deg2rad(45)
                    xs1 = xc - rapp * np.sin(thc)
                    ys1 = yc - rapp * np.cos(thc)
                    samples.append([xs1, ys1])

                else:  # face to face transversal
                    thc = th1+np.deg2rad(90)
                    xs1 = xc - rapp*np.cos(th1+np.deg2rad(90))
                    ys1 = yc - rapp*np.sin(th1+np.deg2rad(90))
                    samples.append([xs1, ys1])
                    minang = -35
                    maxang = 35
                    num = 3
                    angles = np.linspace(np.deg2rad(minang), np.deg2rad(maxang), num)
                    for angle in angles:
                        sx = rapp * np.cos(thc + angle) + xc
                        sy = rapp * np.sin(thc + angle) + yc
                        samples.append([sx, sy])

        # definindo mais approach samples:
        minang = -35
        maxang = 35
        angles = np.linspace(np.deg2rad(minang), np.deg2rad(maxang), num)
        for angle in angles:  # encontra os approach-points de frente para o centro do O-space
            if (x2 > x1) & (y1 > y2):
                thc = np.deg2rad(225)
            else:
                if th1 == th2:
                    thc = th1
                else:
                    if (th2-th1) == np.deg2rad(90):
                        thc = np.deg2rad(180)
                    else:
                        if (y2 > y1) and (th1 == np.deg2rad(45)):
                            thc = np.deg2rad(315)

            sx = rapp * np.cos(thc + angle) + xc
            sy = rapp * np.sin(thc + angle) + yc
            samples.append([sx, sy])

        # print(samples)
        return samples

    # para grupos de 3 ou mais pessoas, informar o qtd = n. de pessoas
    def approach_samples_three(p1, p2, p3, xc, yc, rc):

        # calculo do P-space (1.10=_radius+personal_space)
        r = rc + 1.10
        # Então calcula o raio de approximação r<rapp<R
        #rapp = r + self.sd/2
        rapp = r + 0.6

        samples = []
        x1, y1, th1 = p1.get_coords()
        x2, y2, th2 = p2.get_coords()
        x3, y3, th3 = p3.get_coords()

        # Caso F-formatio semi_circle
        if th2 == np.deg2rad(270):
            num= 5
            angles= np.linspace(np.deg2rad(-45), np.deg2rad(45), num)
            #print(angles)
            for angle in angles:
                xs = rapp*np.cos(th2 + angle)+xc
                ys = rapp*np.sin(th2 + angle)+yc
                samples.append([xs, ys])
                #print(samples)
        else: #caso triangulo isosceles
            if th1==np.deg2rad(0):
                xs = rapp*np.cos(th2-np.deg2rad(25))+xc
                ys = rapp*np.sin(th2-np.deg2rad(25))+yc
                samples.append([xs, ys])
                sx = rapp*np.cos(th3+np.deg2rad(25))+xc
                sy = rapp*np.sin(th3+np.deg2rad(25))+yc
                samples.append([sx,sy])

            else:
            # caso F-formation triangulo equilatero
                xs1 = rapp * np.cos(th1) + xc
                ys1 = rapp * np.sin(th1) + yc
                samples.append([xs1, ys1])
                xs2 = rapp * np.cos(th2) + xc
                ys2 = rapp * np.sin(th2) + yc
                samples.append([xs2, ys2])
                xs3 = rapp * np.cos(th3) + xc
                ys3 = rapp * np.sin(th3) + yc
                samples.append([xs3, ys3])

        return samples

    def approach_samples_four(p1, p2, p3, p4, xc, yc, rc):

        # calculo do P-space (1.10=_radius+personal_space)
        r = rc + 1.10
        # Então calcula o raio de approximação r<rapp<R
        #rapp = r + self.sd/2
        rapp = r + 0.6

        samples = []
        x1, y1, th1 = p1.get_coords()
        x2, y2, th2 = p2.get_coords()
        x3, y3, th3 = p3.get_coords()
        x4, y4, th4 = p4.get_coords()

        xs1 = rapp*np.cos(np.deg2rad(45)) + xc
        ys1 = rapp*np.sin(np.deg2rad(45)) + yc
        samples.append([xs1, ys1])
        xs2 = rapp * np.cos(np.deg2rad(135)) + xc
        ys2 = rapp * np.sin(np.deg2rad(135)) + yc
        samples.append([xs2, ys2])
        xs3 = rapp * np.cos(np.deg2rad(225)) + xc
        ys3 = rapp * np.sin(np.deg2rad(225)) + yc
        samples.append([xs3, ys3])
        xs4 = rapp * np.cos(np.deg2rad(315)) + xc
        ys4 = rapp * np.sin(np.deg2rad(315)) + yc
        samples.append([xs4, ys4])

        return samples

    def approach_samples_five(p1, p2, p3, p4, p5, xc, yc, rc):

        # calculo do P-space (1.10=_radius+personal_space)
        r = rc + 1.10
        # Então calcula o raio de approximação r<rapp<R
        #rapp = r + self.sd/2
        rapp = r + 0.6

        samples = []
        x1, y1, th1 = p1.get_coords()
        x2, y2, th2 = p2.get_coords()
        x3, y3, th3 = p3.get_coords()
        x4, y4, th4 = p4.get_coords()
        x5, y5, th5 = p5.get_coords()

        xs1 = rapp*np.cos(th1) + xc
        ys1 = rapp*np.sin(th1) + yc
        samples.append([xs1, ys1])
        xs2 = rapp * np.cos(th2) + xc
        ys2 = rapp * np.sin(th2) + yc
        samples.append([xs2, ys2])
        xs3 = rapp * np.cos(th3) + xc
        ys3 = rapp * np.sin(th3) + yc
        samples.append([xs3, ys3])
        xs4 = rapp * np.cos(th4) + xc
        ys4 = rapp * np.sin(th4) + yc
        samples.append([xs4, ys4])
        xs5 = rapp * np.cos(th5) + xc
        ys5 = rapp * np.sin(th5) + yc
        samples.append([xs5, ys5])

        return samples
    
    def approach_samples_one(p,xc,yc,rc):
        
        # calculo do P-space (=personal_space)
        r = rc + 0.6
        # Então calcula o raio de approximação r<rapp<R
        #rapp = r + self.sd/2
        rapp = r + 1.10
        
        samples = []
        (x,y,th)= p.get_coords()
        num= 5
        angles = np.linspace(np.deg2rad(-90), np.deg2rad(90), num)
        for angle in angles:
            sx = rapp * np.cos(th + angle) + x
            sy = rapp* np.sin(th + angle) + y
            samples.append([sx,sy])
        
        return samples

    def draw_formation(ax, p1, p2, xc, yc, rc, samples):

        fig = plt.figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111, aspect='equal')
        p1.draw(ax)
        p2.draw(ax)

        # P_Space
        pspace = Circle((xc, yc), radius=(rc + 1.10),
                        fill=False, ls='--', color='b')
        ax.add_patch(pspace)

        # R_Space
        # calculo do R-space
        R = rc + 2.20  # 1.10 + 1.20 #R= r + sd
        Rspace = Circle((xc, yc), radius=R, fill=False, ls='--', color='g')
        ax.add_patch(Rspace)

        for sample in samples:
            ax.scatter(sample[0], sample[1])
            
        ax.scatter(xc,yc)

        ax.tick_params(labelsize=12)
        ax.grid(False)
        #ax.set_xlim([0, 10])
        #ax.set_ylim([0, 10])
        # plt.axis('equal')
        #plt.title('Exemplo teste')
        # plt.show()
        # plt.savefig("cena.png",dpi=100)
        
    def draw_formation_one(ax,p,xc,yc,rc,samples):
            
        fig = plt.figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111, aspect='equal')
        
        p.draw(ax)

        # P_Space
        pspace = Circle((xc, yc), radius=(rc + 1.10),
                        fill=False, ls='--', color='b')
        ax.add_patch(pspace)

        # R_Space
        # calculo do R-space
        R = rc + 2.20  # 1.10 + 1.20 #R= r + sd
        Rspace = Circle((xc, yc), radius=R, fill=False, ls='--', color='g')
        ax.add_patch(Rspace)

        for sample in samples:
            ax.scatter(sample[0], sample[1])

        ax.tick_params(labelsize=12)
        ax.grid(False)
        #ax.set_xlim([0, 10])
        #ax.set_ylim([0, 10])
        # plt.axis('equal')
        #plt.title('Exemplo teste')
        # plt.show()
        # plt.savefig("cena.png",dpi=100)


    def draw_formation_3(ax, p1, p2, p3, xc, yc, rc, samples):

        fig = plt.figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111, aspect='equal')
        p1.draw(ax)
        p2.draw(ax)
        p3.draw(ax)

        # P_Space
        pspace = Circle((xc, yc), radius=(rc + 1.10),
                        fill=False, ls='--', color='b')
        ax.add_patch(pspace)

        # R_Space
        # calculo do R-space
        R = rc + 2.20  # 1.10 + 1.20 #R= r + sd
        Rspace = Circle((xc, yc), radius=R, fill=False, ls='--', color='g')
        ax.add_patch(Rspace)

        for sample in samples:
            ax.scatter(sample[0], sample[1])

        ax.tick_params(labelsize=12)
        ax.grid(False)
        #ax.set_xlim([0, 10])
        #ax.set_ylim([0, 10])
        # plt.axis('equal')
        #plt.title('Exemplo teste')
        # plt.show()

    def draw_formation_4(ax, p1, p2, p3, p4, xc, yc, rc, samples):

        fig = plt.figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111, aspect='equal')
        p1.draw(ax)
        p2.draw(ax)
        p3.draw(ax)
        p4.draw(ax)

        # P_Space
        pspace = Circle((xc, yc), radius=(rc + 1.10),
                        fill=False, ls='--', color='b')
        ax.add_patch(pspace)

        # R_Space
        # calculo do R-space
        R = rc + 2.20  # 1.10 + 1.20 #R= r + sd
        Rspace = Circle((xc, yc), radius=R, fill=False, ls='--', color='g')
        ax.add_patch(Rspace)

        for sample in samples:
            ax.scatter(sample[0], sample[1])

        ax.tick_params(labelsize=12)
        ax.grid(False)
        #ax.set_xlim([0, 10])
        #ax.set_ylim([0, 10])
        plt.axis('equal')
        #plt.title('Exemplo teste')
        # plt.show()

    def draw_formation_5(ax, p1, p2, p3, p4, p5, xc, yc, rc,samples):

        fig = plt.figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111, aspect='equal')
        p1.draw(ax)
        p2.draw(ax)
        p3.draw(ax)
        p4.draw(ax)
        p5.draw(ax)

        # P_Space
        pspace = Circle((xc, yc), radius=(rc + 1.10),
                        fill=False, ls='--', color='b')
        ax.add_patch(pspace)

        # R_Space
        # calculo do R-space
        R = rc + 2.20  # 1.10 + 1.20 #R= r + sd
        Rspace = Circle((xc, yc), radius=R, fill=False, ls='--', color='g')
        ax.add_patch(Rspace)

        for sample in samples:
            ax.scatter(sample[0], sample[1])

        ax.tick_params(labelsize=12)
        ax.grid(False)
        #ax.set_xlim([0, 10])
        #ax.set_ylim([0, 10])
        # plt.axis('equal')
        #plt.title('Exemplo teste')
        # plt.show()


def Create_clusters():  # criação manual de uma cena

    # criando as representações manualmente!

    # caso1 (mesmo x) - face to face
    x1 = 13
    x2 = 13
    y1 = 9.8
    y2 = 12
    th1 = np.deg2rad(90)
    th2 = np.deg2rad(270)
    p1, p2, xc1, yc1, rc1 = F_formation.Face_to_face(x1, y1, th1, x2, y2, th2)
    samples1 = F_formation.approach_samples(p1, p2, xc1, yc1, rc1)

    # caso2 (mesmo y)
    x3 = -12
    x4 = -9.8
    y3 = 4
    y4 = 4
    th3 = np.deg2rad(0)
    th4 = np.deg2rad(180)
    p3, p4, xc2, yc2, rc2 = F_formation.Face_to_face(x3, y3, th3, x4, y4, th4)
    samples2 = F_formation.approach_samples(p3, p4, xc2, yc2, rc2)

    # caso3 (x e y diferentes)
    x5 = 25
    x6 = 26.6
    y5 = 18
    y6 = 19.6
    th5 = np.deg2rad(45)
    th6 = np.deg2rad(225)
    p5, p6, xc3, yc3, rc3 = F_formation.Face_to_face(x5, y5, th5, x6, y6, th6)
    samples3 = F_formation.approach_samples(p5, p6, xc3, yc3, rc3)

    # caso 4 (L-sheppard)
    x7 = 26
    x8 = 27.6
    y7 = 3.6
    y8 = 2
    th7 = np.deg2rad(-90)
    th8 = np.deg2rad(180)
    p7, p8, xc4, yc4, rc4 = F_formation.L_shaped(x7, y7, th7, x8, y8, th8)
    samples4 = F_formation.approach_samples(p7, p8, xc4, yc4, rc4)

    #caso5 (sibe_by_side)
    x9 = -1
    x10 = 1.2
    y9 = 10
    y10 =10
    th9 = np.deg2rad(90)
    th10 = th1
    p9, p10, xc5, yc5, rc5 = F_formation.Side_by_side(
        x9, y9, th9, x10, y10, th10)
    samples5 = F_formation.approach_samples(p9, p10, xc5, yc5, rc5)

    #caso6 (v-shapped)
    x11 = 15
    x12 = 15
    y11 = 0
    y12 = 2.2
    th11 = np.deg2rad(135)
    th12 = np.deg2rad(225)
    p11, p12, xc6, yc6, rc6 = F_formation.v_shaped(
        x11, y11, th11, x12, y12, th12)
    samples6 = F_formation.approach_samples(p11, p12, xc6, yc6, rc6)

    # caso7 (triangular _3 peoples) '''triangulo isosceles'''
    x13 = 2
    x14 = 5
    x15 = 5
    y13 = 19.1
    y14 = 18
    y15 = 20.2
    th13 = np.deg2rad(0)
    th14 = np.deg2rad(135)
    th15 = np.deg2rad(225)
    p13, p14, p15, xc7, yc7, rc7 = F_formation.triangular(
        x13, y13, th13, x14, y14, th14, x15, y15, th15)
    samples7 = F_formation.approach_samples_three(p13, p14, p15, xc7, yc7, rc7)

    # caso 8 (semi_circle 3 pessoas)
    xc8 = -4.5
    yc8 = 27
    rc8 = 1.5
    p16, p17, p18, xc8, yc8, rc8 = F_formation.semi_circle(xc8, yc8, rc8)
    samples8 = F_formation.approach_samples_three(p16, p17, p18, xc8, yc8, rc8)

    # caso 9 (retangular 4 peoples)
    x19 = 16
    x20 = 17.5
    x21 = 19
    x22 = 17.5
    y19 = 24.5
    y20 = 23
    y21 = 24.5
    y22 = 26
    th19 = np.deg2rad(0)
    th20 = np.deg2rad(90)
    th21 = np.deg2rad(180)
    th22 = np.deg2rad(-90)
    p19, p20, p21, p22, xc9, yc9, rc9 = F_formation.retangular(
        x19, y19, th19, x20, y20, th20, x21, y21, th21, x22, y22, th22)
    samples9 = F_formation.approach_samples_four(
        p19, p20, p21, p22, xc9, yc9, rc9)

    # caso 10 (circular 5 peoples)
    xc10 = 2
    yc10 = 2
    rc10 = 2.2
    p23, p24, p25, p26, p27, xc, yc, rc = F_formation.Circular(
        xc10, yc10, rc10)
    samples10 = F_formation.approach_samples_five(p23, p24, p25, p26, p27, xc10, yc10, rc10)
    
    #caso 11 (grupos de um único indivíduo)
    x23 = 28
    y23 = 28
    th23 = np.deg2rad(-90)
    p28 = Person(x23,y23,th23)
    xc11 = x23
    yc11 = y23
    rc11 = 0
    samples11 = F_formation.approach_samples_one(p28,xc11,yc11,rc11)
    x24 = -5
    y24 = 0
    th24 = np.deg2rad(30)
    p29 = Person(x24,y24,th24)
    xc12 = x24
    yc12 = y24
    rc12 = 0
    samples12 = F_formation.approach_samples_one(p29,xc12,yc12,rc12)
    x25 = 8
    y25 = 28
    th25 = np.deg2rad(180)
    p30 = Person(x25,y25,th25)
    xc13 = x25
    yc13 = y25
    rc13 = 0
    samples13 = F_formation.approach_samples_one(p30,xc13,yc13,rc13)
    
    #caso 12 (triangular - triangulo equilátero)
    x26 = -16
    x27 = -13
    x28 = -14.5
    y26 = 20
    y27 = 20
    y28 = 22.25
    th26 = np.deg2rad(45)
    th27 = np.deg2rad(135)
    th28 = np.deg2rad(-90)
    p31, p32, p33, xc14, yc14, rc14 = F_formation.triang_eq(x26, y26, th26, x27, y27, th27, x28, y28, th28)
    samples14 = F_formation.approach_samples_three(p31, p32, p33, xc14, yc14, rc14)
    

    return (p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23, p24, p25, p26, p27,p28,p29,p30,p31,p32,p33,
            xc1, xc2, xc3, xc4, xc5, xc6, xc7, xc8, xc9, xc10, xc11, xc12, xc13, xc14, yc1, yc2, yc3, yc4, yc5, yc6, yc7, yc8, yc9, yc10, yc11, yc12, yc13, yc14, rc1, rc2, rc3, rc4,
            rc5, rc6, rc7, rc8, rc9, rc10, rc11, rc12, rc13, rc14, samples1, samples2, samples3, samples4, samples5, samples6, samples7, samples8,
            samples9,samples10,samples11,samples12,samples13,samples14)


def DrawCena(p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23, p24, p25, p26, p27,p28,p29,p30,p31,p32,p33,
             xc1, xc2, xc3, xc4, xc5, xc6, xc7, xc8, xc9, xc10, xc11, xc12, xc13, xc14, yc1, yc2, yc3, yc4, yc5, yc6, yc7, yc8, yc9, yc10, yc11, yc12, yc13, yc14, rc1, rc2, rc3, rc4,
             rc5, rc6, rc7, rc8, rc9, rc10, rc11, rc12, rc13, rc14, samples1, samples2, samples3, samples4, samples5, samples6, samples7, samples8,
             samples9,samples10,samples11,samples12,samples13,samples14):
    '''plotagem da cena'''
    plt.close('all')
    # matplotlib.style.use('classic')
    fig = plt.figure(figsize=(8, 5), dpi=100)
    ax = fig.add_subplot(111, aspect='equal')

    ax.scatter(-13, 15)  # start_point

    F_formation.draw_formation(ax, p1, p2, xc1, yc1, rc1, samples1)
    F_formation.draw_formation(ax, p3, p4, xc2, yc2, rc2, samples2)
    F_formation.draw_formation(ax, p5, p6, xc3, yc3, rc3, samples3)
    F_formation.draw_formation(ax, p7, p8, xc4, yc4, rc4, samples4)
    F_formation.draw_formation(ax, p9, p10, xc5, yc5, rc5, samples5)
    F_formation.draw_formation(ax, p11, p12, xc6, yc6, rc6, samples6)
    F_formation.draw_formation_3(ax, p13, p14, p15, xc7, yc7, rc7, samples7)
    F_formation.draw_formation_3(ax, p16, p17, p18, xc8, yc8, rc8, samples8)
    F_formation.draw_formation_4(ax, p19, p20, p21, p22, xc9, yc9, rc9, samples9)
    F_formation.draw_formation_5(ax, p23, p24, p25, p26, p27, xc10, yc10, rc10,samples10)
    F_formation.draw_formation_one(ax,p28,xc11,yc11,rc11,samples11)
    F_formation.draw_formation_one(ax,p29,xc12,yc12,rc12,samples12)
    F_formation.draw_formation_one(ax,p30,xc13,yc13,rc13,samples13)
    F_formation.draw_formation_3(ax, p31, p32, p33, xc14, yc14, rc14, samples14)

    ax.tick_params(labelsize=12)
    ax.grid(False)
    ax.set_xlim([-10, 35])
    ax.set_ylim([-10, 35])
    plt.axis('equal')
    #plt.title('Cena inicial')
    plt.show()


# Criação das instâncias para o SOP:
def Instances(samples1, samples2, samples3, samples4, samples5, samples6, samples7, samples8, samples9, samples10,samples11,samples12,samples13,samples14,
              xc1, xc2, xc3, xc4, xc5, xc6, xc7, xc8, xc9, xc10, xc11,xc12,xc13,xc14,yc1, yc2, yc3, yc4, yc5, yc6, yc7, yc8, yc9, yc10,yc11,yc12,yc13,yc14,
              rc1, rc2, rc3, rc4, rc5, rc6, rc7, rc8, rc9, rc10, rc11, rc12, rc13, rc14):
    # preciso retornar: (no_id,x,y) de cada sample; (set_id,set_profit,id_vertex_list) para cada cluster
    # os primeiros clusters deves ser o start_point  !!!!!start = end-point!!!!
    # (set_id,xc,yc) para cada cluster

    vertex_list = []  # [vertex_id,xv,yv]
    cluster_list = []  # [set_id,set_profit,id_vertex_list]
    central_coords_cluster_list = []  # [set_id,xc,yc,rc]

    no_id = 1

    # criar start point e and point #cluster0 e cluster1
    xo = -13
    yo = 13
    vertex_list.append([no_id, xo, yo])
    set_id = 0
    set_profit = 0
    cluster_list.append([set_id, set_profit, [no_id]])
    central_coords_cluster_list.append([set_id, xo, yo, 0])
    set_id = set_id + 1
    cluster_list.append([set_id, set_profit, [no_id]])
    central_coords_cluster_list.append([set_id, xo, yo, 0])

    id_vertex_list1 = []
    for sample in samples1:  # cluster1
        no_id = no_id + 1
        vertex_list.append([no_id, sample[0], sample[1]])
        id_vertex_list1.append(no_id)
    set_id = set_id + 1
    set_profit = 2  # 2 peoples
    cluster_list.append([set_id, set_profit, id_vertex_list1])
    central_coords_cluster_list.append([set_id, xc1, yc1, rc1])

    id_vertex_list2 = []
    for sample in samples2:  # cluster2
        no_id = no_id + 1
        vertex_list.append([no_id, sample[0], sample[1]])
        id_vertex_list2.append(no_id)
    set_id = set_id + 1
    set_profit = 2
    cluster_list.append([set_id, set_profit, id_vertex_list2])
    central_coords_cluster_list.append([set_id, xc2, yc2, rc2])

    id_vertex_list3 = []
    for sample in samples3:
        no_id = no_id + 1
        vertex_list.append([no_id, sample[0], sample[1]])
        id_vertex_list3.append(no_id)
    set_id = set_id + 1
    set_profit = 2
    cluster_list.append([set_id, set_profit, id_vertex_list3])
    central_coords_cluster_list.append([set_id, xc3, yc3, rc3])

    id_vertex_list4 = []
    for sample in samples4:
        no_id = no_id + 1
        vertex_list.append([no_id, sample[0], sample[1]])
        id_vertex_list4.append(no_id)
    set_id = set_id + 1
    set_profit = 2
    cluster_list.append([set_id, set_profit, id_vertex_list4])
    central_coords_cluster_list.append([set_id, xc4, yc4, rc4])

    id_vertex_list5 = []
    for sample in samples5:
        no_id = no_id + 1
        vertex_list.append([no_id, sample[0], sample[1]])
        id_vertex_list5.append(no_id)
    set_id = set_id + 1
    set_profit = 2
    cluster_list.append([set_id, set_profit, id_vertex_list5])
    central_coords_cluster_list.append([set_id, xc5, yc5, rc5])

    id_vertex_list6 = []
    for sample in samples6:
        no_id = no_id + 1
        vertex_list.append([no_id, sample[0], sample[1]])
        id_vertex_list6.append(no_id)
    set_id = set_id + 1
    set_profit = 2
    cluster_list.append([set_id, set_profit, id_vertex_list6])
    central_coords_cluster_list.append([set_id, xc6, yc6, rc6])

    id_vertex_list7 = []
    for sample in samples7:
        no_id = no_id + 1
        vertex_list.append([no_id, sample[0], sample[1]])
        id_vertex_list7.append(no_id)
    set_id = set_id + 1
    set_profit = 3  # 3 peoples
    cluster_list.append([set_id, set_profit, id_vertex_list7])
    central_coords_cluster_list.append([set_id, xc7, yc7, rc7])

    id_vertex_list8 = []
    for sample in samples8:
        no_id = no_id + 1
        vertex_list.append([no_id, sample[0], sample[1]])
        id_vertex_list8.append(no_id)
    set_id = set_id + 1
    set_profit = 3  # 3 peoples
    cluster_list.append([set_id, set_profit, id_vertex_list8])
    central_coords_cluster_list.append([set_id, xc8, yc8, rc8])

    id_vertex_list9 = []
    for sample in samples9:
        no_id = no_id + 1
        vertex_list.append([no_id, sample[0], sample[1]])
        id_vertex_list9.append(no_id)
    set_id = set_id + 1
    set_profit = 4  # 4 peoples
    cluster_list.append([set_id, set_profit, id_vertex_list9])
    central_coords_cluster_list.append([set_id, xc9, yc9, rc9])

    id_vertex_list10 = []
    for sample in samples10:
        no_id = no_id + 1
        vertex_list.append([no_id, sample[0], sample[1]])
        id_vertex_list10.append(no_id)
    set_id = set_id + 1
    set_profit = 5  # 5 peoples
    cluster_list.append([set_id, set_profit, id_vertex_list10])
    central_coords_cluster_list.append([set_id, xc10, yc10, rc10])
    
    id_vertex_list11 = []
    for sample in samples11:
        no_id = no_id + 1
        vertex_list.append([no_id, sample[0], sample[1]])
        id_vertex_list11.append(no_id)
    set_id = set_id + 1
    set_profit = 1  # 1 people
    cluster_list.append([set_id, set_profit, id_vertex_list11])
    central_coords_cluster_list.append([set_id, xc11, yc11, rc11])
    
    id_vertex_list12 = []
    for sample in samples12:
        no_id = no_id + 1
        vertex_list.append([no_id, sample[0], sample[1]])
        id_vertex_list12.append(no_id)
    set_id = set_id + 1
    set_profit = 1  # 1 people
    cluster_list.append([set_id, set_profit, id_vertex_list12])
    central_coords_cluster_list.append([set_id, xc12, yc12, rc12])
    
    id_vertex_list13 = []
    for sample in samples13:
        no_id = no_id + 1
        vertex_list.append([no_id, sample[0], sample[1]])
        id_vertex_list13.append(no_id)
    set_id = set_id + 1
    set_profit = 1  # 1 people
    cluster_list.append([set_id, set_profit, id_vertex_list13])
    central_coords_cluster_list.append([set_id, xc13, yc13, rc13])
    
    id_vertex_list14 = []
    for sample in samples14:
        no_id = no_id + 1
        vertex_list.append([no_id, sample[0], sample[1]])
        id_vertex_list14.append(no_id)
    set_id = set_id + 1
    set_profit = 3  # 3 peoples
    cluster_list.append([set_id, set_profit, id_vertex_list14])
    central_coords_cluster_list.append([set_id, xc14, yc14, rc14])

    return vertex_list, cluster_list, central_coords_cluster_list

##### Aplicando restrições sociais#####


def Bound_box(central_coords_cluster_list):
    # Cria box invisiveis ao redor do P_space transformando a região em obstáculo (obs_set)
    # Cria box invisiveis ao redor do R_space (valid_box) evitando criação de samples (amostras aleatórias) nesta região
    valid_box = []
    obs_set = []
    for coords in central_coords_cluster_list:
        xc = coords[1]
        yc = coords[2]
        rc = coords[3]
        # P_Space
        a = rc + 1.10
        pspace = Point([xc, yc]).buffer(a+0.5)
        obs_set.append(pspace)
        # R_Space
        # calculo do R-space
        R = rc + 2.20  # 1.10 + 1.20 #R= r + sd
        Rspace = Point([xc, yc]).buffer(R+0.5)
        valid_box.append(Rspace)
    #print(obs_set)
    del(obs_set[0]) #remove P-space do start point
    del(obs_set[0]) #remove P-space do end point
    del(valid_box[0])
    #del(valid_box[0])
    #print(obs_set)
    obstaculo = []
    # Cria obstáculos na cena
    obs1 = Polygon([(-10, 11.5), (-10, 17), (-6, 17)])
    obs2 = Point([20, 15]).buffer(2)
    obs3 = Polygon([(10,16),(12,16),(12,24),(10,24)])
    obs4 = Polygon([(8,-2),(10,-2),(10,4),(8,4)])
    obstaculo.append(obs1)
    obstaculo.append(obs2)
    obstaculo.append(obs3)
    obstaculo.append(obs4)

    return obs_set, valid_box, obstaculo

#Preciso gerar amostras aleatórias para o meu grafo (PRM) 
def Rand_samples(obstaculo, valid_box):
    #N = 30
    #N = 250
    N = 500
    #N = 1200
    #N = 2000
    #N = 3000
    
    # Gerando amostras aleatóras
    samples = []
    for n in range(N):
        x = np.random.uniform(-16, 35)
        y = np.random.uniform(-8, 35)
        samples.append(Point([x, y]))
        
        # Verificando as que são inválidas    
        invalid_samples = []
        for s in samples:
            for o in obstaculo:
                if s.intersects(o):
                    invalid_samples.append(s)
                    
    #excluir amostras que invadam a área de approach
    for s in samples:
        for o in valid_box:
            if s.intersects(o):
                invalid_samples.append(s)
            
    # Salvando as amostras válidas em um vetor específico
    valid_samples = list(filter(lambda samples: samples not in invalid_samples, samples))
    
    return valid_samples

#função que calcula distância entre dois pontos
def dist(a, b):

        (x1, y1) = a
        (x2, y2) = b
            
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

#Criando Grafo de visibilidade
def Grafo(vertex_list,cluster_list,obs_set,obstaculo,valid_samples):
    
    G=nx.Graph()
    #adicionar os approuch_samples ao grafo 
    list_nodes=[] #[id,(node)]
    for target in vertex_list:
        q = target[0] #guarda o id
        r = target[1]
        s = target[2]
        G.add_node((r,s))
        list_nodes.append([q,])
    Nodes = list(G.nodes())
    #print(Nodes)
    
    #adicionar arestas entre os nos de clusters diferentes!
    set_ids =[]
    for node in Nodes: #pra cada nó percorro a lista de vértices identificando seu id,
    #e depois encontro na lista de cluster qual o id a qual pertence cada nó e 
    #crio uma nova lista só de set_id
        #print('node',node)
        for vertex in vertex_list:
            #print('vertex',vertex)
            if node == (vertex[1],vertex[2]):
                id_v = vertex[0]
                #print('id',id_v)
                for cluster in cluster_list:
                    list_id = cluster[2]
                    #print('list_id',list_id)
                    for no_id in list_id:
                        if id_v == no_id:
                                set_id = cluster[0]
                                set_ids.append(set_id)
    #print(set_ids)
    for i in range(0,(len(Nodes))):
        for j in range(0,(len(Nodes))):
           if set_ids[i]!=set_ids[j]:
                A = Nodes[i]
                a = A[0]
                b = A[1]
                C = Nodes[j]
                c = C[0]
                d = C[1]
                w = dist((a,b),(c,d))
                G.add_edge((a,b),(c,d),weight=w)

    #adicionar arestas entre os nodes e todas as valid samples
    for sample in valid_samples:
            node2 = (sample.x,sample.y)
            for node in Nodes:
                w = dist(node,node2)
                G.add_edge(node,node2,weight=w)
                
    #adicionar arestas entre as amostras aleatórias válidas
    node_p = []  #guardo as coordenadas das amostras válidas em uma lista
    for sample in valid_samples:
        node_sample = (sample.x,sample.y)
        node_p.append(node_sample)
        
    for i in range(len(node_p)):
        for j in range(len(node_p)):
            if i != j:
                w = dist(node_p[i],node_p[j])
                G.add_edge(node_p[i],node_p[j], weight=w)
   
    #verificar se a aresta intercepta os bound box
    all_edges = list(G.edges)
    for ed in all_edges:
        nod1 = ed[0]
        nod2 = ed[1]
        line = LineString([nod1, nod2])
        for o in obs_set:
            if line.intersects(o):
                if ([nod1,nod2]) in G.edges():
                    G.remove_edge(nod1,nod2)
        for o in obstaculo:
            if line.intersects(o):
                if ([nod1,nod2]) in G.edges():
                    G.remove_edge(nod1,nod2)

    return G

# testando a plotagem de outra forma (FUNCIONOU!!!!!)
def Plot_nods(vertex_list, central_coords_cluster_list, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23, p24, p25, p26, p27, p28, p29, p30, p31, p32, p33,G):

    fig = plt.figure(figsize=(8, 5), dpi=100)
    ax = fig.add_subplot(111, aspect='equal')

    for vertex in vertex_list:
        ax.scatter(vertex[1], vertex[2])
    p1.draw(ax)
    p2.draw(ax)
    p3.draw(ax)
    p4.draw(ax)
    p5.draw(ax)
    p6.draw(ax)
    p7.draw(ax)
    p8.draw(ax)
    p9.draw(ax)
    p10.draw(ax)
    p11.draw(ax)
    p12.draw(ax)
    p13.draw(ax)
    p14.draw(ax)
    p15.draw(ax)
    p16.draw(ax)
    p17.draw(ax)
    p18.draw(ax)
    p19.draw(ax)
    p20.draw(ax)
    p21.draw(ax)
    p22.draw(ax)
    p23.draw(ax)
    p24.draw(ax)
    p25.draw(ax)
    p26.draw(ax)
    p27.draw(ax)
    p28.draw(ax)
    p29.draw(ax)
    p30.draw(ax)
    p31.draw(ax)
    p32.draw(ax)
    p33.draw(ax)

    for coords in central_coords_cluster_list:
        xc = coords[1]
        yc = coords[2]
        rc = coords[3]
        # P_Space
        pspace = Circle((xc, yc), radius=(rc + 1.10),
                        fill=False, ls='--', color='b')
        ax.add_patch(pspace)
        # R_Space
        # calculo do R-space
        R = rc + 2.20  # 1.10 + 1.20 #R= r + sd
        Rspace = Circle((xc, yc), radius=R, fill=False, ls='--', color='g')
        ax.add_patch(Rspace)

    obs_set, valid_box, obstaculo = Bound_box(central_coords_cluster_list)
    for obs in obstaculo:
        ax.add_patch(PolygonPatch(obs, facecolor='black', edgecolor='black'))
    #valid_samples = Rand_samples(obstaculo, valid_box)
    #for v in valid_samples:
        #ax.plot(*v.xy, 'r*')
    
    labels = nx.get_edge_attributes(G,'weight')   
    pos = {node:(node[0], node[1]) for node in G.nodes()}   
    #nx.draw_networkx_edge_labels(G,pos,edge_labels=labels) 
    nx.draw(G, pos, font_size=3, with_labels=False, node_size=50, node_color="g", ax=ax)

    ax.tick_params(labelsize=12)
    ax.grid(False)
    ax.set_xlim([-10, 25])
    ax.set_ylim([-10, 30])
    plt.axis('equal')


# PLOTANDO O RESULTADO INICIAL OBTIDO PELO SOLUCIONADOR (FROM LUCIAN0)
def plot_tour(tour_nodes_id, vertex_list, central_coords_cluster_list, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23, p24, p25, p26, p27, p28, p29, p30, p31, p32, p33, G):

    fig = plt.figure(figsize=(8, 5), dpi=100)
    ax = fig.add_subplot(111, aspect='equal')

    # plot_nodes:
    for vertex in vertex_list:
        ax.scatter(vertex[1], vertex[2])
    p1.draw(ax)
    p2.draw(ax)
    p3.draw(ax)
    p4.draw(ax)
    p5.draw(ax)
    p6.draw(ax)
    p7.draw(ax)
    p8.draw(ax)
    p9.draw(ax)
    p10.draw(ax)
    p11.draw(ax)
    p12.draw(ax)
    p13.draw(ax)
    p14.draw(ax)
    p15.draw(ax)
    p16.draw(ax)
    p17.draw(ax)
    p18.draw(ax)
    p19.draw(ax)
    p20.draw(ax)
    p21.draw(ax)
    p22.draw(ax)
    p23.draw(ax)
    p24.draw(ax)
    p25.draw(ax)
    p26.draw(ax)
    p27.draw(ax)
    p28.draw(ax)
    p29.draw(ax)
    p30.draw(ax)
    p31.draw(ax)
    p32.draw(ax)
    p33.draw(ax)

    for coords in central_coords_cluster_list:
        xc = coords[1]
        yc = coords[2]
        rc = coords[3]
        # P_Space
        pspace = Circle((xc, yc), radius=(rc + 1.10),
                        fill=False, ls='--', color='b')
        #ax.add_patch(pspace)
        # R_Space
        # calculo do R-space
        R = rc + 2.20  # 1.10 + 1.20 #R= r + sd
        Rspace = Circle((xc, yc), radius=R, fill=False, ls='--', color='g')
        #ax.add_patch(Rspace)
        
        obs_set, valid_box, obstaculo = Bound_box(central_coords_cluster_list)
        for obs in obstaculo:
            ax.add_patch(PolygonPatch(obs, facecolor='black', edgecolor='black'))
    #print(G.nodes())
    # plota o tour social encontrado
    new_path = []
    result = []
    comprimento=0
    for id in tour_nodes_id:
        par = vertex_list[id]
        result.append(par)
    #print(result)
    for i in range(1,len(result)):
        a =result[i-1][1]
        b = result[i-1][2]
        start_node = (a,b)
        c = result[i][1]
        d = result[i][2]
        end_node = (c,d)
        
        #print('s_nod',start_node)
        #print('end',end_node)

        #Calcula o menor caminho entre cada node do resultado
        path_menor = nx.shortest_path(G, start_node, end_node,weight='weight')
        new_path.append(path_menor)
        length = nx.shortest_path_length(G, source=start_node, target=end_node, weight='weight')
        comprimento = comprimento + length    
    print('caminho social:',new_path)        
    print('comprimento do caminho:',comprimento)
    
    #extraindo a lista de edges do new_path 
    edgelist = []
    for path in new_path:
        for i in range(1,len(path)):
            a = path[i-1]
            b = path[i]
            ed = (a,b)
            edgelist.append(ed)
            
    #extraindo a lista de nós do new path
    nodelist = []
    for path in new_path:
        for i in range(len(path)):
           nodelist.append(path[i])

    
    pos = {node:(node[0], node[1]) for node in G.nodes()}
    nx.draw_networkx_nodes(G, pos, nodelist=nodelist, node_size=100, node_color='b')
    nx.draw_networkx_edges(G, pos, edgelist=edgelist, ax=ax, nodelist=nodelist, edge_color='g')

    ax.tick_params(labelsize=12)
    ax.grid(False)
    ax.set_xlim([-10, 25])
    ax.set_ylim([-10, 30])
    plt.axis('equal')


####################################### Testes #######################################################
def main():

    (p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23, p24, p25, p26, p27, p28, p29, p30, p31, p32, p33,
     xc1, xc2, xc3, xc4, xc5, xc6, xc7, xc8, xc9, xc10, xc11, xc12, xc13, xc14, yc1, yc2, yc3, yc4, yc5, yc6, yc7, yc8, yc9, yc10, yc11, yc12, yc13, yc14, rc1, rc2, rc3, rc4,
     rc5, rc6, rc7, rc8, rc9, rc10, rc11, rc12, rc13, rc14, samples1, samples2, samples3, samples4, samples5, samples6, samples7, samples8, samples9, samples10, samples11, samples12, samples13, samples14) = Create_clusters()

    #DrawCena(p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23, p24, p25, p26, p27, p28, p29, p30,p31,p32,p33,
     #        xc1, xc2, xc3, xc4, xc5, xc6, xc7, xc8, xc9, xc10, xc11, xc12, xc13, xc14, yc1, yc2, yc3, yc4, yc5, yc6, yc7, yc8, yc9, yc10, yc11, yc12, yc13, yc14, rc1, rc2, rc3, rc4,
      #       rc5, rc6, rc7, rc8, rc9, rc10, rc11, rc12, rc13, rc14, samples1, samples2, samples3, samples4, samples5, samples6, samples7, samples8, samples9,samples10, samples11, samples12, samples13, samples14)

    vertex_list, cluster_list, central_coords_cluster_list = Instances(samples1, samples2, samples3, samples4, samples5, samples6, samples7, samples8, samples9, samples10, samples11, samples12, samples13,samples14,
                                                                       xc1, xc2, xc3, xc4, xc5, xc6, xc7, xc8, xc9, xc10, xc11, xc12, xc13, xc14,yc1, yc2, yc3, yc4, yc5, yc6, yc7, yc8, yc9, yc10, yc11, yc12, yc13,yc14,
                                                                       rc1, rc2, rc3, rc4, rc5, rc6, rc7, rc8, rc9, rc10, rc11, rc12, rc13,rc14)

    obs_set, valid_box, obstaculo = Bound_box(central_coords_cluster_list)
    valid_samples = Rand_samples(obstaculo, valid_box)
    G = Grafo(vertex_list,cluster_list,obs_set,obstaculo,valid_samples)
    #print((G.edges()))
    #print('vertex_list:[vertex_id,xv,yv]', vertex_list)
    #print('cluster_list:[set_id,set_profit,id_vertex_list]', cluster_list)
    #print('central_coords_cluster_list:(set_id,xc,yc,rc)',
         #central_coords_cluster_list)

    #Plot_nods(vertex_list, central_coords_cluster_list, p1, p2, p3, p4, p5, p6, p7, p8, p9,
     #         p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23, p24, p25, p26, p27, p28, p29, p30,p31,p32,p33,G)
    
    # valores obtidos pelo solver VNS -> Luciano
    tour_nodes_id = [0,12,55,46,26,7,29,23,16,47,38,60,31,34,64,0] # tMax:200
    tour_clusters_id = [0,3,13,11,6,2,7,5,4,12,10,14,8,915,1]
    tour_clusters_rews= [0,2,1,5,2,2,2,2,2,4,1,3,3,3,0]
    
    #Inicialmente a ideia é pegar o resultado do VNS e aplicar o PRM para tornar o tour socialmente aceitável
    

    #plot_tour(tour_nodes_id, vertex_list, central_coords_cluster_list, p1, p2, p3, p4, p5, p6, p7, p8,
             # p9, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23, p24, p25, p26, p27, p28, p29, p30,p31,p32,p33,G)

    tour_nodes_id1 = [0,12,46,29,7,26,32,34,64,0]
    #tour_clusters_id1 = [0,3,11,7,2,6,8,9,15,1]
    #tour_clusters_rews = [0,2,5,2,2,2,3,3,3,0]
    
    #plot_tour(tour_nodes_id1, vertex_list, central_coords_cluster_list, p1, p2, p3, p4, p5, p6, p7, p8,
              #p9, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23, p24, p25, p26, p27, p28, p29, p30,p31,p32,p33,G)
     
    # aleatório apenas para gerar imagem
    tour_nodes_id2 = [0,12,46,26,7,29,23,16,38,60,31,34,64,0] # tMax:200
    tour_clusters_id = [0,3,11,6,2,7,5,4,10,14,8,915,1]
    #tour_clusters_rews= [0,2,1,5,2,2,2,2,2,4,1,3,3,3,0]
    plot_tour(tour_nodes_id2, vertex_list, central_coords_cluster_list, p1, p2, p3, p4, p5, p6, p7, p8,
              p9, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23, p24, p25, p26, p27, p28, p29, p30,p31,p32,p33,G)