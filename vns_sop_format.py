#from subprocess import call

import f_formation_ver4_1 as f

vertex_list, cluster_list, central_coords_cluster_list = f.main()

#print("vértices ", vertex_list)
#print("\nCluster ", cluster_list)
#print("\nCentro ", central_coords_cluster_list)
dimensao = len(vertex_list)
tmax = 1500
start_set = 0
end_set = 1
sets = len(cluster_list)
radius = 0

arq = open("problema1.sop", "w+")

linhasParaOArquivo = ["NAME: problema1", "TYPE: TSP", "COMMENT: with 21 locations, OPN dataset , start is first set, goal is second", f"DIMENSION: {dimensao}", f"TMAX: {tmax}", f"START_SET: {start_set}", f"END_SET: {end_set}", f"SETS: {sets}", f"NEIGHBORHOOD_RADIUS: {radius}", "EDGE_WEIGHT_TYPE: CEIL_2D"]
for linha in linhasParaOArquivo:
    arq.write(linha)
    arq.write("\n")


arq.write("NODE_COORD_SECTION")
arq.write("\n")
for vertice in vertex_list:
    ''' vertex_id, x_vertice, y_vertice '''
    l = str(vertice[0]) + ' ' + ' '.join(map(lambda x: "{0:.2f}".format(x), vertice[1:]))
    #l = ' '.join(map(str, vertice))
    arq.write(l)
    arq.write("\n")



arq.write("GTSP_SET_SECTION: set_id set_profit id-vertex-list")
arq.write("\n")
for c in cluster_list:
    l = str(c).replace(']', '').replace('[', '').replace(',', '')
    arq.write(l)
    arq.write("\n")



arq.write("GTSP_SET_CENTER_COORD_SECTION: set_id x y")
arq.write("\n")
for centro in central_coords_cluster_list:
    '''  '''
    l = str(centro[0]) + ' ' + ' '.join(map(lambda x: "{0:.2f}".format(x), centro[1:]))
    #l = ' '.join(map(str, vertice))
    arq.write(l)
    arq.write("\n")
 
arq.close() 

