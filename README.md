# F-formation
Cluster respresentation based in F-formation theory

F-formationver0 - versão pré inicial da representação

F-formationver1 - versão inicial com algumas F-formation Face to face e função Cluster para criar um dicionário com os grupos e atribuir os rewards

F-formationver2 :
versão com 5 casos de F-formation (Face-to-Face (horizontal,vertical e inclinada), L-shaped, Side-by-side;
Rewards atribuídos no momento em que as coordenadas de cada target são definidas.
Não usa mais a função Cluster.

F-formationver3:
Função Create_clusters() retorna um dicionário da forma {cluster0:[xt1,yt1,thc1,rw1],[xt2,yt2,thc2,rw2],...[xtn,ytn,thcn,rwn].
Onde: x,y são as coordenadas do approach point, thc é a orientação em relação ao centro do O-space, rw é o reward daquele approach point.


F-formationver4: 
A função Create_clusters não retorna um dicionário, mas sim todas as pessoas e samples na cena (não está nada elegante, ainda pretendo melhorar)

criei a representação de novos f-formations com grupos maiores que 2 pessoas

função Instance retorna as listas necessárias para o solucionador do SOP: [no_id,x,y],[set_id,set_profit,id_vertice_list],[set_id,xc,yc,rc]

Código muito manual, nada elegante mas funcional!!! (no futuro próximo pretendo melhorar as funções e a classe F-formation para tornar o código mais elegante e compacto)


F_formationver4.1:
Usando função Plot_nods pra plotar a cena com todos as f-formations
